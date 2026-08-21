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
        if (err.message.includes('BACKEND_MISSING')) {
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
    if (d.includes('easy')) return "bg-success/10 text-success border-success/20";
    if (d.includes('medium')) return "bg-warning/10 text-warning border-warning/20";
    if (d.includes('hard')) return "bg-error/10 text-error border-error/20";
    return "bg-accent/10 text-accent border-accent/20";
  };

  return (
    <div className="p-4 lg:p-8 max-w-7xl mx-auto flex flex-col h-[calc(100vh-4rem)] pb-20 animate-fade-in">
      <header className="mb-8 shrink-0">
        <h1 className="text-3xl lg:text-4xl font-bold text-text-primary tracking-tight">Problem Library</h1>
        <p className="text-text-secondary mt-3 text-lg max-w-2xl">
          Practice your algorithm skills with our curated collection of coding challenges.
        </p>
      </header>

      <div className="flex flex-col sm:flex-row gap-4 mb-8 shrink-0">
        <div className="relative flex-1 max-w-md">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <Input 
            type="text" 
            placeholder="Search problems by name or concept..." 
            className="pl-10 h-11"
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
              "px-6 py-4 text-sm font-semibold border-b-2 transition-all whitespace-nowrap flex items-center gap-2",
              activeTab === tab.id 
                ? "border-primary text-primary" 
                : "border-transparent text-text-secondary hover:text-text-primary hover:border-border-hover"
            )}
          >
            {tab.label}
            <span className={cn(
              "text-xs px-2 py-0.5 rounded-full",
              activeTab === tab.id ? "bg-primary-subtle text-primary" : "bg-surface-muted text-text-muted"
            )}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-auto pr-1 lg:pr-4 custom-scrollbar">
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map(i => (
              <Skeleton key={i} className="h-24 w-full rounded-xl" />
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
          <Card>
            <EmptyState
              icon={Search}
              title="No problems found"
              description={searchQuery ? "Try adjusting your search terms." : "Check back later for new problems."}
            />
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredExercises.map((exercise) => (
              <Card 
                key={exercise.id} 
                className={cn(
                  "group hover:border-accent/50 hover:shadow-sm transition-all duration-300",
                  exercise.is_completed ? "bg-surface-muted/30 border-border/50" : ""
                )}
              >
                <CardContent className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className={cn(
                      "w-10 h-10 rounded-lg flex items-center justify-center shrink-0 mt-0.5",
                      exercise.is_completed 
                        ? "bg-success/10 text-success" 
                        : "bg-surface-muted text-text-muted group-hover:bg-accent-subtle group-hover:text-accent transition-colors"
                    )}>
                      {exercise.is_completed ? <CheckCircle2 className="w-5 h-5" /> : <Code2 className="w-5 h-5" />}
                    </div>
                    <div>
                      <h3 className={cn(
                        "text-lg font-bold tracking-tight mb-1",
                        exercise.is_completed ? "text-text-secondary" : "text-text-primary group-hover:text-accent transition-colors"
                      )}>
                        {exercise.title}
                      </h3>
                      <div className="flex items-center gap-2 mt-2">
                        {exercise.difficulty && (
                          <Badge variant="outline" className={cn("text-xs font-semibold uppercase tracking-wider", getDifficultyColor(exercise.difficulty))}>
                            {exercise.difficulty}
                          </Badge>
                        )}
                        {exercise.concept_name && (
                          <span className="text-sm font-medium text-text-secondary">
                            {exercise.concept_name}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="shrink-0 flex items-center sm:pl-4">
                    <Button 
                      onClick={() => navigate(`/workspace/${exercise.id}`)}
                      variant={exercise.is_completed ? "secondary" : "primary"}
                      className="w-full sm:w-auto"
                    >
                      {exercise.is_completed ? "Review Code" : "Solve Challenge"}
                      <Play className="w-4 h-4 ml-2 fill-current" />
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
