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
      <div className="h-96 flex items-center justify-center p-4">
        <div className="flex flex-col items-center gap-4 text-text-secondary">
          <Loader2 className="w-8 h-8 animate-spin text-accent" />
          <p className="font-medium text-sm">Mapping your personalized journey...</p>
        </div>
      </div>
    );
  }

  if (error || !roadmap) {
    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto space-y-6 min-w-0">
        <Card className="border-error-subtle bg-error-subtle/30 shadow-2xs">
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
    <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8 pb-28 animate-fade-in font-sans text-text-primary min-w-0">
      <header className="mb-8 sm:mb-12">
        <Badge variant="outline" className="mb-3 bg-accent-subtle text-accent border-accent/20 text-xs font-semibold">
          <Compass className="w-3.5 h-3.5 mr-1.5" />
          {roadmap.career_goal} Specialization
        </Badge>
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-text-primary tracking-tight">Your DSA Journey</h1>
        <p className="text-text-secondary mt-2 sm:mt-3 text-sm sm:text-base lg:text-lg max-w-2xl leading-relaxed">
          A personalized, strictly sequenced curriculum designed to prepare you for {roadmap.career_goal} interviews and roles.
        </p>
        
        <div className="mt-6 sm:mt-8 flex items-center gap-4 bg-surface p-4 rounded-xl border border-border max-w-xl shadow-2xs">
          <div className="w-full h-2.5 bg-surface-muted rounded-full overflow-hidden shadow-inner flex-1 border border-border/40">
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

      {/* Timeline Section */}
      <div className="space-y-6 sm:space-y-8 relative before:absolute before:inset-0 before:left-[19px] sm:before:left-[27px] md:before:left-[31px] before:w-0.5 before:bg-border before:z-0">
        {roadmap.phases.map((phase, index) => {
          const isCompleted = phase.status === 'COMPLETED';
          const isCurrent = phase.status === 'CURRENT';
          
          return (
            <div key={index} className="relative z-10 flex gap-3 sm:gap-5 md:gap-6 min-w-0">
              {/* Timeline Icon Node */}
              <div className={cn(
                "w-10 h-10 sm:w-14 sm:h-14 md:w-16 md:h-16 shrink-0 rounded-full border-2 sm:border-4 flex items-center justify-center shadow-xs bg-surface transition-colors",
                isCompleted ? "border-success text-success bg-success-subtle/40" : 
                isCurrent ? "border-accent text-accent shadow-accent/20 ring-4 ring-accent/10" : 
                "border-border text-text-muted"
              )}>
                {isCompleted ? <CheckCircle2 className="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7" /> :
                 isCurrent ? <PlayCircle className="w-5 h-5 sm:w-6 sm:h-6 md:w-7 md:h-7 ml-0.5" /> :
                 <Lock className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" />}
              </div>
              
              {/* Phase Card */}
              <Card 
                className={cn(
                  "flex-1 transition-all duration-300 min-w-0 shadow-2xs",
                  isCurrent ? "border-accent/80 shadow-md shadow-accent/5 ring-1 ring-accent/20" : 
                  isCompleted ? "bg-surface/90 border-border" : 
                  "opacity-80 bg-surface-muted/60 border-border/40"
                )}
              >
                <CardContent className="p-4 sm:p-5 md:p-6 min-w-0">
                  <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 min-w-0">
                    <div className="space-y-2 min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-bold text-text-muted uppercase tracking-wider">
                          Phase {index + 1}
                        </span>
                        <h2 className={cn(
                          "text-base sm:text-lg lg:text-xl font-bold tracking-tight",
                          isCurrent ? "text-accent" :
                          isCompleted ? "text-text-primary" : "text-text-secondary"
                        )}>
                          {phase.name}
                        </h2>
                        {isCurrent && (
                          <Badge variant="default" className="bg-accent text-white text-[11px] font-semibold">
                            Current Focus
                          </Badge>
                        )}
                        {isCompleted && (
                          <Badge variant="outline" className="border-success/30 text-success bg-success-subtle text-[11px] font-semibold">
                            Mastered
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-text-secondary leading-relaxed text-xs sm:text-sm">
                        {phase.description}
                      </p>
                    </div>

                    <div className="shrink-0 flex flex-col sm:flex-row lg:flex-col items-start sm:items-center lg:items-end justify-between gap-3 pt-2 lg:pt-0 border-t border-border/40 sm:border-0">
                      <div className="text-xs font-semibold text-text-secondary flex items-center gap-1.5 bg-background px-2.5 py-1.5 rounded-lg border border-border">
                        <BookOpen className="w-3.5 h-3.5 text-text-muted" />
                        <span>{phase.completed_lessons} / {phase.total_lessons} Lessons</span>
                      </div>
                      
                      {isCurrent && (
                        <Button 
                          onClick={() => navigate('/')}
                          size="sm"
                          className="w-full sm:w-auto text-xs font-semibold gap-1.5 shadow-xs"
                        >
                          <span>Continue Learning</span>
                          <ArrowRight className="w-3.5 h-3.5" />
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
