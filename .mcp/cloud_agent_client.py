#!/usr/bin/env python3
"""
cloud_agent_client.py

Client để giao tiếp với Cursor Cloud Agents API.
Fallback về local method nếu API không khả dụng.
"""

import json
import time
import requests
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Model mapping: Local model names → Cloud API model names
MODEL_MAPPING = {
    "Sonnet 4.5": "claude-4-sonnet",
    "GPT-5.1 Codex High Fast": "gpt-5.1-codex-high-fast",
    "claude-4.1-opus": "claude-4.1-opus",
    "o3 Pro": "o3-pro",
    "Sonnet 4 1M": "claude-4-sonnet-1m",
    "Gemini 3 Pro": "gemini-3-pro"
}


class CloudAgentClient:
    """Client để giao tiếp với Cursor Cloud Agents API"""
    
    def __init__(self, api_key: str, api_base: str = "https://api.cursor.com/v0"):
        self.api_key = api_key
        self.api_base = api_base
        self.headers = {
            'Authorization': f'Bearer {api_key}',  # Hoặc Basic Auth tùy API
            'Content-Type': 'application/json'
        }
        self.enabled = bool(api_key and api_key != "your_api_key_here")
    
    def _map_model(self, local_model: str) -> str:
        """Map local model name to Cloud API model name"""
        return MODEL_MAPPING.get(local_model, local_model.lower().replace(' ', '-'))
    
    def launch_agent(self, agent_name: str, model: str, prompt: str) -> Optional[str]:
        """
        Launch cloud agent với model và prompt cụ thể.
        Returns cloud_id nếu thành công, None nếu fail.
        """
        if not self.enabled:
            logger.debug(f"[cloud_agent] API disabled, skipping launch for {agent_name}")
            return None
        
        try:
            cloud_model = self._map_model(model)
            payload = {
                'model': cloud_model,
                'prompt': prompt,
                'agent_name': agent_name
            }
            
            url = f'{self.api_base}/agents'
            logger.info(f"[cloud_agent] Launching agent {agent_name} with model {cloud_model}")
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                cloud_id = result.get('id') or result.get('agent_id')
                logger.info(f"[cloud_agent] ✅ Launched cloud agent for {agent_name}: {cloud_id}")
                return cloud_id
            else:
                logger.warning(f"[cloud_agent] ⚠️ Launch failed for {agent_name}: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"[cloud_agent] ❌ Error launching agent {agent_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"[cloud_agent] ❌ Unexpected error: {e}")
            return None
    
    def send_followup(self, cloud_id: str, instruction: str) -> bool:
        """Send followup instruction to cloud agent"""
        if not self.enabled:
            return False
        
        try:
            payload = {'instruction': instruction}
            url = f'{self.api_base}/agents/{cloud_id}/followup'
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.info(f"[cloud_agent] ✅ Followup sent to {cloud_id}")
                return True
            else:
                logger.warning(f"[cloud_agent] ⚠️ Followup failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"[cloud_agent] ❌ Error sending followup: {e}")
            return False
    
    def poll_conversation(self, cloud_id: str, max_attempts: int = 60, interval: int = 10) -> Optional[Dict[str, Any]]:
        """
        Poll conversation status until complete.
        Returns conversation data if completed, None if timeout or error.
        """
        if not self.enabled:
            return None
        
        url = f'{self.api_base}/agents/{cloud_id}/conversation'
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    conv = response.json()
                    status = conv.get('status') or conv.get('state')
                    
                    # Check if completed (adjust based on actual API response format)
                    if status in ['completed', 'done', 'finished']:
                        logger.info(f"[cloud_agent] ✅ Conversation {cloud_id} completed")
                        return conv
                    elif status in ['failed', 'error']:
                        logger.warning(f"[cloud_agent] ⚠️ Conversation {cloud_id} failed")
                        return conv
                    else:
                        logger.debug(f"[cloud_agent] Polling {cloud_id}: status={status} (attempt {attempt+1}/{max_attempts})")
                        
                else:
                    logger.warning(f"[cloud_agent] ⚠️ Poll failed: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"[cloud_agent] ❌ Error polling: {e}")
            
            if attempt < max_attempts - 1:
                time.sleep(interval)
        
        logger.warning(f"[cloud_agent] ⚠️ Poll timeout for {cloud_id} after {max_attempts} attempts")
        return None


def load_config() -> Dict[str, Any]:
    """Load config from .mcp/config.json"""
    config_path = Path(__file__).parent / 'config.json'
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[cloud_agent] Failed to load config: {e}")
    
    # Return default config
    return {
        "cursor_cloud_api": {
            "enabled": False,
            "api_key": "",
            "api_base": "https://api.cursor.com/v0",
            "poll_interval": 10,
            "max_poll_attempts": 60
        },
        "local_fallback": {
            "enabled": True
        }
    }



