import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { learningApi } from '../services/learning';
import type { ProgressSummary, RecommendationResponse, LearningPath } from '../services/learning';
import { useAuth } from '../features/auth/AuthContext';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { ProgressRing } from '../components/ui/ProgressRing';
import { Play, CheckCircle2, TrendingUp, Compass, Code, LayoutDashboard, Target, Zap, ArrowRight, Trophy } from 'lucide-react';
import { Skeleton } from '../components/ui/Skeleton';
import { cn } from '../lib/utils';

export function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<ProgressSummary | null>(null);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [path, setPath] = useState<LearningPath | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [progressData, nextProbData, pathData] = await Promise.all([
          learningApi.getProgressSummary(),
          learningApi.getNextProblem(),
          learningApi.getEnrolledPath()
        ]);
        setMetrics(progressData);
        setRecommendation(nextProbData);
        setPath(pathData);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const firstName = user?.name?.split(' ')[0] || 'Student';
  const careerGoal = user?.profile?.career_goal;

  if (isLoading) {
    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto space-y-8 min-w-0">
        <Skeleton className="h-32 w-full rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton className="h-40 rounded-xl lg:col-span-2" />
          <Skeleton className="h-40 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8 pb-24 font-sans text-text-primary min-w-0">
      
      {/* Header / Greeting */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-border pb-6 min-w-0">
        <div className="space-y-1.5 min-w-0">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-accent-subtle text-accent text-xs font-semibold tracking-wide border border-accent/20">
              <Target className="w-3.5 h-3.5" />
              {careerGoal || "DSA Mastery"}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-text-primary">
            Good morning, {firstName}.
          </h1>
          <p className="text-text-secondary text-sm sm:text-base leading-relaxed">
            {recommendation 
              ? `You're currently mastering ${recommendation.topic}.` 
              : "Ready to master Data Structures and Algorithms?"}
          </p>
        </div>
        
        <div className="shrink-0">
          <Button 
            size="lg" 
            onClick={() => {
              if (recommendation && recommendation.exercise_id) {
                navigate(`/workspace/${recommendation.exercise_id}`);
              } else {
                navigate('/learn');
              }
            }}
            className="w-full sm:w-auto font-semibold shadow-xs"
          >
            <Play className="w-4 h-4 mr-2 fill-current" />
            {recommendation && recommendation.exercise_id ? "Continue Learning" : "Start Learning Path"}
          </Button>
        </div>
      </div>

      {/* Main Grid: 2 cols Main / 1 col Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 min-w-0">
        
        {/* Main Content Area (2 Cols) */}
        <div className="lg:col-span-2 space-y-8 min-w-0">
          {/* Next Best Action Card */}
          <section className="space-y-3 min-w-0">
            <h2 className="text-xs font-bold tracking-wider text-text-muted uppercase flex items-center gap-2">
              <Compass className="w-4 h-4 text-accent" />
              <span>Next Best Action</span>
            </h2>
            
            {recommendation ? (
              <Card className="hover:border-accent/40 transition-all duration-200 border-l-4 border-l-accent overflow-hidden shadow-2xs">
                <CardContent className="p-5 sm:p-6">
                  <div className="flex flex-col gap-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="text-xs font-bold text-accent uppercase tracking-wider">{recommendation.topic}</span>
                      <span className={cn(
                        "px-2.5 py-0.5 rounded text-xs font-semibold border",
                        recommendation.difficulty.toLowerCase().includes('easy') ? "bg-success-subtle text-success border-success/20" :
                        recommendation.difficulty.toLowerCase().includes('medium') ? "bg-warning-subtle text-warning border-warning/20" :
                        recommendation.difficulty.toLowerCase().includes('hard') ? "bg-error-subtle text-error border-error/20" :
                        "bg-surface-muted text-text-secondary border-border"
                      )}>
                        Difficulty: {recommendation.difficulty}
                      </span>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 items-start sm:items-center">
                      <div className="bg-accent-subtle text-accent p-3.5 rounded-xl shrink-0 border border-accent/10">
                        <Code className="w-6 h-6" />
                      </div>
                      <div className="flex-1 space-y-1 min-w-0">
                        <h3 className="text-lg sm:text-xl font-bold text-text-primary truncate">{recommendation.title}</h3>
                        <div className="flex items-start gap-2 text-xs sm:text-sm text-text-secondary mt-2 bg-surface-muted/60 p-3 rounded-lg border border-border/50">
                          <Zap className="w-4 h-4 shrink-0 text-warning mt-0.5" />
                          <p className="leading-relaxed"><strong>Why this problem:</strong> {recommendation.reason}</p>
                        </div>
                      </div>
                      <Button 
                        onClick={() => {
                          if (recommendation && recommendation.exercise_id) {
                            navigate(`/workspace/${recommendation.exercise_id}`);
                          } else {
                            navigate('/problems');
                          }
                        }} 
                        variant="primary" 
                        className="w-full sm:w-auto shrink-0 font-semibold text-xs sm:text-sm mt-2 sm:mt-0"
                      >
                        {recommendation?.exercise_id ? "Start Problem" : "Browse Problems"}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="shadow-2xs">
                <CardContent className="p-8 text-center">
                  <div className="w-12 h-12 rounded-full bg-surface-muted flex items-center justify-center mx-auto mb-3">
                    <CheckCircle2 className="w-6 h-6 text-text-muted" />
                  </div>
                  <h3 className="text-base font-bold text-text-primary mb-1">Phase Complete</h3>
                  <p className="text-xs text-text-secondary mb-4">You have mastered all current roadmap problems. Browse the full library or curriculum for more challenges.</p>
                  <Button onClick={() => navigate('/problems')} variant="outline" size="sm">Browse Problems</Button>
                </CardContent>
              </Card>
            )}
          </section>

          {/* Roadmap Progress Overview Card */}
          <section className="space-y-3 min-w-0">
            <h2 className="text-xs font-bold tracking-wider text-text-muted uppercase flex items-center gap-2">
              <LayoutDashboard className="w-4 h-4 text-accent" />
              <span>Roadmap Progress</span>
            </h2>
            
            {path ? (
              <Card className="hover:border-border-hover transition-colors shadow-2xs">
                <CardContent className="p-5 sm:p-6 space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <h3 className="text-base font-bold text-text-primary">{path.title}</h3>
                      <p className="text-xs text-text-secondary mt-0.5">{path.description}</p>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => navigate('/learn')} className="text-xs">
                      View Roadmap <ArrowRight className="w-3.5 h-3.5 ml-1" />
                    </Button>
                  </div>
                  
                  <div className="space-y-1.5 pt-2">
                    <div className="flex justify-between text-xs font-semibold text-text-secondary">
                      <span>Curriculum Completion</span>
                      <span className="text-text-primary font-bold">{Math.round(metrics?.completion_percentage || 0)}%</span>
                    </div>
                    <div className="w-full h-2 bg-surface-muted rounded-full overflow-hidden border border-border/40">
                      <div 
                        className="bg-accent h-full rounded-full transition-all duration-1000"
                        style={{ width: `${metrics?.completion_percentage || 0}%` }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="shadow-2xs">
                <CardContent className="p-8 text-center text-text-secondary">
                  <p className="text-sm mb-3">You haven't enrolled in a roadmap yet.</p>
                  <Button onClick={() => navigate('/learn')} variant="outline" size="sm">Browse Curriculum</Button>
                </CardContent>
              </Card>
            )}
          </section>
        </div>

        {/* Right Sidebar: Key Metrics (Reflows into 3 cols on tablet / 1 col on desktop & mobile) */}
        <div className="space-y-3 min-w-0">
          <h2 className="text-xs font-bold tracking-wider text-text-muted uppercase flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-accent" />
            <span>Progress Snapshot</span>
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-1 gap-4 min-w-0">
            {/* Completion */}
            <Card className="p-5 flex items-center gap-4 hover:border-border-hover transition-colors shadow-2xs">
              <div className="shrink-0">
                <ProgressRing progress={metrics?.completion_percentage || 0} size={52} strokeWidth={5} />
              </div>
              <div className="min-w-0">
                <span className="text-2xl font-bold text-text-primary block leading-none">{Math.round(metrics?.completion_percentage || 0)}%</span>
                <span className="text-xs font-semibold text-text-muted uppercase tracking-wider mt-1 block">Completed</span>
              </div>
            </Card>

            {/* Lessons */}
            <Card className="p-5 flex items-center gap-4 hover:border-border-hover transition-colors shadow-2xs">
              <div className="w-12 h-12 rounded-xl bg-accent-subtle text-accent flex items-center justify-center shrink-0 border border-accent/10">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div className="min-w-0">
                <span className="text-2xl font-bold text-text-primary block leading-none">{metrics?.total_lessons_completed || 0}</span>
                <span className="text-xs font-semibold text-text-muted uppercase tracking-wider mt-1 block">Lessons Mastered</span>
              </div>
            </Card>

            {/* Score */}
            <Card className="p-5 flex items-center gap-4 hover:border-border-hover transition-colors shadow-2xs">
              <div className="w-12 h-12 rounded-xl bg-warning-subtle text-warning flex items-center justify-center shrink-0 border border-warning/10">
                <Trophy className="w-6 h-6" />
              </div>
              <div className="min-w-0">
                <span className="text-2xl font-bold text-text-primary block leading-none">
                  {metrics?.average_score ? `${Math.round(metrics.average_score)}%` : 'N/A'}
                </span>
                <span className="text-xs font-semibold text-text-muted uppercase tracking-wider mt-1 block">Avg Score</span>
              </div>
            </Card>
          </div>
        </div>
        
      </div>
    </div>
  );
}
