import { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Play, Send, CheckCircle2, XCircle, Loader2, Bot, Code2, Terminal, Clock, BookOpen, Lightbulb, ShieldAlert, Sparkles } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { executionApi } from '../services/execution';
import type { ExecutionResult, ExecutionSubmitResponse } from '../services/execution';
import { learningApi } from '../services/learning';
import { useTutorWebSocket } from '../features/auth/useTutorWebSocket';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { CoachMarkdown } from '../components/ui/CoachMarkdown';
import { PostSubmissionModal } from '../components/ui/PostSubmissionModal';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { useTheme } from '../features/theme/ThemeContext';
import { cn } from '../lib/utils';

export function ProblemWorkspacePage() {
  const { problemId } = useParams<{ problemId: string }>();
  const navigate = useNavigate();
  const { resolvedTheme } = useTheme();
  
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
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProblem() {
      if (!problemId || problemId === 'null' || problemId === 'undefined') {
        setLoadError('Invalid problem ID or no exercise selected.');
        setIsLoading(false);
        return;
      }
      try {
        const data = await learningApi.getExerciseById(problemId);
        setProblem(data);
        if (data.starter_code) {
          setCode(data.starter_code);
        }
      } catch (err: any) {
        console.error('Failed to load problem:', err);
        setLoadError(err.message || 'Could not load problem.');
      } finally {
        setIsLoading(false);
      }
    }
    loadProblem();
  }, [problemId]);

  const handleRun = async () => {
    if (!problem) return;
    setIsExecuting(true);
    setRightTab('tests');
    setMobileTab('right');
    try {
      let parsedCases = [];
      if (problem.test_cases_json) {
        try {
          parsedCases = typeof problem.test_cases_json === 'string'
            ? JSON.parse(problem.test_cases_json)
            : problem.test_cases_json;
        } catch (e) {
          console.error("Failed to parse test_cases_json", e);
        }
      }

      if (!parsedCases || parsedCases.length === 0) {
        parsedCases = [
          { input_data: { nums: [2, 7, 11, 15], target: 9 }, expected_output: [0, 1] }
        ];
      }

      const response = await executionApi.run({
        code,
        language: 'python',
        test_cases: parsedCases,
        entrypoint: problem.entrypoint || 'twoSum'
      });
      setExecutionResult(response.execution);
    } catch (err: any) {
      console.error(err);
      setExecutionResult({
        success: false,
        error: err.message || 'Execution failed due to a network or server error.',
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
    if (!problem) return;
    setIsExecuting(true);
    setRightTab('tests');
    setMobileTab('right');
    try {
      const response = await executionApi.submit({
        exercise_id: problemId || '',
        code,
        language: 'python',
        entrypoint: problem.entrypoint || 'twoSum'
      });
      setExecutionResult(response.execution);
      
      if (response.status === 'accepted') {
        setSubmissionResult(response);
      }
      
    } catch (err: any) {
      console.error(err);
      setExecutionResult({
        success: false,
        error: err.message || 'Submission failed due to a network or server error.',
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
    setMobileTab('right');
    requestReview(code, executionResult, problem.difficulty, problem.concept_name);
  };

  // Mobile Tabs State
  const [mobileTab, setMobileTab] = useState<'problem' | 'editor' | 'right'>('editor');

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4 text-text-secondary">
          <Loader2 className="w-8 h-8 animate-spin text-accent" />
          <p className="font-medium text-sm">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (loadError || !problem) {
    return (
      <div className="h-screen flex flex-col bg-background font-sans text-text-primary">
        <header className="h-14 bg-surface border-b border-border flex items-center justify-between px-4 shrink-0">
          <Button variant="ghost" size="icon" onClick={() => navigate('/problems')} className="text-text-secondary hover:text-text-primary rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <span className="font-bold text-sm text-text-primary">Problem Workspace</span>
          <ThemeToggle size="sm" />
        </header>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-surface border border-border p-8 rounded-2xl text-center space-y-4 shadow-sm animate-in fade-in zoom-in-95 duration-200">
            <div className="w-12 h-12 bg-warning-subtle text-warning rounded-xl flex items-center justify-center mx-auto border border-warning/20">
              <BookOpen className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-text-primary tracking-tight">Problem Not Found</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              {loadError || "The requested problem could not be found or has not been unlocked yet."}
            </p>
            <div className="pt-2 flex flex-col sm:flex-row gap-3">
              <Button variant="outline" className="flex-1" onClick={() => navigate('/')}>
                Dashboard
              </Button>
              <Button variant="primary" className="flex-1 shadow-xs" onClick={() => navigate('/problems')}>
                Browse Problems
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden font-sans text-text-primary min-w-0">
      {/* Top Workspace Header */}
      <header className="h-14 bg-surface border-b border-border flex items-center justify-between px-2 sm:px-4 shrink-0 z-20 transition-colors w-full min-w-0">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => navigate('/problems')}
            className="text-text-secondary hover:text-text-primary rounded-lg shrink-0 w-8 h-8 sm:w-9 sm:h-9"
            aria-label="Back to problems"
          >
            <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
          </Button>
          
          <div className="flex items-center gap-2 min-w-0">
            <h1 className="font-bold text-text-primary text-xs sm:text-sm md:text-base truncate max-w-[140px] sm:max-w-xs md:max-w-md">
              {problem.title}
            </h1>
            <Badge 
              variant="outline" 
              className={cn(
                "hidden sm:inline-flex text-[11px] font-semibold capitalize shrink-0",
                problem.difficulty === 'easy' ? "text-emerald-600 dark:text-emerald-400 border-emerald-500/30 bg-emerald-500/10" :
                problem.difficulty === 'medium' ? "text-amber-600 dark:text-amber-400 border-amber-500/30 bg-amber-500/10" :
                "text-rose-600 dark:text-rose-400 border-rose-500/30 bg-rose-500/10"
              )}
            >
              {problem.difficulty || 'Easy'}
            </Badge>
          </div>
        </div>
        
        {/* Right Actions */}
        <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
          <ThemeToggle size="sm" />

          <Button 
            variant="outline" 
            onClick={handleAskCoach}
            className="bg-accent-subtle text-accent border-accent/20 hover:bg-accent/15 gap-1.5 font-semibold hidden md:flex h-8 sm:h-9 text-xs"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Ask AI Coach</span>
          </Button>
          
          <div className="w-px h-4 bg-border mx-0.5 hidden sm:block"></div>
          
          <Button 
            variant="secondary" 
            onClick={handleRun}
            disabled={isExecuting}
            className="gap-1.5 font-semibold px-2.5 sm:px-3.5 h-8 sm:h-9 text-xs"
          >
            {isExecuting && rightTab === 'tests' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            <span className="hidden xs:inline">Run</span>
          </Button>
          
          <Button 
            variant="primary" 
            onClick={handleSubmit}
            disabled={isExecuting}
            className="gap-1.5 font-semibold px-3 sm:px-4 h-8 sm:h-9 text-xs shadow-xs"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Submit</span>
          </Button>
        </div>
      </header>

      {/* Mobile / Tablet Tabs Switcher (<1024px) */}
      <div className="lg:hidden flex border-b border-border bg-surface shrink-0 min-w-0">
        {[
          { id: 'problem', label: 'Problem' },
          { id: 'editor', label: 'Code' },
          { id: 'right', label: 'Tests & AI' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setMobileTab(tab.id as any)}
            className={cn(
              "flex-1 py-2.5 text-xs sm:text-sm font-semibold border-b-2 transition-colors cursor-pointer text-center",
              mobileTab === tab.id
                ? "border-accent text-accent bg-accent-subtle/30"
                : "border-transparent text-text-secondary hover:text-text-primary"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 3-Pane Workspace Desktop (Reflows into active mobile/tablet tab) */}
      <div className="flex-1 flex overflow-hidden min-w-0 w-full">
        
        {/* Left Pane: Problem Description */}
        <div className={cn(
          "w-full lg:w-1/4 lg:min-w-[280px] lg:max-w-sm flex-col border-r border-border bg-surface relative z-0 min-w-0",
          mobileTab === 'problem' ? "flex" : "hidden lg:flex"
        )}>
          <div className="h-11 border-b border-border hidden lg:flex items-center px-4 shrink-0 bg-surface-muted/30">
            <BookOpen className="w-4 h-4 text-text-secondary mr-2" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-text-muted">Problem Description</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4 sm:p-5 custom-scrollbar min-w-0">
            <div className="text-text-secondary leading-relaxed text-xs sm:text-sm whitespace-pre-wrap">
              {problem.instructions}
            </div>
          </div>
        </div>

        {/* Center Pane: Monaco Code Editor */}
        <div className={cn(
          "flex-1 flex-col min-w-0 bg-background relative z-0 overflow-hidden",
          mobileTab === 'editor' ? "flex" : "hidden lg:flex"
        )}>
          <div className="h-11 border-b border-border bg-surface flex items-center px-4 shrink-0 justify-between">
            <div className="flex items-center gap-2">
              <Code2 className="w-4 h-4 text-text-secondary" />
              <span className="text-xs sm:text-sm font-semibold text-text-primary">solution.py</span>
            </div>
            <div className="flex items-center gap-2">
               <Badge variant="outline" className="text-[11px] font-mono">Python 3</Badge>
            </div>
          </div>
          
          <div className="flex-1 relative min-w-0 w-full overflow-hidden">
            <Editor
              height="100%"
              defaultLanguage="python"
              theme={resolvedTheme === 'dark' ? 'vs-dark' : 'vs'}
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
                lineHeight: 1.6,
                padding: { top: 12, bottom: 12 },
                scrollBeyondLastLine: false,
                smoothScrolling: true,
                cursorBlinking: "smooth",
                cursorSmoothCaretAnimation: "on",
                formatOnPaste: true,
                roundedSelection: true,
                wordWrap: "on"
              }}
            />
          </div>
        </div>

        {/* Right Pane: Tests / Coach */}
        <div className={cn(
          "w-full lg:w-[32%] lg:min-w-[300px] lg:max-w-md flex-col border-l border-border bg-surface relative z-0 min-w-0",
          mobileTab === 'right' ? "flex" : "hidden lg:flex"
        )}>
          {/* Tests vs Coach Tab Header */}
          <div className="flex border-b border-border h-11 shrink-0 bg-surface px-2">
            {[
              { id: 'tests', label: 'Test Results', icon: Terminal },
              { id: 'coach', label: 'AI Coach', icon: Bot }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setRightTab(tab.id as any)}
                className={cn(
                  "flex items-center gap-1.5 px-3 sm:px-4 h-full text-xs sm:text-sm font-semibold border-b-2 transition-all relative cursor-pointer",
                  rightTab === tab.id 
                    ? "border-accent text-accent" 
                    : "border-transparent text-text-secondary hover:text-text-primary hover:bg-surface-hover"
                )}
              >
                <tab.icon className={cn("w-3.5 h-3.5", rightTab === tab.id ? "text-accent" : "text-text-muted")} />
                <span>{tab.label}</span>
                {tab.id === 'coach' && wsStatus === 'connected' && (
                  <span className="w-1.5 h-1.5 bg-success rounded-full ring-2 ring-surface ml-1"></span>
                )}
              </button>
            ))}
          </div>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar flex flex-col min-w-0">
            
            {/* AI Coach Tab */}
            {rightTab === 'coach' && (
              <div className="flex flex-col h-full bg-surface min-w-0">
                {/* Status Banner */}
                {wsStatus !== 'connected' && (
                   <div className="bg-warning-subtle text-warning text-xs font-medium px-3 py-1.5 border-b border-warning/20 flex items-center justify-center gap-2 shrink-0">
                     <Loader2 className="w-3.5 h-3.5 animate-spin" />
                     <span>{wsStatus === 'connecting' ? 'Connecting to AI Tutor...' : 'AI Tutor Disconnected'}</span>
                   </div>
                )}
                
                {/* Messages Viewport */}
                <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-4 min-w-0">
                  {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center px-4 py-8">
                      <div className="w-12 h-12 bg-accent-subtle text-accent rounded-full flex items-center justify-center mb-3 shadow-xs border border-accent/20">
                        <Bot className="w-6 h-6" />
                      </div>
                      <h3 className="text-text-primary font-bold text-sm mb-1">Your Personal AI Coach</h3>
                      <p className="text-text-secondary text-xs leading-relaxed max-w-xs">
                        Stuck on a problem? Ask the AI Coach to review your code and give Socratic hints without spoiling the answer.
                      </p>
                    </div>
                  ) : (
                    messages.map(msg => (
                      <div key={msg.id} className={cn(
                        "flex flex-col max-w-[95%]",
                        msg.sender === 'user' ? "ml-auto items-end" : "mr-auto items-start w-full"
                      )}>
                        <div className={cn(
                          "flex items-center gap-1.5 mb-1 px-1",
                          msg.sender === 'user' ? "flex-row-reverse" : "flex-row"
                        )}>
                          {msg.sender === 'ai' && (
                            <div className="w-5 h-5 rounded-full bg-accent text-white flex items-center justify-center shadow-xs">
                              <Bot className="w-3 h-3" />
                            </div>
                          )}
                          <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">
                            {msg.sender === 'user' ? 'You' : 'AI Coach'}
                          </span>
                        </div>
                        
                        <div className={cn(
                          "px-3.5 py-2.5 rounded-2xl text-xs sm:text-[13px] leading-relaxed shadow-xs min-w-0",
                          msg.sender === 'user' 
                            ? "bg-accent text-white rounded-tr-xs" 
                            : "bg-surface-muted border border-border text-text-primary rounded-tl-xs w-full"
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
                      <div className="flex items-center gap-1.5 mb-1 px-1 flex-row">
                        <div className="w-5 h-5 rounded-full bg-accent text-white flex items-center justify-center shadow-xs">
                          <Bot className="w-3 h-3" />
                        </div>
                        <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">
                          AI Coach
                        </span>
                      </div>
                      <div className="px-3.5 py-2.5 rounded-2xl text-xs leading-relaxed shadow-xs bg-surface-muted border border-border text-text-primary rounded-tl-xs flex items-center h-9">
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

                {/* Socratic Quick-Actions */}
                <div className="p-2.5 sm:p-3 border-t border-border bg-surface shrink-0 min-w-0">
                  <div className="text-[10px] font-bold text-text-muted uppercase tracking-wider mb-2 flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-accent" />
                    <span>Quick Inquiries</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    <button
                      onClick={() => askAction('socratic_guide', code, '💡 Give me a smaller hint', executionResult)}
                      disabled={isStreaming}
                      className="px-2 py-1 rounded-lg bg-surface-muted border border-border hover:border-amber-500/50 hover:bg-amber-500/10 text-text-secondary hover:text-amber-600 dark:hover:text-amber-300 text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer shadow-2xs"
                    >
                      <Lightbulb className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                      <span>Hint</span>
                    </button>
                    <button
                      onClick={() => askAction('code_auditor', code, '🛡️ Audit my edge cases', executionResult)}
                      disabled={isStreaming}
                      className="px-2 py-1 rounded-lg bg-surface-muted border border-border hover:border-emerald-500/50 hover:bg-emerald-500/10 text-text-secondary hover:text-emerald-600 dark:hover:text-emerald-300 text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer shadow-2xs"
                    >
                      <ShieldAlert className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                      <span>Edge Cases</span>
                    </button>
                    <button
                      onClick={() => askAction('complexity_analyst', code, '⏱️ Analyze time & space complexity', executionResult)}
                      disabled={isStreaming}
                      className="px-2 py-1 rounded-lg bg-surface-muted border border-border hover:border-cyan-500/50 hover:bg-cyan-500/10 text-text-secondary hover:text-cyan-600 dark:hover:text-cyan-300 text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50 cursor-pointer shadow-2xs"
                    >
                      <Clock className="w-3.5 h-3.5 text-cyan-500 shrink-0" />
                      <span>Complexity</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Test Results Tab */}
            {rightTab === 'tests' && (
              <div className="flex flex-col h-full bg-surface p-3 sm:p-4 min-w-0">
                {!executionResult && !isExecuting && (
                  <div className="h-full flex flex-col items-center justify-center text-center px-4 py-8">
                    <div className="w-12 h-12 bg-surface-muted rounded-full flex items-center justify-center mb-3">
                      <Terminal className="w-6 h-6 text-text-muted" />
                    </div>
                    <p className="text-text-secondary text-xs max-w-xs">
                      Run or submit your code to see compilation and test results here.
                    </p>
                  </div>
                )}
                
                {isExecuting && (
                  <div className="h-full flex flex-col items-center justify-center text-center py-10">
                    <Loader2 className="w-8 h-8 animate-spin text-accent mb-3" />
                    <p className="text-text-primary font-semibold text-sm">Executing code...</p>
                    <p className="text-text-secondary text-xs mt-1">Evaluating test cases</p>
                  </div>
                )}
                
                {executionResult && !isExecuting && (
                  <div className="space-y-4 min-w-0">
                    {/* Status Header */}
                    <div className={cn(
                      "p-3.5 rounded-xl border flex items-center gap-3",
                      executionResult.success 
                        ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-700 dark:text-emerald-300" 
                        : "bg-rose-500/10 border-rose-500/30 text-rose-700 dark:text-rose-300"
                    )}>
                      {executionResult.success ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                      ) : (
                        <XCircle className="w-5 h-5 text-rose-500 shrink-0" />
                      )}
                      <div>
                        <h4 className="font-bold text-sm">
                          {executionResult.success ? "All Tests Passed!" : "Tests Failed"}
                        </h4>
                        <p className="text-xs opacity-90">
                          {executionResult.test_results?.filter((t: any) => t.passed).length || 0} of {executionResult.test_results?.length || 0} test cases passed.
                        </p>
                      </div>
                    </div>

                    {/* Error Box if any */}
                    {executionResult.error && (
                      <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs font-mono text-rose-700 dark:text-rose-300 whitespace-pre-wrap overflow-x-auto">
                        {executionResult.error}
                      </div>
                    )}

                    {/* Standard Output if any */}
                    {executionResult.output && (
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Console Output</span>
                        <div className="p-3 bg-surface-muted border border-border rounded-xl text-xs font-mono text-text-secondary whitespace-pre-wrap overflow-x-auto">
                          {executionResult.output}
                        </div>
                      </div>
                    )}

                    {/* Test Cases List */}
                    {executionResult.test_results && executionResult.test_results.length > 0 && (
                      <div className="space-y-2">
                        <span className="text-[10px] font-bold text-text-muted uppercase tracking-wider">Test Cases</span>
                        <div className="space-y-2">
                          {executionResult.test_results.map((tr: any, idx: number) => (
                            <div key={idx} className="p-3 bg-surface-muted/60 border border-border rounded-xl space-y-1.5 text-xs">
                              <div className="flex items-center justify-between">
                                <span className="font-semibold text-text-primary">Test Case {idx + 1}</span>
                                <Badge variant="outline" className={cn(
                                  "text-[10px] font-semibold",
                                  tr.passed 
                                    ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30" 
                                    : "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30"
                                )}>
                                  {tr.passed ? "Passed" : "Failed"}
                                </Badge>
                              </div>
                              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-text-secondary pt-1">
                                <div>
                                  <span className="text-text-muted block text-[10px] uppercase">Input</span>
                                  <div className="bg-surface p-1.5 rounded border border-border/50 truncate">{JSON.stringify(tr.input_data)}</div>
                                </div>
                                <div>
                                  <span className="text-text-muted block text-[10px] uppercase">Expected</span>
                                  <div className="bg-surface p-1.5 rounded border border-border/50 truncate">{JSON.stringify(tr.expected_output)}</div>
                                </div>
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
