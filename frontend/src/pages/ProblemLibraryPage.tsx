import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Play, Code2, CheckCircle2 } from 'lucide-react';
import { learningApi } from '../services/learning';
import type { Exercise } from '../services/learning';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { cn } from '../lib/utils';

export function ProblemLibraryPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'all' | 'todo' | 'completed'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadExercises() {
      try {
        const data = await learningApi.getExercises();
        setExercises(data);
      } catch (err: any) {
        if (err.message?.includes('BACKEND_MISSING')) {
          setError(err.message);
        } else {
          setError('Failed to load exercises.');
        }
      } finally {
        setIsLoading(false);
      }
    }
    loadExercises();
  }, []);

  const filteredExercises = exercises.filter(ex => {
    const matchesSearch = ex.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          (ex.concept_name && ex.concept_name.toLowerCase().includes(searchQuery.toLowerCase()));
    
    if (activeTab === 'completed') return matchesSearch && ex.is_completed;
    if (activeTab === 'todo') return matchesSearch && !ex.is_completed;
    return matchesSearch;
  });

  const getDifficultyColor = (diff: string | undefined) => {
    if (!diff) return "bg-surface-muted text-text-secondary border-border";
    const d = diff.toLowerCase();
    if (d.includes('easy')) return "bg-success-subtle text-success border-success/25";
    if (d.includes('medium')) return "bg-warning-subtle text-warning border-warning/25";
    if (d.includes('hard')) return "bg-error-subtle text-error border-error/25";
    return "bg-accent-subtle text-accent border-accent/25";
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 flex flex-col min-w-0 pb-24 animate-fade-in font-sans text-text-primary">
      <header className="mb-6 sm:mb-8 shrink-0">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-text-primary tracking-tight">Problem Library</h1>
        <p className="text-text-secondary mt-2 text-sm sm:text-base max-w-2xl">
          Practice your algorithm skills with our curated collection of coding challenges.
        </p>
      </header>

      <div className="flex flex-col sm:flex-row gap-4 mb-6 shrink-0">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 sm:w-5 sm:h-5 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
          <Input 
            type="text" 
            placeholder="Search problems by name or concept..." 
            className="pl-10 h-10 sm:h-11 text-xs sm:text-sm bg-surface"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="flex border-b border-border mb-6 shrink-0 overflow-x-auto no-scrollbar">
        {[
          { id: 'all', label: 'All Problems', count: exercises.length },
          { id: 'todo', label: 'To Do', count: exercises.filter(e => !e.is_completed).length },
          { id: 'completed', label: 'Completed', count: exercises.filter(e => e.is_completed).length }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={cn(
              "px-4 sm:px-6 py-3 text-xs sm:text-sm font-semibold border-b-2 transition-all whitespace-nowrap flex items-center gap-2 cursor-pointer",
              activeTab === tab.id 
                ? "border-primary text-primary" 
                : "border-transparent text-text-secondary hover:text-text-primary hover:border-border-hover"
            )}
          >
            {tab.label}
            <span className={cn(
              "text-[11px] px-2 py-0.5 rounded-full font-bold",
              activeTab === tab.id ? "bg-accent-subtle text-accent" : "bg-surface-muted text-text-muted"
            )}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      <div className="space-y-3 min-w-0">
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(i => (
              <Skeleton key={i} className="h-20 w-full rounded-xl" />
            ))}
          </div>
        ) : error ? (
          <Card className="border-error-subtle bg-error-subtle/30">
            <EmptyState
              icon={Code2}
              title="Problems Unavailable"
              description={error}
            />
          </Card>
        ) : filteredExercises.length === 0 ? (
          <div className="py-12">
            <EmptyState
              icon={Code2}
              title="No problems found"
              description={searchQuery ? "No matching problems found for your search query." : "No problems currently in this category."}
            />
          </div>
        ) : (
          <div className="space-y-3 min-w-0">
            {filteredExercises.map(exercise => (
              <Card 
                key={exercise.id} 
                className="hover:border-border-hover transition-all duration-200 cursor-pointer shadow-2xs group min-w-0"
                onClick={() => navigate(`/workspace/${exercise.id}`)}
              >
                <CardContent className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 min-w-0">
                  <div className="flex items-start gap-3.5 min-w-0 flex-1">
                    <div className={cn(
                      "w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5 transition-colors",
                      exercise.is_completed 
                        ? "bg-success-subtle text-success" 
                        : "bg-surface-muted text-text-muted group-hover:text-text-primary"
                    )}>
                      {exercise.is_completed ? (
                        <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5" />
                      ) : (
                        <div className="w-2.5 h-2.5 rounded-full border-2 border-current"></div>
                      )}
                    </div>
                    
                    <div className="space-y-1 min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="font-bold text-sm sm:text-base text-text-primary group-hover:text-accent transition-colors truncate">
                          {exercise.title}
                        </h2>
                        <Badge 
                          variant="outline" 
                          className={cn("text-[11px] font-semibold capitalize shrink-0", getDifficultyColor(exercise.difficulty))}
                        >
                          {exercise.difficulty || 'Easy'}
                        </Badge>
                      </div>
                      
                      {exercise.concept_name && (
                        <p className="text-xs text-text-muted font-medium truncate">
                          Topic: {exercise.concept_name}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-3 shrink-0 pt-2 sm:pt-0 border-t border-border/40 sm:border-0">
                    <span className="text-xs font-semibold text-text-muted sm:hidden">
                      {exercise.is_completed ? 'Completed' : 'To Do'}
                    </span>
                    <Button 
                      size="sm" 
                      variant={exercise.is_completed ? "secondary" : "primary"}
                      className="gap-1.5 text-xs font-semibold"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>{exercise.is_completed ? 'Review' : 'Solve'}</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
