import { X, Trophy, CheckCircle2, TrendingUp, Compass, ArrowRight, Zap } from 'lucide-react';
import { Button } from './Button';
import type { ExecutionSubmitResponse } from '../../services/execution';
import { useNavigate } from 'react-router-dom';

interface PostSubmissionModalProps {
  submissionResult: ExecutionSubmitResponse;
  onClose: () => void;
}

export function PostSubmissionModal({ submissionResult, onClose }: PostSubmissionModalProps) {
  const navigate = useNavigate();
  const isAccepted = submissionResult.status === 'accepted';
  const hasAchievements = submissionResult.new_achievements && submissionResult.new_achievements.length > 0;
  const mastery = submissionResult.mastery_update;
  const nextProblem = submissionResult.next_problem;

  if (!isAccepted) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-surface border border-border rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in zoom-in-95 slide-in-from-bottom-4 duration-500">
        <div className="p-8 flex flex-col relative">
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full text-text-muted hover:bg-surface-muted hover:text-text-primary transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-success/10 text-success rounded-full flex items-center justify-center shrink-0">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <div className="text-[10px] font-bold text-success uppercase tracking-widest">
                Status
              </div>
              <h2 className="text-xl font-bold text-text-primary">
                Accepted
              </h2>
            </div>
          </div>
          
          <div className="space-y-4 mb-8">
            {mastery && (
              <div className="flex items-center justify-between p-3 rounded-xl border border-border bg-surface-muted/30">
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-5 h-5 text-accent" />
                  <span className="font-semibold text-sm">{mastery.concept} Mastery</span>
                </div>
                <div className="flex items-center gap-2 font-mono text-sm font-bold">
                  <span className="text-text-secondary">{Math.round(mastery.old_percentage)}%</span>
                  <ArrowRight className="w-4 h-4 text-text-muted" />
                  <span className="text-success">{Math.round(mastery.new_percentage)}%</span>
                </div>
              </div>
            )}
            
            {hasAchievements && submissionResult.new_achievements?.map((achievement, i) => (
              <div key={i} className="flex items-start gap-4 p-4 rounded-xl border border-warning/30 bg-warning/5">
                <Trophy className="w-6 h-6 text-warning shrink-0" />
                <div>
                  <div className="text-[10px] font-bold text-warning uppercase tracking-widest mb-1">
                    Achievement Unlocked
                  </div>
                  <h3 className="font-bold text-sm text-text-primary mb-1">{achievement.name}</h3>
                  <p className="text-xs text-text-secondary">{achievement.description}</p>
                </div>
              </div>
            ))}

            {nextProblem && (
              <div className="p-4 rounded-xl border border-accent/20 bg-accent/5">
                <div className="text-[10px] font-bold text-accent uppercase tracking-widest mb-2 flex items-center gap-1.5">
                  <Compass className="w-3.5 h-3.5" /> Next Best Action
                </div>
                <h3 className="font-bold text-base text-text-primary">{nextProblem.title}</h3>
                <div className="flex items-center gap-2 mt-2 mb-3">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-surface border border-border text-text-secondary">
                    {nextProblem.difficulty}
                  </span>
                </div>
                <div className="flex gap-2 text-xs text-text-secondary bg-surface p-2 rounded border border-border/50">
                  <Zap className="w-3.5 h-3.5 text-warning shrink-0" />
                  <p>{nextProblem.reason}</p>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex gap-3">
            <Button variant="outline" className="flex-1" onClick={onClose}>
              Close
            </Button>
            {nextProblem && nextProblem.exercise_id && (
              <Button 
                variant="primary" 
                className="flex-1" 
                onClick={() => {
                  onClose();
                  navigate(`/workspace/${nextProblem.exercise_id}`);
                }}
              >
                Start Next Problem
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
