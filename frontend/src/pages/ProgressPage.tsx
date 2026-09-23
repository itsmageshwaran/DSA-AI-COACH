import { useState, useEffect } from 'react';
import { Target, TrendingUp, Brain, Loader2, Trophy, Star, ArrowUpRight, CheckCircle2, Lock, Zap } from 'lucide-react';
import { learningApi } from '../services/learning';
import type { ConceptMasteryResponse, ProgressSummary, AchievementResponse, LearningPath } from '../services/learning';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../features/auth/AuthContext';
import { cn } from '../lib/utils';

// ─── helpers ─────────────────────────────────────────────────────────────────

/** Returns the Tailwind bar colour class based on mastery percentage. */
function masteryBarClass(pct: number): string {
  if (pct >= 80) return 'bg-success';
  if (pct >= 50) return 'bg-accent';
  if (pct >= 25) return 'bg-warning';
  return 'bg-danger';
}

/** Returns a short human-readable label for a mastery percentage. */
function masteryLabel(pct: number): { text: string; className: string } {
  if (pct >= 80) return { text: 'Mastered', className: 'text-success' };
  if (pct >= 50) return { text: 'Proficient', className: 'text-accent' };
  if (pct >= 25) return { text: 'Learning', className: 'text-warning' };
  return { text: 'Beginner', className: 'text-danger' };
}

// ─── component ────────────────────────────────────────────────────────────────

export function ProgressPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<ProgressSummary | null>(null);
  const [concepts, setConcepts] = useState<ConceptMasteryResponse[]>([]);
  const [achievements, setAchievements] = useState<AchievementResponse[]>([]);
  const [path, setPath] = useState<LearningPath | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [summaryData, conceptsData, achievementsData, pathData] = await Promise.all([
          learningApi.getProgressSummary(),
          learningApi.getConceptMastery(),
          learningApi.getAchievements(),
          learningApi.getEnrolledPath()
        ]);
        setSummary(summaryData);
        setConcepts(conceptsData);
        setAchievements(achievementsData);
        setPath(pathData);
      } catch (err) {
        console.error('Failed to load progress data:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="h-96 flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-4 text-text-secondary">
          <Loader2 className="w-8 h-8 animate-spin text-accent" />
          <p className="font-medium text-sm">Loading progress intelligence...</p>
        </div>
      </div>
    );
  }

  const overallMastery = concepts.length > 0
    ? Math.round(concepts.reduce((acc, curr) => acc + (curr.mastery_percentage ?? 0), 0) / concepts.length)
    : 0;

  const totalProblemsSolved = summary?.total_lessons_completed ?? 0;
  const careerGoal = user?.profile?.career_goal || 'DSA Mastery';
  const strengths = concepts.filter(c => (c.mastery_percentage ?? 0) >= 70);
  const focusAreas = concepts.filter(c => (c.mastery_percentage ?? 0) < 70);

  return (
    <div className="w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 animate-fade-in pb-24 font-sans text-text-primary min-w-0">

      {/* ── Page Header ─────────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border pb-6">
        <div className="space-y-1.5 min-w-0">
          <Badge variant="outline" className="bg-accent-subtle text-accent border-accent/20 text-xs font-semibold">
            <Target className="w-3.5 h-3.5 mr-1.5" />
            {careerGoal} Track
          </Badge>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-text-primary tracking-tight">
            Progress Intelligence
          </h1>
          <p className="text-text-secondary text-sm sm:text-base max-w-2xl leading-relaxed">
            Track your algorithmic mastery, review performance metrics, and see your continuous learning progress.
          </p>
        </div>

        {path && (
          <div className="flex flex-col sm:items-end bg-surface p-3.5 rounded-xl border border-border shrink-0 shadow-2xs">
            <span className="text-xs font-semibold text-text-secondary mb-1.5">Roadmap Completion</span>
            <div className="flex items-center gap-3">
              <div className="w-36 sm:w-44 h-2 bg-surface-muted rounded-full overflow-hidden shadow-inner border border-border/40">
                <div
                  className="h-full bg-success rounded-full transition-all duration-1000"
                  style={{ width: `${summary?.completion_percentage ?? 0}%` }}
                />
              </div>
              <span className="text-sm font-bold text-text-primary w-10 text-right">
                {Math.round(summary?.completion_percentage ?? 0)}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* ── Hero Stat: Total Problems Solved ────────────────────────────────── */}
      <div className="relative overflow-hidden rounded-2xl border border-accent/30 bg-gradient-to-br from-accent/10 via-surface to-accent-subtle/20 p-6 sm:p-8 shadow-md">
        {/* decorative glow */}
        <div className="pointer-events-none absolute -top-10 -right-10 w-48 h-48 rounded-full bg-accent/20 blur-3xl" />
        <div className="relative flex flex-col sm:flex-row sm:items-center gap-6">
          {/* icon + number */}
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-accent/20 border border-accent/30 flex items-center justify-center shadow-lg shrink-0">
              <Zap className="w-8 h-8 sm:w-10 sm:h-10 text-accent" />
            </div>
            <div>
              <p className="text-xs sm:text-sm font-semibold text-text-secondary uppercase tracking-widest mb-0.5">
                Total Problems Solved
              </p>
              <p className="text-5xl sm:text-6xl font-extrabold text-accent leading-none tracking-tight">
                {totalProblemsSolved}
              </p>
            </div>
          </div>

          {/* divider */}
          <div className="hidden sm:block w-px self-stretch bg-border mx-2" />

          {/* secondary stats */}
          <div className="flex flex-wrap gap-6 sm:gap-8">
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-0.5">Avg Score</span>
              <span className="text-2xl font-bold text-text-primary">
                {summary?.average_score != null ? `${Math.round(summary.average_score)}%` : '—'}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-0.5">Overall Mastery</span>
              <span className="text-2xl font-bold text-accent">{overallMastery}%</span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-0.5">Achievements</span>
              <span className="text-2xl font-bold text-text-primary">{achievements?.length ?? 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── 4-Card Metric Grid ───────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 min-[1280px]:grid-cols-4 gap-4 sm:gap-5 min-w-0">
        <Card className="p-5 sm:p-6 flex flex-col items-center text-center justify-center hover:border-border-hover transition-all duration-200 shadow-2xs">
          <div className="w-12 h-12 bg-accent-subtle text-accent rounded-xl flex items-center justify-center mb-3 shadow-2xs border border-accent/10">
            <Target className="w-6 h-6" />
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-text-primary mb-0.5 tracking-tight">
            {totalProblemsSolved}
          </h3>
          <p className="text-text-secondary font-medium text-xs sm:text-sm">Problems Solved</p>
        </Card>

        <Card className="p-5 sm:p-6 flex flex-col items-center text-center justify-center hover:border-border-hover transition-all duration-200 shadow-2xs">
          <div className="w-12 h-12 bg-success-subtle text-success rounded-xl flex items-center justify-center mb-3 shadow-2xs border border-success/10">
            <Trophy className="w-6 h-6" />
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-text-primary mb-0.5 tracking-tight">
            {achievements?.length ?? 0}
          </h3>
          <p className="text-text-secondary font-medium text-xs sm:text-sm">Achievements Earned</p>
        </Card>

        <Card className="p-5 sm:p-6 flex flex-col items-center text-center justify-center hover:border-border-hover transition-all duration-200 shadow-2xs">
          <div className="w-12 h-12 bg-warning-subtle text-warning rounded-xl flex items-center justify-center mb-3 shadow-2xs border border-warning/10">
            <TrendingUp className="w-6 h-6" />
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-text-primary mb-0.5 tracking-tight">
            {summary?.average_score != null ? `${Math.round(summary.average_score)}%` : '—'}
          </h3>
          <p className="text-text-secondary font-medium text-xs sm:text-sm">Average Score</p>
        </Card>

        <Card className="p-5 sm:p-6 flex flex-col items-center text-center justify-center hover:border-accent/40 transition-all duration-200 shadow-2xs bg-gradient-to-b from-surface to-accent-subtle/30 border-accent/20">
          <div className="w-12 h-12 bg-accent/20 text-accent rounded-xl flex items-center justify-center mb-3 shadow-2xs border border-accent/20">
            <Brain className="w-6 h-6" />
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-accent mb-0.5 tracking-tight">
            {overallMastery}%
          </h3>
          <p className="text-text-secondary font-medium text-xs sm:text-sm">Overall Mastery</p>
        </Card>
      </div>

      {/* ── Analytics: Concept Mastery + Insights ───────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8 min-w-0">

        {/* Left Col: Per-topic Mastery Progress Bars */}
        <div className="lg:col-span-2 space-y-4 min-w-0">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2">
              <Brain className="w-5 h-5 text-accent" />
              <span>Topic Mastery</span>
            </h2>
            <Badge variant="outline" className="text-xs font-semibold shrink-0">
              {concepts.length} Topic{concepts.length !== 1 ? 's' : ''}
            </Badge>
          </div>

          <Card className="divide-y divide-border overflow-hidden shadow-2xs">
            {concepts.length > 0 ? (
              concepts.map((concept, idx) => {
                const pct = Math.round(concept.mastery_percentage ?? 0);
                const label = masteryLabel(pct);
                const barClass = masteryBarClass(pct);
                return (
                  <div key={idx} className="p-4 sm:p-5 hover:bg-surface-hover/50 transition-colors">
                    {/* Row 1: topic name + badge + percentage */}
                    <div className="flex items-center justify-between gap-3 mb-2.5">
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="font-bold text-text-primary text-sm sm:text-base truncate">
                          {concept.concept_name ?? '—'}
                        </span>
                        <span
                          className={cn(
                            'hidden sm:inline text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-full border',
                            pct >= 80
                              ? 'bg-success/10 text-success border-success/20'
                              : pct >= 50
                              ? 'bg-accent/10 text-accent border-accent/20'
                              : pct >= 25
                              ? 'bg-warning/10 text-warning border-warning/20'
                              : 'bg-danger/10 text-danger border-danger/20'
                          )}
                        >
                          {label.text}
                        </span>
                      </div>
                      <span className={cn('text-sm font-extrabold shrink-0', label.className)}>
                        {pct}%
                      </span>
                    </div>

                    {/* Row 2: full-width color-coded progress bar */}
                    <div className="w-full h-3 bg-surface-muted rounded-full overflow-hidden shadow-inner border border-border/30">
                      <div
                        className={cn('h-full rounded-full transition-all duration-1000', barClass)}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="p-10 text-center text-text-secondary flex flex-col items-center">
                <div className="w-12 h-12 bg-surface-muted rounded-full flex items-center justify-center mb-3">
                  <Brain className="w-6 h-6 text-text-muted" />
                </div>
                <h3 className="text-base font-bold text-text-primary mb-1">No Mastery Profile Yet</h3>
                <p className="text-xs text-text-muted max-w-sm">
                  Complete coding challenges and lessons in your roadmap to unlock real-time concept mastery stats.
                </p>
              </div>
            )}
          </Card>
        </div>

        {/* Right Col: Strengths & Focus Areas */}
        <div className="space-y-6 min-w-0">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2">
            <ArrowUpRight className="w-5 h-5 text-success" />
            <span>Learning Insights</span>
          </h2>

          <div className="space-y-4">
            {/* Strengths */}
            <Card className="p-5 space-y-3 shadow-2xs">
              <h3 className="font-bold text-sm text-text-primary flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-success" />
                <span>Verified Strengths (≥70%)</span>
              </h3>
              {strengths.length > 0 ? (
                <ul className="space-y-2.5">
                  {strengths.map((c, i) => (
                    <li key={i} className="flex items-center justify-between text-xs sm:text-sm font-medium text-text-secondary">
                      <span className="truncate">{c.concept_name ?? '—'}</span>
                      <span className="text-success font-bold shrink-0">{Math.round(c.mastery_percentage ?? 0)}%</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-text-muted">Master more problems to build your confirmed strengths.</p>
              )}
            </Card>

            {/* Focus Areas */}
            <Card className="p-5 space-y-3 shadow-2xs">
              <h3 className="font-bold text-sm text-text-primary flex items-center gap-2">
                <Target className="w-4 h-4 text-warning" />
                <span>Focus Areas (&lt;70%)</span>
              </h3>
              {focusAreas.length > 0 ? (
                <ul className="space-y-2.5">
                  {focusAreas.map((c, i) => (
                    <li key={i} className="flex items-center justify-between text-xs sm:text-sm font-medium text-text-secondary">
                      <span className="truncate">{c.concept_name ?? '—'}</span>
                      <span className="text-warning font-bold shrink-0">{Math.round(c.mastery_percentage ?? 0)}%</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-text-muted">No focus areas flagged. All reviewed concepts are in good standing.</p>
              )}
            </Card>
          </div>
        </div>

      </div>

      {/* ── Achievements & Milestones ────────────────────────────────────────── */}
      <div className="space-y-4 pt-4 min-w-0">
        <div className="flex items-center justify-between">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2">
            <Trophy className="w-5 h-5 text-accent" />
            <span>Achievements &amp; Milestones</span>
          </h2>
          <span className="text-xs text-text-muted font-medium">
            {achievements?.length ?? 0} Unlocked
          </span>
        </div>

        {(achievements?.length ?? 0) > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.map((achievement, idx) => {
              // All items returned by the API are earned/unlocked; treat any with a
              // missing or falsy earned_at as locked (null-safe guard).
              const isUnlocked = Boolean(achievement?.earned_at);
              const earnedDate =
                isUnlocked && achievement.earned_at
                  ? (() => {
                      try {
                        return new Date(achievement.earned_at).toLocaleDateString();
                      } catch {
                        return null;
                      }
                    })()
                  : null;

              return (
                <Card
                  key={idx}
                  className={cn(
                    'p-5 flex items-start gap-4 transition-all duration-200 shadow-2xs',
                    isUnlocked
                      ? 'hover:border-accent/50 ring-1 ring-accent/10 shadow-[0_0_16px_0_rgba(var(--color-accent-rgb,99,102,241),0.12)]'
                      : 'opacity-50 grayscale hover:border-border'
                  )}
                >
                  {/* Icon bubble */}
                  <div
                    className={cn(
                      'w-11 h-11 rounded-xl flex items-center justify-center shrink-0 border',
                      isUnlocked
                        ? 'bg-accent-subtle text-accent border-accent/20 shadow-[0_0_12px_2px_rgba(var(--color-accent-rgb,99,102,241),0.18)]'
                        : 'bg-surface-muted text-text-muted border-border'
                    )}
                  >
                    {isUnlocked ? (
                      <Star className="w-5 h-5" />
                    ) : (
                      <Lock className="w-5 h-5" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 className="font-bold text-sm text-text-primary truncate">
                        {achievement?.name ?? 'Unknown Achievement'}
                      </h4>
                      {isUnlocked && (
                        <span className="text-[10px] font-bold uppercase tracking-wide text-success bg-success/10 border border-success/20 rounded-full px-1.5 py-0.5 shrink-0">
                          Unlocked
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-text-secondary leading-relaxed mb-2 line-clamp-2">
                      {achievement?.description ?? ''}
                    </p>
                    {earnedDate ? (
                      <span className="text-[11px] font-medium text-text-muted block">
                        Earned on {earnedDate}
                      </span>
                    ) : (
                      <span className="text-[11px] font-medium text-text-muted block italic">
                        Not yet earned
                      </span>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        ) : (
          <Card className="p-10 text-center text-text-secondary shadow-2xs">
            <div className="w-12 h-12 bg-surface-muted rounded-full flex items-center justify-center mx-auto mb-3">
              <Trophy className="w-6 h-6 text-text-muted" />
            </div>
            <h3 className="text-base font-bold text-text-primary mb-1">No Achievements Unlocked Yet</h3>
            <p className="text-xs text-text-muted max-w-sm mx-auto">
              Solve problems, maintain streaks, and complete learning phases to unlock DSA achievements.
            </p>
          </Card>
        )}
      </div>

    </div>
  );
}
