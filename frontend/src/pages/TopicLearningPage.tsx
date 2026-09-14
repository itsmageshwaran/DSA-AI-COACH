import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  BookOpen,
  PlayCircle,
  Code2,
  CheckCircle2,
  Circle,
  ArrowRight,
  Clock,
  Zap,
  Sparkles,
  ChevronRight,
  Award,
  Layers,
  Copy,
  Check,
  ExternalLink,
  HelpCircle,
  BarChart3
} from 'lucide-react';
import { learningApi, type TopicLearningResponse } from '../services/learning';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { cn } from '../lib/utils';

type TabType = 'learn' | 'understand' | 'practice' | 'master';

export const TopicLearningPage: React.FC = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<TabType>('learn');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [topicData, setTopicData] = useState<TopicLearningResponse | null>(null);
  const [selectedLang, setSelectedLang] = useState<string>('python');
  const [copiedCode, setCopiedCode] = useState(false);

  useEffect(() => {
    const fetchTopic = async () => {
      if (!topicId) return;
      setLoading(true);
      setError(null);
      try {
        const data = await learningApi.getTopicLearningData(topicId);
        setTopicData(data);
        if (data.preferred_language && data.code_snippets[data.preferred_language]) {
          setSelectedLang(data.preferred_language);
        } else if (Object.keys(data.code_snippets).length > 0) {
          setSelectedLang(Object.keys(data.code_snippets)[0]);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load topic learning module');
      } finally {
        setLoading(false);
      }
    };
    fetchTopic();
  }, [topicId]);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 font-sans">
        <div className="w-10 h-10 border-4 border-accent border-t-transparent rounded-full animate-spin"></div>
        <p className="text-text-secondary text-sm font-medium">Assembling curriculum, code patterns, and live problems...</p>
      </div>
    );
  }

  if (error || !topicData) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-8 bg-surface border border-border rounded-2xl text-center shadow-xs font-sans">
        <HelpCircle className="w-14 h-14 text-error mx-auto mb-4" />
        <h2 className="text-xl font-bold text-text-primary mb-2">Topic Module Unavailable</h2>
        <p className="text-text-secondary text-sm mb-6">{error || 'Could not load curriculum data for this concept.'}</p>
        <Button onClick={() => navigate('/roadmap')} variant="primary">
          Return to Learning Roadmap
        </Button>
      </div>
    );
  }

  const { stats, video, complexity, notes, code_snippets, practice_problems } = topicData;

  return (
    <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8 pb-24 font-sans text-text-primary antialiased min-w-0 animate-fade-in">
      {/* Accessible Breadcrumb Navigation */}
      <nav aria-label="Breadcrumb" className="flex items-center space-x-2 text-xs sm:text-sm text-text-muted">
        <Link to="/" className="hover:text-text-primary transition-colors">Home</Link>
        <ChevronRight className="w-3.5 h-3.5" />
        <Link to="/learn" className="hover:text-text-primary transition-colors">Roadmap</Link>
        <ChevronRight className="w-3.5 h-3.5" />
        <span className="text-accent font-semibold">{topicData.name}</span>
      </nav>

      {/* Header Hero Banner with Adaptive Design Tokens */}
      <div className="relative overflow-hidden bg-surface border border-border rounded-2xl sm:rounded-3xl p-6 sm:p-8 shadow-xs">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline" className="bg-accent-subtle text-accent border-accent/20 text-xs font-semibold gap-1.5 py-1">
                <Layers className="w-3.5 h-3.5" /> Core Data Structure
              </Badge>
              <Badge variant="outline" className="bg-success-subtle text-success border-success/20 text-xs font-semibold gap-1.5 py-1">
                <Clock className="w-3.5 h-3.5" /> {topicData.estimated_minutes} mins estimated
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-text-primary">
              {topicData.name}
            </h1>
            <p className="text-sm sm:text-base text-text-secondary leading-relaxed">
              {topicData.tagline}
            </p>
            {topicData.prerequisites && topicData.prerequisites.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 text-xs text-text-secondary pt-1">
                <span className="font-semibold text-text-muted uppercase tracking-wider">Prerequisites:</span>
                {topicData.prerequisites.map((p, i) => (
                  <span key={i} className="bg-surface-muted px-2.5 py-1 rounded-md border border-border text-text-secondary font-medium">
                    {p}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Mastery Circular Badge Card */}
          <div className="flex flex-col items-center justify-center p-5 bg-surface-elevated border border-border rounded-2xl min-w-[200px] text-center shadow-xs">
            <div className="flex items-center gap-1.5 mb-1">
              <BarChart3 className="w-4 h-4 text-accent" />
              <span className="text-xs font-bold uppercase tracking-wider text-text-muted">Mastery Level</span>
            </div>
            <div className="text-3xl sm:text-4xl font-black text-accent my-1">
              {stats.mastery_percentage}%
            </div>
            <div className="w-full bg-surface-muted h-2.5 rounded-full overflow-hidden my-2 border border-border/60">
              <div
                className="bg-accent h-full rounded-full transition-all duration-700"
                style={{ width: `${stats.mastery_percentage}%` }}
              />
            </div>
            <span className="text-xs text-text-secondary font-medium">
              {stats.solved_problems} of {stats.total_problems} problems solved
            </span>
          </div>
        </div>
      </div>

      {/* 4-Step Interactive Learning Tab Navigation */}
      <div className="border-b border-border flex overflow-x-auto space-x-2 pb-px scrollbar-none">
        <button
          onClick={() => setActiveTab('learn')}
          className={cn(
            "flex items-center gap-2 py-3 px-4 sm:px-5 border-b-2 font-medium text-xs sm:text-sm transition-all whitespace-nowrap cursor-pointer",
            activeTab === 'learn'
              ? "border-accent text-accent font-semibold bg-accent-subtle/50 rounded-t-xl"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border-hover"
          )}
        >
          <PlayCircle className="w-4 h-4" />
          <span>1. Learn</span>
          <span className="text-[11px] bg-surface-muted px-2 py-0.5 rounded-full text-text-muted font-medium">Video Intuition</span>
        </button>

        <button
          onClick={() => setActiveTab('understand')}
          className={cn(
            "flex items-center gap-2 py-3 px-4 sm:px-5 border-b-2 font-medium text-xs sm:text-sm transition-all whitespace-nowrap cursor-pointer",
            activeTab === 'understand'
              ? "border-accent text-accent font-semibold bg-accent-subtle/50 rounded-t-xl"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border-hover"
          )}
        >
          <BookOpen className="w-4 h-4" />
          <span>2. Understand</span>
          <span className="text-[11px] bg-surface-muted px-2 py-0.5 rounded-full text-text-muted font-medium">Notes & Code</span>
        </button>

        <button
          onClick={() => setActiveTab('practice')}
          className={cn(
            "flex items-center gap-2 py-3 px-4 sm:px-5 border-b-2 font-medium text-xs sm:text-sm transition-all whitespace-nowrap cursor-pointer",
            activeTab === 'practice'
              ? "border-accent text-accent font-semibold bg-accent-subtle/50 rounded-t-xl"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border-hover"
          )}
        >
          <Code2 className="w-4 h-4" />
          <span>3. Practice</span>
          <span className="text-[11px] bg-accent-subtle text-accent px-2 py-0.5 rounded-full font-bold">
            {practice_problems.length} Problems
          </span>
        </button>

        <button
          onClick={() => setActiveTab('master')}
          className={cn(
            "flex items-center gap-2 py-3 px-4 sm:px-5 border-b-2 font-medium text-xs sm:text-sm transition-all whitespace-nowrap cursor-pointer",
            activeTab === 'master'
              ? "border-accent text-accent font-semibold bg-accent-subtle/50 rounded-t-xl"
              : "border-transparent text-text-secondary hover:text-text-primary hover:border-border-hover"
          )}
        >
          <Award className="w-4 h-4" />
          <span>4. Master</span>
          <span className="text-[11px] bg-surface-muted px-2 py-0.5 rounded-full text-text-muted font-medium">Milestones</span>
        </button>
      </div>

      {/* TAB CONTENT 1: LEARN (VIDEO INTUITION) */}
      {activeTab === 'learn' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
          <div className="lg:col-span-2 space-y-6">
            <Card className="overflow-hidden shadow-xs">
              <div className="p-4 bg-surface-muted border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <PlayCircle className="w-5 h-5 text-accent" />
                  <h3 className="font-bold text-sm sm:text-base text-text-primary">{video.title || `${topicData.name} Overview`}</h3>
                </div>
                <Badge variant="outline" className="text-xs font-mono text-text-muted">
                  {video.duration || '15 mins'}
                </Badge>
              </div>
              <div className="relative aspect-video w-full bg-black">
                {video.embed_url ? (
                  <iframe
                    src={video.embed_url}
                    title={video.title}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    className="w-full h-full border-0"
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-center p-6 space-y-3 bg-surface-muted">
                    <PlayCircle className="w-14 h-14 text-accent/60" />
                    <p className="text-text-primary font-medium text-sm">Visual Lecture & Concept Breakdown</p>
                    <a
                      href={`https://www.youtube.com/results?search_query=${encodeURIComponent(video.search_query || topicData.name)}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-accent hover:bg-accent-hover text-white text-xs font-semibold rounded-lg transition shadow-xs"
                    >
                      Search Video Tutorials <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                )}
              </div>
            </Card>

            {/* Why It Matters Card */}
            {topicData.why_it_matters && (
              <Card className="border-accent/30 bg-accent-subtle/20 shadow-xs">
                <CardContent className="p-5 sm:p-6">
                  <div className="flex items-center gap-2 text-accent font-bold text-sm mb-2">
                    <Sparkles className="w-4 h-4" /> Why This Concept Matters in Production
                  </div>
                  <p className="text-text-secondary leading-relaxed text-xs sm:text-sm">
                    {topicData.why_it_matters}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Column: Key Takeaways & Complexity */}
          <div className="space-y-6">
            <Card className="shadow-xs">
              <CardContent className="p-5 sm:p-6 space-y-4">
                <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-success" /> Key Takeaways
                </h3>
                <ul className="space-y-3 text-xs sm:text-sm text-text-secondary">
                  {(video.key_takeaways || [
                    'Understand the core contiguous memory layout.',
                    'Know the trade-offs between linear scan and indexed access.',
                    'Practice standard two-pointer in-place transformations.'
                  ]).map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2.5">
                      <span className="w-5 h-5 rounded-full bg-success-subtle text-success flex items-center justify-center text-xs font-bold mt-0.5 shrink-0">
                        {idx + 1}
                      </span>
                      <span className="leading-relaxed">{item}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Asymptotic Complexity Matrix */}
            <Card className="shadow-xs">
              <CardContent className="p-5 sm:p-6 space-y-4">
                <h3 className="text-base font-bold text-text-primary flex items-center gap-2">
                  <Zap className="w-4 h-4 text-warning" /> Asymptotic Complexity
                </h3>
                <div className="space-y-2 text-xs sm:text-sm">
                  {Object.entries(complexity).map(([op, comp]) => (
                    <div key={op} className="flex items-center justify-between py-1.5 border-b border-border last:border-0">
                      <span className="text-text-muted capitalize">{op}</span>
                      <span className="font-mono px-2 py-0.5 bg-surface-muted rounded text-accent font-semibold text-xs border border-border">
                        {comp}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Button
              onClick={() => setActiveTab('understand')}
              variant="primary"
              className="w-full text-xs sm:text-sm font-semibold gap-1.5 shadow-xs"
            >
              <span>Continue to Detailed Notes</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {/* TAB CONTENT 2: UNDERSTAND (NOTES & MULTI-LANGUAGE CODE) */}
      {activeTab === 'understand' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          {/* Notes Column */}
          <div className="space-y-4">
            <h3 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-accent" /> Architectural Breakdown
            </h3>
            {notes.map((note, idx) => (
              <Card key={idx} className="shadow-xs hover:border-border-hover transition-colors">
                <CardContent className="p-5 space-y-2">
                  <h4 className="text-sm sm:text-base font-bold text-accent">{note.title}</h4>
                  <div className="text-xs sm:text-sm text-text-secondary leading-relaxed whitespace-pre-line">
                    {note.content}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Code Snippets Column */}
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2">
                <Code2 className="w-5 h-5 text-success" /> Reference Implementations
              </h3>
              {/* Language Switcher */}
              <div className="flex bg-surface-muted border border-border p-1 rounded-xl">
                {Object.keys(code_snippets).map((lang) => (
                  <button
                    key={lang}
                    onClick={() => setSelectedLang(lang)}
                    className={cn(
                      "px-2.5 py-1 text-xs font-semibold rounded-lg capitalize transition cursor-pointer",
                      selectedLang === lang
                        ? "bg-accent text-white shadow-xs"
                        : "text-text-secondary hover:text-text-primary"
                    )}
                  >
                    {lang}
                  </button>
                ))}
              </div>
            </div>

            <Card className="overflow-hidden border-border shadow-xs">
              <div className="bg-surface-muted px-4 py-2.5 border-b border-border flex items-center justify-between">
                <span className="text-xs font-mono text-text-secondary capitalize font-semibold">{selectedLang} Pattern</span>
                <button
                  onClick={() => handleCopy(code_snippets[selectedLang] || '')}
                  className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-text-primary px-2.5 py-1 bg-surface hover:bg-surface-hover border border-border rounded-md transition cursor-pointer"
                >
                  {copiedCode ? <Check className="w-3.5 h-3.5 text-success" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedCode ? 'Copied!' : 'Copy Snippet'}</span>
                </button>
              </div>
              <pre className="p-5 font-mono text-xs overflow-x-auto leading-relaxed bg-[#0d1117] text-slate-100 selection:bg-accent/40">
                <code className="text-slate-100 font-mono">{code_snippets[selectedLang] || '# No snippet available for this language'}</code>
              </pre>
            </Card>

            <div className="pt-2">
              <Button
                onClick={() => setActiveTab('practice')}
                variant="primary"
                className="w-full text-xs sm:text-sm font-semibold gap-1.5 shadow-xs"
              >
                <span>Proceed to Practice Problems</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT 3: PRACTICE (ADAPTIVE EXERCISES) */}
      {activeTab === 'practice' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2">
                <Code2 className="w-5 h-5 text-accent" /> Progressive Practice Curriculum
              </h3>
              <p className="text-xs sm:text-sm text-text-secondary">
                Curated challenges sequenced from fundamental lookups to algorithmic edge cases.
              </p>
            </div>
            <Badge variant="outline" className="text-xs font-semibold px-3 py-1.5 self-start">
              {stats.solved_problems} / {stats.total_problems} Completed
            </Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {practice_problems.map((problem) => {
              const diffBadges: Record<string, { label: string; cls: string }> = {
                easy: { label: 'Easy', cls: 'bg-success-subtle text-success border-success/20' },
                easy_plus: { label: 'Easy+', cls: 'bg-success-subtle text-success border-success/20' },
                medium: { label: 'Medium', cls: 'bg-warning-subtle text-warning border-warning/20' },
                medium_plus: { label: 'Medium+', cls: 'bg-warning-subtle text-warning border-warning/20' },
                hard: { label: 'Hard', cls: 'bg-error-subtle text-error border-error/20' },
                advanced: { label: 'Advanced', cls: 'bg-accent-subtle text-accent border-accent/20' },
              };

              const currentDiff = diffBadges[problem.difficulty] || diffBadges.easy;

              return (
                <Card
                  key={problem.id}
                  className={cn(
                    "p-5 rounded-2xl border transition-all duration-200 flex flex-col justify-between shadow-2xs hover:shadow-xs",
                    problem.is_completed
                      ? "bg-success-subtle/20 border-success/30 hover:border-success/60"
                      : "hover:border-accent/40"
                  )}
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span className={cn("px-2.5 py-0.5 text-xs font-bold rounded-full border uppercase tracking-wider", currentDiff.cls)}>
                        {currentDiff.label}
                      </span>
                      {problem.is_completed ? (
                        <span className="flex items-center gap-1 text-xs text-success font-semibold">
                          <CheckCircle2 className="w-4 h-4" /> Solved
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-xs text-text-muted">
                          <Circle className="w-3.5 h-3.5" /> Ready
                        </span>
                      )}
                    </div>

                    <h4 className="text-base font-bold text-text-primary">
                      {problem.title}
                    </h4>

                    <p className="text-xs text-text-secondary line-clamp-2 leading-relaxed">
                      {problem.recommended_reason}
                    </p>
                  </div>

                  <div className="pt-4 mt-4 border-t border-border flex items-center justify-between">
                    <span className="text-xs font-mono text-text-muted">
                      entry: {problem.entrypoint}()
                    </span>
                    <Button
                      onClick={() => navigate(`/problems/${problem.id}`)}
                      size="sm"
                      variant={problem.is_completed ? "outline" : "primary"}
                      className="text-xs font-semibold gap-1.5"
                    >
                      <span>{problem.is_completed ? 'Review Solution' : 'Solve Problem'}</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB CONTENT 4: MASTER (MASTERY SUMMARY & CONTINUATION) */}
      {activeTab === 'master' && (
        <Card className="max-w-2xl mx-auto text-center shadow-xs p-6 sm:p-8 space-y-6">
          <div className="w-16 h-16 mx-auto rounded-full bg-accent-subtle border border-accent/20 flex items-center justify-center">
            <Award className="w-8 h-8 text-accent" />
          </div>

          <div className="space-y-2">
            <h3 className="text-xl sm:text-2xl font-bold text-text-primary">Topic Mastery Milestone</h3>
            <p className="text-xs sm:text-sm text-text-secondary max-w-md mx-auto leading-relaxed">
              Complete all practice problems to unlock full competency certification for <strong className="text-accent">{topicData.name}</strong>.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3 max-w-md mx-auto py-2">
            <div className="bg-surface-muted p-3.5 rounded-xl border border-border">
              <div className="text-xl sm:text-2xl font-black text-text-primary">{stats.total_problems}</div>
              <div className="text-[11px] text-text-muted font-medium mt-0.5">Total Problems</div>
            </div>
            <div className="bg-surface-muted p-3.5 rounded-xl border border-border">
              <div className="text-xl sm:text-2xl font-black text-success">{stats.solved_problems}</div>
              <div className="text-[11px] text-text-muted font-medium mt-0.5">Solved</div>
            </div>
            <div className="bg-surface-muted p-3.5 rounded-xl border border-border">
              <div className="text-xl sm:text-2xl font-black text-accent">{stats.mastery_percentage}%</div>
              <div className="text-[11px] text-text-muted font-medium mt-0.5">Mastery</div>
            </div>
          </div>

          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Button
              onClick={() => setActiveTab('practice')}
              variant="outline"
              className="w-full sm:w-auto text-xs sm:text-sm font-semibold"
            >
              Practice More Problems
            </Button>
            <Button
              onClick={() => navigate('/roadmap')}
              variant="primary"
              className="w-full sm:w-auto text-xs sm:text-sm font-semibold gap-1.5 shadow-xs"
            >
              <span>Next Topic in Roadmap</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};
