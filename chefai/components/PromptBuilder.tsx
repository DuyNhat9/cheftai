import React, { useMemo, useState } from 'react';

type AgentType = 'General' | 'Architect' | 'UI_UX_Dev' | 'Backend_AI_Dev' | 'Testing_QA';

type DetailLevel = 'concise' | 'balanced' | 'deep';

interface ConstraintOption {
  id: string;
  label: string;
}

const constraintOptions: ConstraintOption[] = [
  { id: 'step_by_step', label: 'Giải thích từng bước' },
  { id: 'code_first', label: 'Ưu tiên code mẫu rõ ràng' },
  { id: 'no_fluff', label: 'Không nói lan man, đi thẳng vào vấn đề' },
  { id: 'ask_before_assuming', label: 'Hỏi lại nếu thông tin chưa đủ rõ' },
  { id: 'respect_existing_code', label: 'Hạn chế phá vỡ kiến trúc/code hiện tại' },
];

const languageOptions = [
  { id: 'vi', label: 'Tiếng Việt' },
  { id: 'en', label: 'English' },
  { id: 'mixed', label: 'Linh hoạt (Việt + Anh nếu cần)' },
];

const taskTypeOptions = [
  'Giải thích code',
  'Sửa bug',
  'Tối ưu hiệu năng',
  'Viết mới tính năng',
  'Thiết kế API / kiến trúc',
  'Viết test / QA',
  'Viết tài liệu / README',
  'Khác',
];

const PromptBuilder: React.FC = () => {
  const [agent, setAgent] = useState<AgentType>('General');
  const [taskType, setTaskType] = useState<string>('Giải thích code');
  const [language, setLanguage] = useState<'vi' | 'en' | 'mixed'>('vi');
  const [detailLevel, setDetailLevel] = useState<DetailLevel>('balanced');
  const [constraints, setConstraints] = useState<string[]>(['ask_before_assuming']);
  const [context, setContext] = useState<string>('');
  const [expectedOutput, setExpectedOutput] = useState<string>('');
  const [extraNotes, setExtraNotes] = useState<string>('');
  const [copied, setCopied] = useState(false);

  const toggleConstraint = (id: string) => {
    setConstraints(prev =>
      prev.includes(id) ? prev.filter(c => c !== id) : [...prev, id],
    );
  };

  const generatedPrompt = useMemo(() => {
    const lines: string[] = [];

    // Agent / role
    if (agent !== 'General') {
      lines.push(
        `Bạn đang đóng vai trò **${agent}** trong project CheftAi. Hãy suy nghĩ như một senior ${agent}.`,
      );
    } else {
      lines.push(
        'Bạn là một AI trợ lý code cấp senior, đang giúp tôi trong project CheftAi chạy trong Cursor IDE.',
      );
    }

    // Language
    if (language === 'vi') {
      lines.push('Hãy luôn trả lời bằng **tiếng Việt tự nhiên, dễ hiểu**.');
    } else if (language === 'en') {
      lines.push('Please answer in **clear, natural English**.');
    } else {
      lines.push(
        'Trả lời chính bằng **tiếng Việt**, nhưng có thể dùng thuật ngữ/đoạn tiếng Anh khi cần chính xác.',
      );
    }

    // Task type
    lines.push('');
    lines.push(`**Mục tiêu chính:** ${taskType}.`);

    // Context
    if (context.trim()) {
      lines.push('');
      lines.push('**Bối cảnh / ngữ cảnh hiện tại:**');
      lines.push(context.trim());
    } else {
      lines.push('');
      lines.push(
        '_(Tôi sẽ bổ sung thêm bối cảnh: file, đoạn code, stack trace… vào ngay dưới prompt này khi sử dụng.)_',
      );
    }

    // Expected output
    if (expectedOutput.trim()) {
      lines.push('');
      lines.push('**Kết quả mà tôi mong muốn:**');
      lines.push(expectedOutput.trim());
    }

    // Detail level
    lines.push('');
    if (detailLevel === 'concise') {
      lines.push(
        '- Mức độ chi tiết: **Ngắn gọn** — tập trung vào ý chính, code mẫu, và các bước hành động rõ ràng.',
      );
    } else if (detailLevel === 'balanced') {
      lines.push(
        '- Mức độ chi tiết: **Vừa đủ** — giải thích nhanh lý do, sau đó đưa ra các bước/code cụ thể.',
      );
    } else {
      lines.push(
        '- Mức độ chi tiết: **Sâu** — phân tích kỹ vấn đề, nêu trade-off, rồi đề xuất giải pháp/các bước cụ thể.',
      );
    }

    // Constraints
    if (constraints.length > 0) {
      lines.push('');
      lines.push('**Ràng buộc / phong cách trả lời:**');
      constraintOptions.forEach(opt => {
        if (constraints.includes(opt.id)) {
          lines.push(`- ${opt.label}`);
        }
      });
    }

    // Extra notes
    if (extraNotes.trim()) {
      lines.push('');
      lines.push('**Ghi chú thêm:**');
      lines.push(extraNotes.trim());
    }

    lines.push('');
    lines.push(
      'Nếu thấy thông tin chưa đủ để trả lời chính xác, hãy hỏi lại tối đa 2–3 câu trước khi đưa ra giải pháp.',
    );

    return lines.join('\n');
  }, [agent, language, taskType, context, expectedOutput, detailLevel, constraints, extraNotes]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(generatedPrompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-slate-950 text-slate-50 flex justify-center px-4 py-6">
      <div className="w-full max-w-6xl grid gap-6 md:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
        {/* Left side: form */}
        <section className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 md:p-6 shadow-xl shadow-slate-950/40 backdrop-blur">
          <div className="flex items-center justify-between gap-3 mb-6">
            <div>
              <h1 className="text-xl md:text-2xl font-semibold tracking-tight">
                Cursor Prompt Helper cho CheftAi
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Chọn mục tiêu, agent, style trả lời… để sinh prompt chuẩn, copy dán thẳng vào Cursor.
              </p>
            </div>
          </div>

          <div className="space-y-5">
            {/* Agent & language */}
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                  Agent / vai trò
                </label>
                <select
                  value={agent}
                  onChange={e => setAgent(e.target.value as AgentType)}
                  className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-500/70 focus:border-emerald-500/60 transition"
                >
                  <option value="General">General (trợ lý code chung)</option>
                  <option value="Architect">Architect</option>
                  <option value="UI_UX_Dev">UI_UX_Dev</option>
                  <option value="Backend_AI_Dev">Backend_AI_Dev</option>
                  <option value="Testing_QA">Testing_QA</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                  Ngôn ngữ trả lời
                </label>
                <div className="flex gap-2">
                  {languageOptions.map(opt => (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => setLanguage(opt.id as 'vi' | 'en' | 'mixed')}
                      className={`flex-1 rounded-lg border px-3 py-2 text-xs font-medium transition ${
                        language === opt.id
                          ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-sm shadow-emerald-500/40'
                          : 'bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-500'
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Task type */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                Loại nhiệm vụ
              </label>
              <select
                value={taskType}
                onChange={e => setTaskType(e.target.value)}
                className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-500/70 focus:border-emerald-500/60 transition"
              >
                {taskTypeOptions.map(option => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>

            {/* Context & expected output */}
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                  Bối cảnh / ngữ cảnh
                </label>
                <textarea
                  value={context}
                  onChange={e => setContext(e.target.value)}
                  rows={6}
                  placeholder="Ví dụ: Mình đang làm việc trong project CheftAi. File chính đang chỉnh là ..., gặp lỗi ..., stack trace/miêu tả như sau..."
                  className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-500/70 focus:border-emerald-500/60 transition resize-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                  Kết quả mong muốn
                </label>
                <textarea
                  value={expectedOutput}
                  onChange={e => setExpectedOutput(e.target.value)}
                  rows={6}
                  placeholder="Ví dụ: Muốn có snippet code hoàn chỉnh, hoặc danh sách bước chi tiết để refactor, hoặc giải thích ngắn gọn 2–3 đoạn."
                  className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-500/70 focus:border-emerald-500/60 transition resize-none"
                />
              </div>
            </div>

            {/* Detail level */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                Mức độ chi tiết câu trả lời
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setDetailLevel('concise')}
                  className={`rounded-lg border px-3 py-2 text-xs text-left transition ${
                    detailLevel === 'concise'
                      ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-sm shadow-emerald-500/40'
                      : 'bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  <div className="font-semibold mb-0.5">Ngắn gọn</div>
                  <div className="text-[11px] text-slate-200/80">
                    Ưu tiên kết luận &amp; code, ít giải thích.
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setDetailLevel('balanced')}
                  className={`rounded-lg border px-3 py-2 text-xs text-left transition ${
                    detailLevel === 'balanced'
                      ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-sm shadow-emerald-500/40'
                      : 'bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  <div className="font-semibold mb-0.5">Vừa đủ</div>
                  <div className="text-[11px] text-slate-200/80">
                    Giải thích nhanh, sau đó đưa ra bước cụ thể.
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setDetailLevel('deep')}
                  className={`rounded-lg border px-3 py-2 text-xs text-left transition ${
                    detailLevel === 'deep'
                      ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-sm shadow-emerald-500/40'
                      : 'bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  <div className="font-semibold mb-0.5">Chi tiết</div>
                  <div className="text-[11px] text-slate-200/80">
                    Phân tích kỹ trade-off và đề xuất rõ ràng.
                  </div>
                </button>
              </div>
            </div>

            {/* Constraints */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                Ràng buộc / phong cách trả lời
              </label>
              <div className="flex flex-wrap gap-2">
                {constraintOptions.map(opt => {
                  const active = constraints.includes(opt.id);
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => toggleConstraint(opt.id)}
                      className={`inline-flex items-center gap-1 rounded-full border px-3 py-1.5 text-xs transition ${
                        active
                          ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-sm shadow-emerald-500/40'
                          : 'bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-500'
                      }`}
                    >
                      <span>{opt.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Extra notes */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wide text-slate-400 mb-2">
                Ghi chú thêm (optional)
              </label>
              <textarea
                value={extraNotes}
                onChange={e => setExtraNotes(e.target.value)}
                rows={3}
                placeholder="Ví dụ: Ưu tiên giải pháp ít đụng vào backend, hoặc không thay đổi schema DB, v.v."
                className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-emerald-500/70 focus:border-emerald-500/60 transition resize-none"
              />
            </div>
          </div>
        </section>

        {/* Right side: generated prompt */}
        <section className="flex flex-col gap-3">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 md:p-5 shadow-xl shadow-slate-950/40 backdrop-blur flex-1 flex flex-col min-h-[260px]">
            <div className="flex items-center justify-between gap-3 mb-3">
              <div>
                <h2 className="text-sm font-semibold tracking-tight">
                  Prompt đã sinh sẵn cho Cursor
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Copy đoạn dưới và dán thẳng vào Cursor chat (có thể thêm code/bối cảnh bên dưới).
                </p>
              </div>
              <button
                type="button"
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 rounded-full border border-emerald-400/70 bg-emerald-500 text-slate-950 px-3 py-1.5 text-xs font-semibold shadow-sm shadow-emerald-500/50 hover:bg-emerald-400 transition"
              >
                {copied ? '✅ Đã copy' : 'Copy prompt'}
              </button>
            </div>
            <div className="relative flex-1">
              <pre className="h-full max-h-[520px] overflow-auto text-xs leading-relaxed bg-slate-950/60 border border-slate-800 rounded-xl px-3.5 py-3 text-slate-100 whitespace-pre-wrap">
                {generatedPrompt}
              </pre>
              <div className="pointer-events-none absolute inset-x-0 bottom-0 h-10 bg-gradient-to-t from-slate-950/90 to-transparent rounded-b-xl" />
            </div>
          </div>

          <p className="text-[11px] text-slate-500">
            Gợi ý: Sau khi dán prompt vào Cursor, hãy gắn thêm đoạn code, file path hoặc stack trace ngay
            bên dưới để mình (AI) hiểu rõ bối cảnh và giúp bạn chính xác hơn.
          </p>
        </section>
      </div>
    </div>
  );
};

export default PromptBuilder;













