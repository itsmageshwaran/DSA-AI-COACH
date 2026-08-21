import { useState, useEffect } from 'react';
import { Target, TrendingUp, Brain, Loader2, Trophy, Star, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { learningApi } from '../services/learning';
import type { ConceptMasteryResponse, ProgressSummary, AchievementResponse, LearningPath } from '../services/learning';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../features/auth/AuthContext';
import { cn } from '../lib/utils';

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
    ? Math.round(concepts.reduce((acc, curr) => acc + curr.mastery_percentage, 0) / concepts.length)
    : 0;

  const careerGoal = user?.profile?.career_goal || "DSA Mastery";

  const strengths = concepts.filter(c => c.mastery_percentage >= 70);
  const focusAreas = concepts.filter(c => c.mastery_percentage < 70);

  return (
    <div className="w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8 animate-fade-in pb-24 font-sans text-text-primary min-w-0">
      {/* Page Header */}
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
                  style={{ width: `${summary?.completion_percentage || 0}%` }}
                ></div>
              </div>
              <span className="text-sm font-bold text-text-primary w-10 text-right">
                {Math.round(summary?.completion_percentage || 0)}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* 4-Card Responsive Metric Grid (1-col mobile, 2-col tablet/zoom, 4-col desktop) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 min-[1280px]:grid-cols-4 gap-4 sm:gap-5 min-w-0">
        <Card className="p-5 sm:p-6 flex flex-col items-center text-center justify-center hover:border-border-hover transition-all duration-200 shadow-2xs">
          <div className="w-12 h-12 bg-accent-subtle text-accent rounded-xl flex items-center justify-center mb-3 shadow-2xs border border-accent/10">
            <Target className="w-6 h-6" />
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-text-primary mb-0.5 tracking-tight">
            {summary?.total_lessons_completed || 0}
          </h3>
          <p className="text-text-secondary font-medium text-xs sm:text-sm">Problems Solved</p>
        </Card>

        <Card className="p-5 sm:p-6 flex flex-col items-center text-center justify-center hover:border-border-hover transition-all duration-200 shadow-2xs">
          <div className="w-12 h-12 bg-success-subtle text-success rounded-xl flex items-center justify-center mb-3 shadow-2xs border border-success/10">
            <Trophy className="w-6 h-6" />
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-text-primary mb-0.5 tracking-tight">
            {achievements.length}
          </h3>
          <p className="text-text-secondary font-medium text-xs sm:text-sm">Achievements Earned</p>
        </Card>

        <Card className="p-5 sm:p-6 flex flex-col items-center text-center justify-center hover:border-border-hover transition-all duration-200 shadow-2xs">
          <div className="w-12 h-12 bg-warning-subtle text-warning rounded-xl flex items-center justify-center mb-3 shadow-2xs border border-warning/10">
            <TrendingUp className="w-6 h-6" />
          </div>
          <h3 className="text-2xl sm:text-3xl font-bold text-text-primary mb-0.5 tracking-tight">
            {summary?.average_score ? Math.round(summary.average_score) : 0}%
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

      {/* Analytics Section: Concept Mastery (2 cols) & Strength/Focus Insights (1 col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8 min-w-0">
        
        {/* Left Col: Concept Mastery List */}
        <div className="lg:col-span-2 space-y-4 min-w-0">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2">
              <Brain className="w-5 h-5 text-accent" />
              <span>Concept Mastery</span>
            </h2>
            <Badge variant="outline" className="text-xs font-semibold shrink-0">
              Problem Analytics
            </Badge>
          </div>
          
          <Card className="divide-y divide-border overflow-hidden shadow-2xs">
            {concepts.length > 0 ? (
              concepts.map((concept, idx) => (
                <div key={idx} className="p-4 sm:p-5 flex items-center justify-between gap-4 hover:bg-surface-hover/50 transition-colors">
                  <div className="flex flex-col gap-0.5 min-w-0 flex-1">
                    <span className="font-bold text-text-primary text-sm sm:text-base truncate">
                      {concept.concept_name}
                    </span>
                    <span className="text-xs font-medium text-text-muted">
                      Topic Proficiency
                    </span>
                  </div>
                  <div className="flex items-center gap-3 sm:gap-4 shrink-0">
                    <div className="w-24 sm:w-36 h-2 bg-surface-muted rounded-full overflow-hidden shadow-inner border border-border/40">
                      <div 
                        className={cn(
                          "h-full rounded-full transition-all duration-1000",
                          concept.mastery_percentage >= 70 ? "bg-success" :
                          concept.mastery_percentage >= 40 ? "bg-accent" : "bg-warning"
                        )}
                        style={{ width: `${concept.mastery_percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-xs sm:text-sm font-bold text-text-primary w-10 text-right">
                      {Math.round(concept.mastery_percentage)}%
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-10 text-center text-text-secondary flex flex-col items-center">
                <div className="w-12 h-12 bg-surface-muted rounded-full flex items-center justify-center mb-3">
                  <Brain className="w-6 h-6 text-text-muted" />
                </div>
                <h3 className="text-base font-bold text-text-primary mb-1">No Mastery Profile Yet</h3>
                <p className="text-xs text-text-muted max-w-sm">Complete coding challenges and lessons in your roadmap to unlock real-time concept mastery stats.</p>
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
                      <span className="truncate">{c.concept_name}</span>
                      <span className="text-success font-bold shrink-0">{Math.round(c.mastery_percentage)}%</span>
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
                      <span className="truncate">{c.concept_name}</span>
                      <span className="text-warning font-bold shrink-0">{Math.round(c.mastery_percentage)}%</span>
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

      {/* Achievements & Milestones Section */}
      <div className="space-y-4 pt-4 min-w-0">
        <div className="flex items-center justify-between">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary flex items-center gap-2">
            <Trophy className="w-5 h-5 text-accent" />
            <span>Achievements &amp; Milestones</span>
          </h2>
          <span className="text-xs text-text-muted font-medium">{achievements.length} Unlocked</span>
        </div>
        
        {achievements.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.map((achievement, idx) => (
              <Card key={idx} className="p-5 flex items-start gap-4 hover:border-accent/40 transition-colors shadow-2xs">
                <div className="w-11 h-11 bg-accent-subtle text-accent rounded-xl flex items-center justify-center shrink-0 border border-accent/10">
                  <Star className="w-5 h-5" />
                </div>
                <div className="min-w-0 flex-1">
                  <h4 className="font-bold text-sm text-text-primary mb-1 truncate">{achievement.name}</h4>
                  <p className="text-xs text-text-secondary leading-relaxed mb-2 line-clamp-2">
                    {achievement.description}
                  </p>
                  <span className="text-[11px] font-medium text-text-muted block">
                    Earned on {new Date(achievement.earned_at).toLocaleDateString()}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="p-10 text-center text-text-secondary shadow-2xs">
            <div className="w-12 h-12 bg-surface-muted rounded-full flex items-center justify-center mx-auto mb-3">
              <Trophy className="w-6 h-6 text-text-muted" />
            </div>
            <h3 className="text-base font-bold text-text-primary mb-1">No Achievements Unlocked Yet</h3>
            <p className="text-xs text-text-muted max-w-sm mx-auto">Solve problems, maintain streaks, and complete learning phases to unlock DSA achievements.</p>
          </Card>
        )}
      </div>

    </div>
  );
}
