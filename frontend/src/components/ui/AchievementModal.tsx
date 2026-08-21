import { X, Trophy, Star, ArrowUpCircle } from 'lucide-react';
import { Button } from './Button';
import type { AchievementResponse } from '../../services/learning';

interface AchievementModalProps {
  achievement: AchievementResponse;
  onClose: () => void;
}

export function AchievementModal({ achievement, onClose }: AchievementModalProps) {
  // Map icon names to lucide icons
  const getIcon = (name: string) => {
    switch (name) {
      case 'trophy': return <Trophy className="w-12 h-12 text-accent" />;
      case 'star': return <Star className="w-12 h-12 text-accent" />;
      case 'arrow-up-circle': return <ArrowUpCircle className="w-12 h-12 text-accent" />;
      default: return <Trophy className="w-12 h-12 text-accent" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-surface border border-border rounded-2xl shadow-xl w-full max-w-sm overflow-hidden animate-in zoom-in-95 slide-in-from-bottom-4 duration-500">
        <div className="p-8 flex flex-col items-center text-center relative">
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full text-text-muted hover:bg-surface-muted hover:text-text-primary transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="text-[10px] font-bold text-accent uppercase tracking-widest mb-6">
            Achievement Unlocked
          </div>
          
          <div className="w-24 h-24 bg-accent/10 rounded-full flex items-center justify-center mb-6 relative">
            {getIcon(achievement.icon_name)}
            <div className="absolute inset-0 rounded-full border-2 border-accent/20 animate-ping opacity-20"></div>
          </div>
          
          <h2 className="text-2xl font-bold text-text-primary mb-2">
            {achievement.name}
          </h2>
          
          <p className="text-text-secondary mb-8">
            {achievement.description}
          </p>
          
          <Button variant="primary" className="w-full" onClick={onClose}>
            Continue
          </Button>
        </div>
      </div>
    </div>
  );
}
