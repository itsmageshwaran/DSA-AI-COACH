import React from 'react';
import { Lightbulb, Target, Zap, Clock, Sparkles } from 'lucide-react';

interface CoachMarkdownProps {
  content: string;
}

export function CoachMarkdown({ content }: CoachMarkdownProps) {
  const trimmed = content.trim();

  if (!trimmed) {
    return <span className="text-text-muted italic">Thinking...</span>;
  }

  const lines = trimmed.split('\n');
  const renderedElements: React.ReactNode[] = [];
  let currentParagraph: string[] = [];

  const flushParagraph = (key: string) => {
    if (currentParagraph.length > 0) {
      const text = currentParagraph.join(' ').trim();
      if (text) {
        renderedElements.push(
          <p key={key} className="text-text-secondary leading-relaxed text-[13px] mb-2.5">
            {formatInlineText(text)}
          </p>
        );
      }
      currentParagraph = [];
    }
  };

  lines.forEach((line, idx) => {
    const trimmedLine = line.trim();

    if (!trimmedLine) {
      flushParagraph(`p-break-${idx}`);
      return;
    }

    // Filter out internal monologue preambles
    if (trimmedLine.match(/^(We need to|Let's think|Thinking process|I need to guide|Plan:|Here is my thought|As a socratic|We should not)/i)) {
      return;
    }

    // Observation / Insight card
    if (trimmedLine.match(/^[💡🔍]\s*(\*\*|__)?(Observation|Insight|Vulnerability|Current State)/i)) {
      flushParagraph(`before-obs-${idx}`);
      renderedElements.push(
        <div key={`card-obs-${idx}`} className="my-2.5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-text-primary">
          <div className="flex items-center gap-2 font-bold text-xs text-amber-400 mb-1">
            <Lightbulb className="w-3.5 h-3.5 shrink-0" />
            <span>OBSERVATION</span>
          </div>
          <div className="text-[13px] leading-relaxed text-amber-100/90 font-medium">
            {formatInlineText(cleanLeadingLabel(trimmedLine))}
          </div>
        </div>
      );
      return;
    }

    // Probing Question card
    if (trimmedLine.match(/^[🎯❓]\s*(\*\*|__)?(Key Question|Question|Next Step|To Consider)/i)) {
      flushParagraph(`before-q-${idx}`);
      renderedElements.push(
        <div key={`card-q-${idx}`} className="my-2.5 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/25 text-text-primary shadow-sm">
          <div className="flex items-center gap-2 font-bold text-xs text-cyan-400 mb-1">
            <Target className="w-3.5 h-3.5 shrink-0" />
            <span>PROBING QUESTION</span>
          </div>
          <div className="text-[13px] leading-relaxed text-cyan-100 font-semibold">
            {formatInlineText(cleanLeadingLabel(trimmedLine))}
          </div>
        </div>
      );
      return;
    }

    // Actionable Hint card
    if (trimmedLine.match(/^[⚡🚀💡🛡️]\s*(\*\*|__)?(Hint|Action|Edge Case|Tip|Recommendation)/i)) {
      flushParagraph(`before-h-${idx}`);
      renderedElements.push(
        <div key={`card-h-${idx}`} className="my-2.5 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-text-primary">
          <div className="flex items-center gap-2 font-bold text-xs text-emerald-400 mb-1">
            <Zap className="w-3.5 h-3.5 shrink-0" />
            <span>ACTIONABLE HINT</span>
          </div>
          <div className="text-[13px] leading-relaxed text-emerald-100/90 font-medium">
            {formatInlineText(cleanLeadingLabel(trimmedLine))}
          </div>
        </div>
      );
      return;
    }

    // Complexity cards
    if (trimmedLine.match(/^[⏱️💾🚀]\s*(\*\*|__)?(Time Complexity|Space Complexity|Target Optimal)/i)) {
      flushParagraph(`before-comp-${idx}`);
      const isTime = trimmedLine.toLowerCase().includes('time');
      renderedElements.push(
        <div key={`card-comp-${idx}`} className="my-1.5 p-2.5 rounded-lg bg-surface border border-border/80 flex items-start gap-2.5">
          {isTime ? <Clock className="w-4 h-4 text-primary mt-0.5 shrink-0" /> : <Sparkles className="w-4 h-4 text-accent mt-0.5 shrink-0" />}
          <div className="text-[12.5px] leading-relaxed">
            {formatInlineText(trimmedLine)}
          </div>
        </div>
      );
      return;
    }

    // List items
    if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ') || trimmedLine.match(/^\d+\.\s/)) {
      flushParagraph(`before-list-${idx}`);
      const listContent = trimmedLine.replace(/^([-*]|\d+\.)\s+/, '');
      renderedElements.push(
        <div key={`list-${idx}`} className="flex items-start gap-2 my-1 pl-1">
          <span className="w-1.5 h-1.5 rounded-full bg-accent mt-2 shrink-0"></span>
          <span className="text-text-secondary text-[13px] leading-relaxed font-normal">
            {formatInlineText(listContent)}
          </span>
        </div>
      );
      return;
    }

    currentParagraph.push(trimmedLine);
  });

  flushParagraph('final-flush');

  return (
    <div className="space-y-1 text-text-primary text-[13px] leading-relaxed">
      {renderedElements}
    </div>
  );
}

function cleanLeadingLabel(line: string): string {
  return line.replace(/^[💡🎯⚡🚀🔍🛡️⏱️💾❓]\s*(\*\*|__)?[A-Za-z\s/]+(\*\*|__)?:\s*/i, '').trim() || line;
}

function formatInlineText(text: string): React.ReactNode {
  const tokens = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);

  return tokens.map((token, index) => {
    if (token.startsWith('**') && token.endsWith('**')) {
      return (
        <strong key={index} className="font-semibold text-text-primary">
          {token.slice(2, -2)}
        </strong>
      );
    }
    if (token.startsWith('`') && token.endsWith('`')) {
      return (
        <code key={index} className="px-1.5 py-0.5 rounded bg-surface border border-border/80 text-primary font-mono text-[12px] font-medium mx-0.5">
          {token.slice(1, -1)}
        </code>
      );
    }
    return token;
  });
}
