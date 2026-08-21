import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BrainCircuit } from 'lucide-react';
import { useAuth } from '../features/auth/AuthContext';
import { ThemeToggle } from '../components/ui/ThemeToggle';

export function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password);
      }
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4 relative font-sans text-text-primary">
      {/* Top right theme toggle */}
      <div className="absolute top-6 right-6">
        <ThemeToggle size="sm" />
      </div>

      <div className="bg-surface border border-border rounded-2xl shadow-soft w-full max-w-md p-8 transition-colors">
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 bg-ai-light rounded-xl flex items-center justify-center mb-4 text-accent shadow-xs border border-ai/10">
            <BrainCircuit className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">
            {isLogin ? 'Welcome back' : 'Create an account'}
          </h1>
          <p className="text-text-secondary mt-2 text-sm text-center">
            {isLogin 
              ? 'Enter your credentials to access your AI Coach.' 
              : 'Join the DSA AI Coach and master algorithms.'}
          </p>
        </div>

        {error && (
          <div className="mb-6 p-3 bg-error-subtle border border-error/20 text-error rounded-lg text-sm text-center font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-1">Email</label>
            <input 
              id="email"
              type="email" 
              required
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
              placeholder="student@example.com"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-1">Password</label>
            <input 
              id="password"
              type="password" 
              required
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
              placeholder="••••••••"
            />
          </div>
          
          <button 
            type="submit" 
            disabled={isSubmitting}
            className="w-full bg-primary hover:bg-primary-hover text-text-inverse py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2 shadow-xs cursor-pointer"
          >
            {isSubmitting ? 'Please wait...' : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-text-secondary">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button 
            onClick={() => setIsLogin(!isLogin)}
            className="text-accent hover:underline font-semibold focus:outline-none cursor-pointer"
          >
            {isLogin ? 'Sign up' : 'Sign in'}
          </button>
        </div>
      </div>
    </div>
  );
}
