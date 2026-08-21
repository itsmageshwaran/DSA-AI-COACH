import { useState, useEffect } from 'react';
import { Map, BookOpen, ArrowRight, Compass, CheckCircle2, Lock, PlayCircle, Loader2 } from 'lucide-react';
import { learningApi } from '../services/learning';
import type { RoadmapResponse } from '../services/learning';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { cn } from '../lib/utils';
import { useNavigate } from 'react-router-dom';

export function LearningPathPage() {
  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadRoadmap() {
      try {
        const data = await learningApi.getRoadmap();
        setRoadmap(data);
      } catch (err: any) {
        setError('Failed to load personalized roadmap.');
      } finally {
        setIsLoading(false);
      }
    }
    loadRoadmap();
  }, []);

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-text-secondary">
          <Loader2 className="w-8 h-8 animate-spin text-accent" />
          <p className="font-medium">Mapping your personalized journey...</p>
        </div>
      </div>
    );
  }

  if (error || !roadmap) {
    return (
      <div className="p-4 lg:p-8 max-w-5xl mx-auto space-y-6">
        <Card className="border-error-subtle bg-error-subtle/30">
          <EmptyState
            icon={Map}
            title="Roadmap Unavailable"
            description={error || "Could not fetch your roadmap."}
          />
        </Card>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-8 max-w-5xl mx-auto pb-24 animate-fade-in">
      <header className="mb-12">
        <Badge variant="outline" className="mb-3 bg-accent/5 text-accent border-accent/20">
          <Compass className="w-3 h-3 mr-1.5" />
          {roadmap.career_goal} Specialization
        </Badge>
        <h1 className="text-3xl lg:text-4xl font-bold text-text-primary tracking-tight">Your DSA Journey</h1>
        <p className="text-text-secondary mt-3 text-lg max-w-2xl">
          A personalized, strictly sequenced curriculum designed to prepare you for {roadmap.career_goal} interviews and roles.
        </p>
        
        <div className="mt-8 flex items-center gap-4 bg-surface p-4 rounded-xl border border-border/50 max-w-xl">
          <div className="w-full h-2.5 bg-background rounded-full overflow-hidden shadow-inner flex-1">
            <div 
              className="h-full bg-success rounded-full transition-all duration-1000"
              style={{ width: `${roadmap.overall_progress}%` }}
            ></div>
          </div>
          <span className="text-sm font-bold text-text-primary w-12 text-right">
            {Math.round(roadmap.overall_progress)}%
          </span>
        </div>
      </header>

      <div className="space-y-6 relative before:absolute before:inset-0 before:ml-[27px] md:before:ml-[39px] before:-translate-x-px md:before:translate-x-0 before:w-0.5 before:bg-border/50 before:z-0">
        {roadmap.phases.map((phase, index) => {
          const isCompleted = phase.status === 'COMPLETED';
          const isCurrent = phase.status === 'CURRENT';
          
          return (
            <div key={index} className="relative z-10 flex gap-4 md:gap-6">
              <div className={cn(
                "w-14 h-14 md:w-20 md:h-20 shrink-0 rounded-full border-4 flex items-center justify-center shadow-sm bg-surface transition-colors",
                isCompleted ? "border-success text-success" : 
                isCurrent ? "border-accent text-accent shadow-accent/20" : 
                "border-border text-text-muted"
              )}>
                {isCompleted ? <CheckCircle2 className="w-6 h-6 md:w-8 md:h-8" /> :
                 isCurrent ? <PlayCircle className="w-6 h-6 md:w-8 md:h-8 ml-1" /> :
                 <Lock className="w-6 h-6 md:w-8 md:h-8" />}
              </div>
              
              <Card 
                className={cn(
                  "flex-1 transition-all duration-300 relative",
                  isCurrent ? "border-accent shadow-md shadow-accent/5 ring-1 ring-accent/10" : 
                  isCompleted ? "bg-surface/50 border-border" : 
                  "opacity-75 bg-surface-muted/50 border-transparent shadow-none"
                )}
              >
                <CardContent className="p-5 md:p-6">
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center gap-3">
                        <span className="text-sm font-bold text-text-muted uppercase tracking-wider">
                          Phase {index + 1}
                        </span>
                        <h2 className={cn(
                          "text-xl font-bold tracking-tight",
                          isCurrent ? "text-accent" :
                          isCompleted ? "text-text-primary" : "text-text-secondary"
                        )}>
                          {phase.name}
                        </h2>
                        {isCurrent && (
                          <Badge variant="default" className="bg-accent text-accent-fg">
                            Current Focus
                          </Badge>
                        )}
                        {isCompleted && (
                          <Badge variant="outline" className="border-success text-success bg-success/5">
                            Mastered
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-text-secondary leading-relaxed max-w-2xl text-sm md:text-base">
                        {phase.description}
                      </p>
                    </div>

                    <div className="shrink-0 flex flex-col items-start md:items-end gap-3 pt-2 md:pt-0">
                      <div className="text-sm font-medium text-text-secondary flex items-center gap-1.5 bg-background px-3 py-1.5 rounded-md border border-border/50">
                        <BookOpen className="w-4 h-4 text-text-muted" />
                        {phase.completed_lessons} / {phase.total_lessons} Lessons
                      </div>
                      
                      {isCurrent && (
                        <Button 
                          onClick={() => navigate('/dashboard')}
                          size="sm"
                          className="w-full md:w-auto"
                        >
                          Continue Learning
                          <ArrowRight className="w-4 h-4 ml-1.5" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          );
        })}
      </div>
    </div>
  );
}
