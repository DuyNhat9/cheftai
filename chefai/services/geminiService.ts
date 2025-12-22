import { GoogleGenAI, Type, Schema } from "@google/genai";
import { Recipe } from "../types";

const apiKey = process.env.API_KEY || '';

// Define the response schema strictly
const recipeSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    title: { type: Type.STRING, description: "The name of the dish." },
    description: { type: Type.STRING, description: "A tempting short description." },
    cookTime: { type: Type.STRING, description: "Total cooking time (e.g., '30 mins')." },
    difficulty: { type: Type.STRING, enum: ["Easy", "Medium", "Hard"] },
    calories: { type: Type.NUMBER, description: "Approximate calories per serving." },
    ingredients: {
      type: Type.ARRAY,
      items: { type: Type.STRING },
      description: "List of ingredients with measurements."
    },
    instructions: {
      type: Type.ARRAY,
      items: { type: Type.STRING },
      description: "Step-by-step cooking instructions."
    }
  },
  required: ["title", "description", "cookTime", "difficulty", "calories", "ingredients", "instructions"]
};

export const generateRecipe = async (ingredients: string[]): Promise<Recipe> => {
  if (!apiKey) {
    throw new Error("API Key is missing. Please set REACT_APP_GEMINI_API_KEY.");
  }

  const ai = new GoogleGenAI({ apiKey });

  const prompt = `
    I have the following ingredients in my fridge: ${ingredients.join(", ")}.
    
    Please create a delicious, creative, and practical recipe using some or all of these ingredients. 
    You may assume I have basic pantry staples like salt, pepper, oil, and water.
    
    The recipe should be formatted perfectly for a cooking app.
  `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: recipeSchema,
        systemInstruction: "You are a world-class chef assistant. You create mouth-watering, easy-to-follow recipes based on limited ingredients.",
        temperature: 0.7,
      },
    });

    const text = response.text;
    if (!text) {
        throw new Error("No response from AI");
    }

    return JSON.parse(text) as Recipe;
  } catch (error) {
    console.error("Error generating recipe:", error);
    throw error;
  }
};