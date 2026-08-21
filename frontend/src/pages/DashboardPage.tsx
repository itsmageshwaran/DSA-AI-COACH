import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { learningApi } from '../services/learning';
import type { ProgressSummary, RecommendationResponse, LearningPath } from '../services/learning';
import { useAuth } from '../features/auth/AuthContext';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { ProgressRing } from '../components/ui/ProgressRing';
import { Play, CheckCircle2, TrendingUp, Compass, Code, LayoutDashboard, Target, Zap } from 'lucide-react';
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
      <div className="p-4 lg:p-8 max-w-6xl mx-auto space-y-8">
        <Skeleton className="h-32 w-full rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton className="h-40 rounded-xl lg:col-span-2" />
          <Skeleton className="h-40 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-8 max-w-5xl mx-auto space-y-10 pb-20">
      
      {/* Header / Greeting */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-accent/10 text-accent text-sm font-semibold tracking-wide">
              <Target className="w-4 h-4" />
              {careerGoal || "DSA Mastery"}
            </span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-text-primary">
            Good morning, {firstName}.
          </h1>
          <p className="text-text-secondary mt-1 text-lg">
            {recommendation 
              ? `You're currently mastering ${recommendation.topic}.` 
              : "Ready to master Data Structures and Algorithms?"}
          </p>
        </div>
        <div>
          <Button size="lg" onClick={() => navigate(recommendation ? `/workspace/${recommendation.exercise_id}` : '/learn')}>
            <Play className="w-4 h-4 mr-2 fill-current" />
            {recommendation ? "Continue Learning" : "Start Learning Path"}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-8">
          <section>
            <h2 className="text-sm font-semibold tracking-wider text-text-muted uppercase mb-4 flex items-center gap-2">
              <Compass className="w-4 h-4" />
              Next Best Action
            </h2>
            
            {recommendation ? (
              <Card className="hover:shadow-sm transition-shadow border-l-4 border-l-accent overflow-hidden">
                <CardContent className="p-6">
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-accent uppercase tracking-wider">{recommendation.topic}</span>
                      <span className={cn(
                        "px-2 py-1 rounded text-xs font-semibold border",
                        recommendation.difficulty.toLowerCase().includes('easy') ? "bg-success/10 text-success border-success/20" :
                        recommendation.difficulty.toLowerCase().includes('medium') ? "bg-warning/10 text-warning border-warning/20" :
                        recommendation.difficulty.toLowerCase().includes('hard') ? "bg-error/10 text-error border-error/20" :
                        "bg-surface-muted text-text-secondary border-border"
                      )}>
                        Difficulty: {recommendation.difficulty}
                      </span>
                    </div>
                    
                    <div className="flex flex-col md:flex-row gap-6 items-start md:items-center">
                      <div className="bg-accent-subtle p-4 rounded-xl shrink-0">
                        <Code className="w-6 h-6 text-accent" />
                      </div>
                      <div className="flex-1 space-y-1">
                        <h3 className="text-xl font-bold text-text-primary">{recommendation.title}</h3>
                        <div className="flex items-start gap-2 text-sm text-text-secondary mt-2 bg-surface-muted p-3 rounded-lg">
                          <Zap className="w-4 h-4 shrink-0 text-warning mt-0.5" />
                          <p><strong>Why this problem:</strong> {recommendation.reason}</p>
                        </div>
                      </div>
                      <Button onClick={() => navigate(`/workspace/${recommendation.exercise_id}`)} variant="primary" className="w-full md:w-auto shrink-0 mt-4 md:mt-0">
                        Start Problem
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="p-8 text-center">
                  <div className="w-12 h-12 rounded-full bg-surface-muted flex items-center justify-center mx-auto mb-4">
                    <CheckCircle2 className="w-6 h-6 text-text-muted" />
                  </div>
                  <h3 className="text-lg font-bold text-text-primary mb-2">You're all caught up!</h3>
                  <p className="text-text-secondary mb-6">Browse the problem library to find more challenges.</p>
                  <Button onClick={() => navigate('/problems')} variant="outline">Browse Problems</Button>
                </CardContent>
              </Card>
            )}
          </section>

          <section>
            <h2 className="text-sm font-semibold tracking-wider text-text-muted uppercase mb-4 flex items-center gap-2">
              <LayoutDashboard className="w-4 h-4" />
              Roadmap Progress
            </h2>
            <Card>
               <CardContent className="p-6">
                 {path ? (
                   <div className="flex items-center justify-between">
                     <div>
                       <h3 className="font-bold text-text-primary">{path.title}</h3>
                       <p className="text-sm text-text-secondary">{path.description}</p>
                     </div>
                     <Button onClick={() => navigate('/learn')} variant="ghost">View Details</Button>
                   </div>
                 ) : (
                   <div className="text-center py-4">
                     <p className="text-text-secondary mb-4">You haven't enrolled in a roadmap yet.</p>
                     <Button onClick={() => navigate('/learn')} variant="outline">Browse Curriculum</Button>
                   </div>
                 )}
               </CardContent>
            </Card>
          </section>
        </div>

        {/* Sidebar / Progress */}
        <div className="space-y-8">
          <section>
            <h2 className="text-sm font-semibold tracking-wider text-text-muted uppercase mb-4 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Progress
            </h2>
            
            <div className="flex flex-col gap-4">
              <Card>
                <CardContent className="p-5 flex items-center gap-4">
                  <ProgressRing progress={metrics?.completion_percentage || 0} size={56} strokeWidth={5} colorClass="text-success" />
                  <div>
                    <p className="text-xl font-bold text-text-primary">
                      {metrics?.completion_percentage ? metrics.completion_percentage.toFixed(1) : '0'}%
                    </p>
                    <p className="text-xs text-text-secondary font-medium uppercase tracking-wide">Completed</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-5 flex items-center gap-4">
                  <div className="w-14 h-14 rounded-full bg-ai-light flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-6 h-6 text-ai" />
                  </div>
                  <div>
                    <p className="text-xl font-bold text-text-primary">{metrics?.total_lessons_completed || 0}</p>
                    <p className="text-xs text-text-secondary font-medium uppercase tracking-wide">Lessons Mastered</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-5 flex items-center gap-4">
                  <div className="w-14 h-14 rounded-full bg-warning-subtle flex items-center justify-center shrink-0">
                    <span className="text-xl font-bold text-warning">{metrics?.average_score ? Math.round(metrics.average_score) : '-'}</span>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-text-primary">{metrics?.average_score ? `${metrics.average_score.toFixed(1)}%` : 'N/A'}</p>
                    <p className="text-xs text-text-secondary font-medium uppercase tracking-wide">Avg Score</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
