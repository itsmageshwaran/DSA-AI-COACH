import { useState, useEffect } from 'react';
import { Target, TrendingUp, Brain, Loader2, Trophy, Star } from 'lucide-react';
import { learningApi } from '../services/learning';
import type { ConceptMasteryResponse, ProgressSummary, AchievementResponse, LearningPath } from '../services/learning';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../features/auth/AuthContext';

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
      <div className="h-full flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-text-secondary">
          <Loader2 className="w-8 h-8 animate-spin text-accent" />
          <p className="font-medium">Loading your progress...</p>
        </div>
      </div>
    );
  }

  const overallMastery = concepts.length > 0
    ? Math.round(concepts.reduce((acc, curr) => acc + curr.mastery_percentage, 0) / concepts.length)
    : 0;

  const careerGoal = user?.profile?.career_goal || "DSA Mastery";

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <Badge variant="outline" className="mb-2 bg-accent/5 text-accent border-accent/20">
            <Target className="w-3 h-3 mr-1" />
            {careerGoal} Track
          </Badge>
          <h1 className="text-3xl font-bold text-text-primary tracking-tight">Progress Intelligence</h1>
          <p className="text-text-secondary mt-2 text-lg max-w-2xl">
            Track your algorithmic mastery, review your performance metrics, and see how you are improving over time.
          </p>
        </div>
        
        {path && (
          <div className="flex flex-col items-end">
            <span className="text-sm font-medium text-text-secondary mb-1">Roadmap Completion</span>
            <div className="flex items-center gap-3">
              <div className="w-48 h-2.5 bg-background rounded-full overflow-hidden shadow-inner border border-border/50">
                <div 
                  className="h-full bg-success rounded-full transition-all duration-1000"
                  style={{ width: `${summary?.completion_percentage || 0}%` }}
                ></div>
              </div>
              <span className="text-lg font-bold text-text-primary w-12 text-right">
                {summary?.completion_percentage || 0}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6 flex flex-col items-center text-center">
          <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center mb-4">
            <Target className="w-6 h-6 text-accent" />
          </div>
          <h3 className="text-3xl font-bold text-text-primary mb-1">{summary?.total_lessons_completed || 0}</h3>
          <p className="text-text-secondary font-medium text-sm">Problems Solved</p>
        </Card>

        <Card className="p-6 flex flex-col items-center text-center">
          <div className="w-12 h-12 bg-success/10 rounded-xl flex items-center justify-center mb-4">
            <Trophy className="w-6 h-6 text-success" />
          </div>
          <h3 className="text-3xl font-bold text-text-primary mb-1">{achievements.length}</h3>
          <p className="text-text-secondary font-medium text-sm">Achievements Earned</p>
        </Card>

        <Card className="p-6 flex flex-col items-center text-center">
          <div className="w-12 h-12 bg-warning/10 rounded-xl flex items-center justify-center mb-4">
            <TrendingUp className="w-6 h-6 text-warning" />
          </div>
          <h3 className="text-3xl font-bold text-text-primary mb-1">{summary?.average_score ? Math.round(summary.average_score) : 0}%</h3>
          <p className="text-text-secondary font-medium text-sm">Average Score</p>
        </Card>

        <Card className="p-6 flex flex-col items-center text-center bg-gradient-to-b from-surface to-accent/5 border-accent/20">
          <div className="w-12 h-12 bg-accent/20 rounded-xl flex items-center justify-center mb-4 shadow-sm">
            <Brain className="w-6 h-6 text-accent" />
          </div>
          <h3 className="text-3xl font-bold text-accent mb-1">{overallMastery}%</h3>
          <p className="text-text-secondary font-medium text-sm">Overall Mastery</p>
        </Card>
      </div>

      {/* Concept Mastery Radar / List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Col: Concept Mastery List */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-text-primary flex items-center gap-2">
              <Brain className="w-5 h-5 text-accent" />
              Concept Mastery
            </h2>
            <Badge variant="outline" className="text-xs">Based on problem-solving</Badge>
          </div>
          
          <Card className="divide-y divide-border/50">
            {concepts.length > 0 ? (
              concepts.map((concept, idx) => (
                <div key={idx} className="p-5 flex items-center justify-between hover:bg-surface-hover/50 transition-colors">
                  <div className="flex flex-col gap-1">
                    <span className="font-bold text-text-primary text-base">{concept.concept_name}</span>
                    <span className="text-sm font-medium text-text-secondary flex items-center gap-2">
                      Mastery Level
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-32 h-2.5 bg-background rounded-full overflow-hidden shadow-inner">
                      <div 
                        className="h-full bg-accent rounded-full transition-all duration-1000"
                        style={{ width: `${concept.mastery_percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-bold text-text-primary w-10 text-right">
                      {Math.round(concept.mastery_percentage)}%
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-12 text-center text-text-secondary">
                <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-semibold text-text-primary mb-2">No Mastery Data Yet</h3>
                <p>Complete exercises and lessons to build your concept mastery profile.</p>
              </div>
            )}
          </Card>
        </div>

        {/* Right Col: Insights */}
        <div className="space-y-6">
          <h2 className="text-xl font-bold text-text-primary">Insights</h2>
          
          <Card className="p-5 space-y-4">
            <h3 className="font-bold text-text-primary flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-success" />
              Strengths
            </h3>
            {concepts.filter(c => c.mastery_percentage >= 80).length > 0 ? (
              <ul className="space-y-3">
                {concepts.filter(c => c.mastery_percentage >= 80).map((c, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-success rounded-full"></div>
                    <span className="text-sm font-medium text-text-secondary">{c.concept_name}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-text-muted">Keep practicing to build your strengths.</p>
            )}
          </Card>

          <Card className="p-5 space-y-4">
            <h3 className="font-bold text-text-primary flex items-center gap-2">
              <Target className="w-4 h-4 text-warning" />
              Focus Areas
            </h3>
            {concepts.filter(c => c.mastery_percentage > 0 && c.mastery_percentage < 80).length > 0 ? (
              <ul className="space-y-3">
                {concepts.filter(c => c.mastery_percentage > 0 && c.mastery_percentage < 80).map((c, i) => (
                  <li key={i} className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-warning rounded-full"></div>
                    <span className="text-sm font-medium text-text-secondary">{c.concept_name}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-text-muted">Start solving problems to identify areas for improvement.</p>
            )}
          </Card>
        </div>
        
      </div>

      {/* Achievements Section */}
      <div className="space-y-6 pt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-text-primary flex items-center gap-2">
            <Trophy className="w-5 h-5 text-accent" />
            Achievements & Milestones
          </h2>
        </div>
        
        {achievements.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.map((achievement, idx) => (
              <Card key={idx} className="p-5 flex items-start gap-4 hover:border-accent/30 transition-colors">
                <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center shrink-0">
                  <Star className="w-6 h-6 text-accent" />
                </div>
                <div>
                  <h4 className="font-bold text-text-primary mb-1">{achievement.name}</h4>
                  <p className="text-sm text-text-secondary leading-relaxed mb-2">
                    {achievement.description}
                  </p>
                  <span className="text-xs font-medium text-text-muted">
                    Earned on {new Date(achievement.earned_at).toLocaleDateString()}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="p-12 text-center text-text-secondary">
            <Trophy className="w-12 h-12 mx-auto mb-4 opacity-30" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">No Achievements Yet</h3>
            <p>Keep practicing and completing lessons to unlock special achievements!</p>
          </Card>
        )}
      </div>

    </div>
  );
}
