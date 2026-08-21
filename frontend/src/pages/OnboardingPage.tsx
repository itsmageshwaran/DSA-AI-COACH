import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthContext';
import { Button } from '../components/ui/Button';
import { Loader2, ArrowRight } from 'lucide-react';
import { cn } from '../lib/utils';

const CAREER_GOALS = [
  "Backend Engineering",
  "Frontend Engineering",
  "Full Stack Engineering",
  "Data Science",
  "Machine Learning / AI",
  "Cybersecurity"
];

const EXPERIENCE_LEVELS = [
  "Beginner",
  "Intermediate",
  "Advanced"
];

const LANGUAGES = [
  "python",
  "java",
  "cpp",
  "javascript",
  "go"
];

export function OnboardingPage() {
  const { updateProfile } = useAuth();
  const navigate = useNavigate();
  
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    career_goal: '',
    experience_level: '',
    preferred_language: 'python'
  });

  const handleNext = () => {
    if (step === 1 && !formData.career_goal) return;
    if (step === 2 && !formData.experience_level) return;
    setStep(s => s + 1);
  };

  const handleSubmit = async () => {
    if (!formData.preferred_language) return;
    
    setIsLoading(true);
    setError(null);
    try {
      await updateProfile(formData);
      navigate('/');
    } catch (err: any) {
      setError(err.message || "Failed to save profile.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="max-w-xl w-full">
        {/* Progress */}
        <div className="flex gap-2 mb-12">
          {[1, 2, 3].map(i => (
            <div 
              key={i} 
              className={cn(
                "h-1.5 flex-1 rounded-full transition-colors duration-500",
                step >= i ? "bg-accent" : "bg-surface-muted"
              )} 
            />
          ))}
        </div>

        {/* Content */}
        <div className="bg-surface border border-border p-8 rounded-2xl shadow-sm">
          {error && (
            <div className="mb-6 p-4 bg-error/10 border border-error/20 rounded-lg text-error text-sm font-semibold">
              {error}
            </div>
          )}

          {step === 1 && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h1 className="text-3xl font-bold text-text-primary mb-2">Let's build your DSA roadmap.</h1>
              <p className="text-text-secondary text-lg mb-8">
                Tell us where you're heading, and we'll adapt the journey around that goal.
              </p>
              
              <div className="space-y-3">
                <label className="text-sm font-bold text-text-muted uppercase tracking-wider">Which field are you preparing for?</label>
                <div className="grid gap-3 sm:grid-cols-2">
                  {CAREER_GOALS.map(goal => (
                    <button
                      key={goal}
                      onClick={() => setFormData(prev => ({ ...prev, career_goal: goal }))}
                      className={cn(
                        "p-4 rounded-xl border text-left font-semibold transition-all duration-200",
                        formData.career_goal === goal 
                          ? "border-accent bg-accent/5 text-accent" 
                          : "border-border bg-background text-text-secondary hover:border-text-muted hover:text-text-primary"
                      )}
                    >
                      {goal}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h1 className="text-3xl font-bold text-text-primary mb-2">What's your current level?</h1>
              <p className="text-text-secondary text-lg mb-8">
                We'll start your roadmap at the right difficulty.
              </p>
              
              <div className="space-y-3">
                <label className="text-sm font-bold text-text-muted uppercase tracking-wider">Experience Level</label>
                <div className="grid gap-3">
                  {EXPERIENCE_LEVELS.map(level => (
                    <button
                      key={level}
                      onClick={() => setFormData(prev => ({ ...prev, experience_level: level }))}
                      className={cn(
                        "p-4 rounded-xl border text-left font-semibold transition-all duration-200",
                        formData.experience_level === level 
                          ? "border-accent bg-accent/5 text-accent" 
                          : "border-border bg-background text-text-secondary hover:border-text-muted hover:text-text-primary"
                      )}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h1 className="text-3xl font-bold text-text-primary mb-2">One last thing.</h1>
              <p className="text-text-secondary text-lg mb-8">
                Which programming language will you be coding in?
              </p>
              
              <div className="space-y-3">
                <label className="text-sm font-bold text-text-muted uppercase tracking-wider">Preferred Language</label>
                <div className="grid gap-3 sm:grid-cols-2">
                  {LANGUAGES.map(lang => (
                    <button
                      key={lang}
                      onClick={() => setFormData(prev => ({ ...prev, preferred_language: lang }))}
                      className={cn(
                        "p-4 rounded-xl border text-left font-semibold capitalize transition-all duration-200",
                        formData.preferred_language === lang 
                          ? "border-accent bg-accent/5 text-accent" 
                          : "border-border bg-background text-text-secondary hover:border-text-muted hover:text-text-primary"
                      )}
                    >
                      {lang === 'cpp' ? 'C++' : lang}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Footer Actions */}
          <div className="mt-10 flex justify-between items-center">
            {step > 1 ? (
              <Button variant="ghost" onClick={() => setStep(s => s - 1)}>
                Back
              </Button>
            ) : <div />}
            
            {step < 3 ? (
              <Button 
                variant="primary" 
                onClick={handleNext}
                disabled={
                  (step === 1 && !formData.career_goal) ||
                  (step === 2 && !formData.experience_level)
                }
                className="gap-2"
              >
                Continue <ArrowRight className="w-4 h-4" />
              </Button>
            ) : (
              <Button 
                variant="primary" 
                onClick={handleSubmit}
                disabled={isLoading || !formData.preferred_language}
                className="gap-2"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>Complete Setup <ArrowRight className="w-4 h-4" /></>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
