import { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Play, Send, CheckCircle2, XCircle, Loader2, Bot, Code2, Terminal, AlertCircle, Clock, BookOpen, Lightbulb, ShieldAlert, Sparkles } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { executionApi } from '../services/execution';
import type { ExecutionResult } from '../services/execution';
import { learningApi } from '../services/learning';
import { useTutorWebSocket } from '../features/auth/useTutorWebSocket';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { CoachMarkdown } from '../components/ui/CoachMarkdown';
import { PostSubmissionModal } from '../components/ui/PostSubmissionModal';
import type { ExecutionSubmitResponse } from '../services/execution';
import { cn } from '../lib/utils';

export function ProblemWorkspacePage() {
  const { problemId } = useParams();
  const navigate = useNavigate();
  const [rightTab, setRightTab] = useState<'tests' | 'coach'>('tests');
  const [code, setCode] = useState('def binary_search(arr, target):\n    # Write your implementation here\n    pass');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);

  const { messages, status: wsStatus, requestReview, askAction, isStreaming } = useTutorWebSocket(problemId || 'unknown');
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (rightTab === 'coach') {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, rightTab]);

  const [problem, setProblem] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadProblem() {
      if (!problemId) return;
      try {
        const data = await learningApi.getExerciseById(problemId);
        setProblem(data);
        if (data.starter_code) {
          setCode(data.starter_code);
        }
      } catch (err) {
        console.error('Failed to load problem:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadProblem();
  }, [problemId]);

  const handleRun = async () => {
    setIsExecuting(true);
    setRightTab('tests');
    try {
      const response = await executionApi.run({
        code,
        language: 'python',
        test_cases: [
          { input_data: { nums: [-1, 0, 3, 5, 9, 12], target: 9 }, expected_output: 4 },
          { input_data: { nums: [-1, 0, 3, 5, 9, 12], target: 2 }, expected_output: -1 }
        ],
        entrypoint: 'binary_search'
      });
      setExecutionResult(response.execution);
    } catch (err) {
      console.error(err);
      setExecutionResult({
        success: false,
        error: 'Execution failed due to a network or server error.',
        execution_time_ms: 0,
        memory_used_kb: 0,
        test_results: []
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const [submissionResult, setSubmissionResult] = useState<ExecutionSubmitResponse | null>(null);

  const handleSubmit = async () => {
    setIsExecuting(true);
    setRightTab('tests');
    try {
      const response = await executionApi.submit({
        exercise_id: problemId || '',
        code,
        language: 'python',
        entrypoint: 'binary_search' // we might want to get this dynamically later
      });
      setExecutionResult(response.execution);
      
      if (response.status === 'accepted') {
        setSubmissionResult(response);
      }
      
    } catch (err) {
      console.error(err);
      setExecutionResult({
        success: false,
        error: 'Submission failed due to a network or server error.',
        execution_time_ms: 0,
        memory_used_kb: 0,
        test_results: []
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleAskCoach = () => {
    if (!problem || !code) return;
    setRightTab('coach');
    requestReview(code, executionResult, problem.difficulty, problem.concept_name);
  };

  // Mobile Tabs State
  const [mobileTab, setMobileTab] = useState<'problem' | 'editor' | 'right'>('editor');

  if (isLoading || !problem) {
    return (
      <div className="h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4 text-text-secondary">
          <Loader2 className="w-8 h-8 animate-spin text-accent" />
          <p className="font-medium">Loading workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden font-sans">
      {/* Header */}
      <header className="h-14 bg-surface border-b border-border flex items-center justify-between px-2 sm:px-4 shrink-0 z-10">
        <div className="flex items-center gap-2 sm:gap-4">
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => navigate('/problems')}
            className="text-text-secondary rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-3">
            <h1 className="font-bold text-text-primary text-sm sm:text-base line-clamp-1">{problem.title}</h1>
            <Badge variant="outline" className={cn(
              "hidden lg:inline-flex font-semibold text-xs capitalize",
              problem.difficulty === 'easy' ? "text-emerald-400 border-emerald-500/30 bg-emerald-500/10" :
              problem.difficulty === 'medium' ? "text-amber-400 border-amber-500/30 bg-amber-500/10" :
              "text-rose-400 border-rose-500/30 bg-rose-500/10"
            )}>
              {problem.difficulty || 'Easy'}
            </Badge>
          </div>
        </div>
        
        <div className="flex items-center gap-1 sm:gap-2">
          <Button 
            variant="outline"
            onClick={handleAskCoach}
            className="bg-ai-light text-ai border-transparent hover:bg-ai/10 gap-2 font-semibold hidden sm:flex"
          >
            <Bot className="w-4 h-4" />
            <span className="hidden lg:inline">Ask AI Coach</span>
          </Button>
          
          <div className="w-px h-6 bg-border mx-1 sm:mx-2 hidden sm:block"></div>
          
          <Button 
            variant="secondary"
            onClick={handleRun}
            disabled={isExecuting}
            className="gap-2 font-semibold px-2 sm:px-4"
          >
            {isExecuting && rightTab === 'tests' ? <Loader2 className="w-4 h-4 animate-spin text-text-secondary" /> : <Play className="w-4 h-4 text-text-secondary" />}
            <span className="hidden sm:inline">Run</span>
          </Button>
          
          <Button 
            variant="primary"
            onClick={handleSubmit}
            disabled={isExecuting}
            className="gap-2 font-semibold px-2 sm:px-4"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Submit</span>
          </Button>
        </div>
      </header>

      {/* Mobile Tabs */}
      <div className="lg:hidden flex border-b border-border bg-surface shrink-0">
        {[
          { id: 'problem', label: 'Problem' },
          { id: 'editor', label: 'Code' },
          { id: 'right', label: 'Tests & AI' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setMobileTab(tab.id as any)}
            className={cn(
              "flex-1 py-3 text-sm font-semibold border-b-2 transition-colors",
              mobileTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-text-secondary"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 3-Pane Workspace */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Pane: Problem Description (25%) */}
        <div className={cn(
          "w-full lg:w-1/4 lg:min-w-[300px] flex-col border-r border-border bg-surface relative z-0",
          mobileTab === 'problem' ? "flex" : "hidden lg:flex"
        )}>
          <div className="h-12 border-b border-border hidden lg:flex items-center px-4 shrink-0 bg-surface/50 backdrop-blur-sm">
            <BookOpen className="w-4 h-4 text-text-secondary mr-2" />
            <h2 className="text-sm font-bold text-text-primary">Problem Description</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-5 custom-scrollbar">
            <div className="prose prose-invert prose-sm max-w-none text-text-secondary leading-relaxed whitespace-pre-wrap">
              {problem.instructions}
            </div>
          </div>
        </div>

        {/* Center Pane: Code Editor (Flex) */}
        <div className={cn(
          "flex-1 flex-col min-w-0 lg:min-w-[400px] bg-background relative z-0",
          mobileTab === 'editor' ? "flex" : "hidden lg:flex"
        )}>
          <div className="h-12 border-b border-border bg-surface/80 backdrop-blur-sm flex items-center px-4 shrink-0 justify-between">
            <div className="flex items-center gap-2">
              <Code2 className="w-4 h-4 text-text-secondary" />
              <span className="text-sm font-semibold text-text-primary">solution.py</span>
            </div>
            <div className="flex items-center gap-2">
               <Badge variant="outline" className="text-xs font-mono">Python 3</Badge>
            </div>
          </div>
          
          <div className="flex-1 relative">
            <Editor
              height="100%"
              defaultLanguage="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
                lineHeight: 1.6,
                padding: { top: 16, bottom: 16 },
                scrollBeyondLastLine: false,
                smoothScrolling: true,
                cursorBlinking: "smooth",
                cursorSmoothCaretAnimation: "on",
                formatOnPaste: true,
                roundedSelection: true,
              }}
            />
          </div>
        </div>

        {/* Right Pane: Tests / Coach (30%) */}
        <div className={cn(
          "w-full lg:w-[30%] lg:min-w-[320px] flex-col border-l border-border bg-surface relative z-0",
          mobileTab === 'right' ? "flex" : "hidden lg:flex"
        )}>
          <div className="flex border-b border-border h-12 shrink-0 bg-surface/50 backdrop-blur-sm px-2">
            {[
              { id: 'tests', label: 'Test Results', icon: Terminal },
              { id: 'coach', label: 'AI Coach', icon: Bot }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setRightTab(tab.id as any)}
                className={cn(
                  "flex items-center gap-2 px-4 h-full text-sm font-semibold border-b-2 transition-all relative",
                  rightTab === tab.id 
                    ? "border-primary text-primary" 
                    : "border-transparent text-text-secondary hover:text-text-primary hover:bg-surface-hover"
                )}
              >
                <tab.icon className={cn("w-4 h-4", rightTab === tab.id ? "text-primary" : "text-text-muted")} />
                {tab.label}
                {tab.id === 'coach' && wsStatus === 'connected' && (
                  <span className="absolute top-3 right-2 w-2 h-2 bg-success rounded-full ring-2 ring-surface"></span>
                )}
              </button>
            ))}
          </div>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar flex flex-col">
            
            {/* AI Coach Tab */}
            {rightTab === 'coach' && (
              <div className="flex flex-col h-full bg-surface">
                {/* Status Banner */}
                {wsStatus !== 'connected' && (
                   <div className="bg-warning-subtle text-warning text-xs font-medium px-4 py-2 border-b border-warning/20 flex items-center justify-center gap-2">
                     <Loader2 className="w-3.5 h-3.5 animate-spin" />
                     {wsStatus === 'connecting' ? 'Connecting to AI Tutor...' : 'Disconnected from AI Tutor.'}
                   </div>
                )}
                
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center px-6">
                      <div className="w-16 h-16 bg-ai-light rounded-full flex items-center justify-center mb-4 shadow-sm border border-ai/10">
                        <Bot className="w-8 h-8 text-ai" />
                      </div>
                      <h3 className="text-text-primary font-bold text-lg mb-1">Your Personal AI Coach</h3>
                      <p className="text-text-secondary text-sm leading-relaxed">
                        Stuck on a problem? Ask the AI Coach to review your code and give Socratic hints without giving away the answer.
                      </p>
                    </div>
                  ) : (
                    messages.map(msg => (
                      <div key={msg.id} className={cn(
                        "flex flex-col max-w-[95%]",
                        msg.sender === 'user' ? "ml-auto items-end" : "mr-auto items-start w-full"
                      )}>
                        <div className={cn(
                          "flex items-center gap-2 mb-1.5 px-1",
                          msg.sender === 'user' ? "flex-row-reverse" : "flex-row"
                        )}>
                          {msg.sender === 'ai' && (
                            <div className="w-6 h-6 rounded-full bg-ai flex items-center justify-center shadow-sm">
                              <Bot className="w-3.5 h-3.5 text-white" />
                            </div>
                          )}
                          <span className="text-[11px] font-bold text-text-muted uppercase tracking-wider">
                            {msg.sender === 'user' ? 'You' : 'AI Coach'}
                          </span>
                        </div>
                        
                        <div className={cn(
                          "px-4 py-3 rounded-2xl text-[13px] leading-relaxed shadow-sm",
                          msg.sender === 'user' 
                            ? "bg-primary text-text-inverse rounded-tr-sm" 
                            : "bg-surface-muted border border-border text-text-primary rounded-tl-sm w-full"
                        )}>
                          {msg.sender === 'user' ? (
                            <div className="whitespace-pre-wrap">{msg.text}</div>
                          ) : (
                            <CoachMarkdown content={msg.text} />
                          )}
                        </div>
                      </div>
                    ))
                  )}
                  {isStreaming && messages.length > 0 && messages[messages.length - 1].sender === 'user' && (
                    <div className="mr-auto items-start flex flex-col max-w-[90%]">
                      <div className="flex items-center gap-2 mb-1.5 px-1 flex-row">
                        <div className="w-6 h-6 rounded-full bg-ai flex items-center justify-center shadow-sm">
                          <Bot className="w-3.5 h-3.5 text-white" />
                        </div>
                        <span className="text-[11px] font-bold text-text-muted uppercase tracking-wider">
                          AI Coach
                        </span>
                      </div>
                      <div className="px-4 py-3 rounded-2xl text-[13px] leading-relaxed shadow-sm bg-surface-muted border border-border text-text-primary rounded-tl-sm flex items-center h-10">
                        <div className="flex space-x-1 items-center opacity-60">
                          <div className="w-1.5 h-1.5 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-1.5 h-1.5 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-1.5 h-1.5 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Interactive Socratic Quick-Actions */}
                <div className="p-3 border-t border-border bg-surface/80 backdrop-blur-sm shrink-0">
                  <div className="text-[11px] font-bold text-text-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-accent" />
                    <span>Quick Inquiries</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    <button
                      onClick={() => askAction('socratic_guide', code, '💡 Give me a smaller hint', executionResult)}
                      disabled={isStreaming}
                      className="px-2.5 py-1.5 rounded-lg bg-surface border border-border hover:border-amber-500/40 hover:bg-amber-500/10 text-text-secondary hover:text-amber-300 text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer shadow-2xs"
                    >
                      <Lightbulb className="w-3.5 h-3.5 text-amber-400" />
                      <span>Smaller Hint</span>
                    </button>
                    <button
                      onClick={() => askAction('code_auditor', code, '🛡️ Audit my edge cases', executionResult)}
                      disabled={isStreaming}
                      className="px-2.5 py-1.5 rounded-lg bg-surface border border-border hover:border-emerald-500/40 hover:bg-emerald-500/10 text-text-secondary hover:text-emerald-300 text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer shadow-2xs"
                    >
                      <ShieldAlert className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Edge Cases</span>
                    </button>
                    <button
                      onClick={() => askAction('complexity_analyst', code, '⏱️ Analyze time & space complexity', executionResult)}
                      disabled={isStreaming}
                      className="px-2.5 py-1.5 rounded-lg bg-surface border border-border hover:border-cyan-500/40 hover:bg-cyan-500/10 text-text-secondary hover:text-cyan-300 text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer shadow-2xs"
                    >
                      <Clock className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Complexity</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Test Results Tab */}
            {rightTab === 'tests' && (
              <div className="flex flex-col h-full bg-surface p-4">
                {!executionResult && !isExecuting && (
                  <div className="h-full flex flex-col items-center justify-center text-center px-6">
                    <div className="w-16 h-16 bg-surface-muted rounded-full flex items-center justify-center mb-4">
                      <Terminal className="w-8 h-8 text-text-muted" />
                    </div>
                    <p className="text-text-secondary text-sm">
                      Run or submit your code to see compilation and test results here.
                    </p>
                  </div>
                )}
                
                {isExecuting && (
                  <div className="h-full flex flex-col items-center justify-center text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-accent mb-4" />
                    <p className="text-text-primary font-semibold text-sm">Executing code...</p>
                    <p className="text-text-secondary text-xs mt-1">Running against test cases</p>
                  </div>
                )}
                
                {executionResult && !isExecuting && (
                  <div className="space-y-6">
                    {/* Overall status */}
                    <div className={cn(
                      "p-5 rounded-xl border flex flex-col gap-3",
                      executionResult.success ? "bg-success-subtle border-success/20" : "bg-error-subtle border-error/20"
                    )}>
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                          executionResult.success ? "bg-success/20 text-success" : "bg-error/20 text-error"
                        )}>
                          {executionResult.success ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                        </div>
                        <h3 className={cn(
                          "font-bold text-lg",
                          executionResult.success ? "text-success" : "text-error"
                        )}>
                          {executionResult.success ? "Accepted" : "Wrong Answer / Error"}
                        </h3>
                      </div>
                      <div className="flex gap-4 text-xs font-semibold text-text-secondary bg-background/50 p-2 rounded-md border border-border/50">
                        <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {executionResult.execution_time_ms} ms</span>
                        <span className="flex items-center gap-1"><Terminal className="w-3.5 h-3.5" /> {executionResult.memory_used_kb} KB</span>
                      </div>
                    </div>
                    
                    {/* Output / Errors */}
                    {executionResult.error && (
                      <div className="bg-background border border-error/30 rounded-lg overflow-hidden shadow-sm">
                        <div className="bg-error-subtle px-3 py-2 border-b border-error/20 flex items-center gap-2">
                          <AlertCircle className="w-4 h-4 text-error" />
                          <h4 className="text-xs font-bold text-error uppercase tracking-wide">Error Output</h4>
                        </div>
                        <pre className="p-4 text-error text-[13px] font-mono whitespace-pre-wrap overflow-x-auto">{executionResult.error}</pre>
                      </div>
                    )}
                    
                    {executionResult.output && (
                      <div className="bg-background border border-border rounded-lg overflow-hidden shadow-sm">
                        <div className="bg-surface-muted px-3 py-2 border-b border-border">
                          <h4 className="text-xs font-bold text-text-secondary uppercase tracking-wide">Standard Output</h4>
                        </div>
                        <pre className="p-4 text-text-primary text-[13px] font-mono whitespace-pre-wrap overflow-x-auto">{executionResult.output}</pre>
                      </div>
                    )}

                    {/* Test Cases */}
                    {executionResult.test_results && executionResult.test_results.length > 0 && (
                      <div className="space-y-3">
                        <h4 className="text-sm font-bold text-text-primary flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-success" />
                          Test Cases ({executionResult.test_results.filter(t => t.passed).length}/{executionResult.test_results.length})
                        </h4>
                        <div className="space-y-3">
                          {executionResult.test_results.map((tr, idx) => (
                            <div key={idx} className={cn(
                              "bg-background border rounded-lg overflow-hidden shadow-sm transition-colors",
                              tr.passed ? "border-border hover:border-success/50" : "border-error/30"
                            )}>
                              <div className={cn(
                                "p-3 flex items-center gap-3 border-b",
                                tr.passed ? "bg-surface-muted/50 border-border" : "bg-error-subtle border-error/20"
                              )}>
                                {tr.passed ? (
                                  <CheckCircle2 className="w-4 h-4 text-success" />
                                ) : (
                                  <XCircle className="w-4 h-4 text-error" />
                                )}
                                <span className="text-sm font-bold text-text-primary">Case {idx + 1}</span>
                              </div>
                              <div className="p-4 space-y-4 font-mono text-[13px]">
                                <div>
                                  <span className="text-text-muted text-[11px] uppercase font-bold tracking-wider block mb-1.5">Input</span>
                                  <div className="bg-surface p-2.5 rounded-md border border-border text-text-primary">{JSON.stringify(tr.input_data)}</div>
                                </div>
                                <div>
                                  <span className="text-text-muted text-[11px] uppercase font-bold tracking-wider block mb-1.5">Expected Output</span>
                                  <div className="bg-surface p-2.5 rounded-md border border-border text-text-primary">{JSON.stringify(tr.expected)}</div>
                                </div>
                                {!tr.passed && (
                                  <div>
                                    <span className="text-error text-[11px] uppercase font-bold tracking-wider block mb-1.5">Actual Output</span>
                                    <div className="bg-error-subtle border border-error/30 p-2.5 rounded-md text-error font-semibold">{JSON.stringify(tr.actual)}</div>
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {submissionResult && (
        <PostSubmissionModal 
          submissionResult={submissionResult} 
          onClose={() => setSubmissionResult(null)} 
        />
      )}
    </div>
  );
}
