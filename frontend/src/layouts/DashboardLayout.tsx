import { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  BookOpen, 
  Code2, 
  BrainCircuit, 
  TrendingUp, 
  Search, 
  Bell, 
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useAuth } from '../features/auth/AuthContext';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { ThemeToggle } from '../components/ui/ThemeToggle';

const NAVIGATION = [
  { name: 'Home', to: '/', icon: LayoutDashboard },
  { name: 'My Roadmap', to: '/learn', icon: BookOpen },
  { name: 'Problems', to: '/problems', icon: Code2 },
  { name: 'Progress', to: '/progress', icon: TrendingUp },
  { name: 'AI Coach', to: '/coach', icon: BrainCircuit },
];

export function DashboardLayout() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Close mobile menu on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Prevent background scroll when mobile drawer is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const NavContent = () => (
    <nav className="flex-1 space-y-1 p-3">
      {NAVIGATION.map((item) => (
        <NavLink
          key={item.name}
          to={item.to}
          onClick={() => setIsMobileMenuOpen(false)}
          className={({ isActive }) => cn(
            "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
            isActive 
              ? "bg-accent-subtle text-accent shadow-xs font-semibold" 
              : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
          )}
        >
          <item.icon className="w-5 h-5 shrink-0" />
          <span className="truncate">
            {item.name}
          </span>
        </NavLink>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans text-text-primary antialiased selection:bg-accent/20">
      {/* Top Sticky Header */}
      <header className="h-14 sm:h-16 bg-surface/95 backdrop-blur-md border-b border-border flex items-center justify-between px-3 sm:px-6 shrink-0 z-30 sticky top-0 transition-colors w-full">
        {/* Left: Hamburger & Brand */}
        <div className="flex items-center gap-2 sm:gap-4 shrink-0">
          <button 
            className="lg:hidden p-1.5 sm:p-2 text-text-secondary hover:text-text-primary hover:bg-surface-hover rounded-lg transition-colors cursor-pointer"
            onClick={() => setIsMobileMenuOpen(true)}
            aria-label="Open mobile menu"
          >
            <Menu className="w-5 h-5" />
          </button>
          
          <div 
            onClick={() => navigate('/')} 
            className="flex items-center gap-2 text-text-primary font-bold text-base sm:text-lg tracking-tight shrink-0 cursor-pointer select-none"
          >
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-primary text-text-inverse flex items-center justify-center shadow-xs shrink-0">
              <BrainCircuit className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            {/* Branding ALWAYS visible on all screen sizes and zoom levels */}
            <span className="font-bold tracking-tight text-text-primary shrink-0 whitespace-nowrap">
              DSA AI Coach
            </span>
          </div>
        </div>
        
        {/* Center: Search (hidden on mobile and high zoom, compact on tablet, full on desktop) */}
        <div className="flex-1 max-w-xs lg:max-w-md mx-2 sm:mx-6 hidden min-[920px]:block min-w-0">
          <div className="relative w-full">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" />
            <Input 
              type="text" 
              placeholder="Search concepts, topics, algorithms..." 
              className="pl-9 h-9 bg-surface-muted/80 border-border/60 focus-visible:border-accent focus-visible:bg-surface text-xs sm:text-sm w-full"
            />
          </div>
        </div>
        
        {/* Right: Actions */}
        <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
          {/* Header Theme Toggle */}
          <div className="hidden sm:block">
            <ThemeToggle size="sm" />
          </div>

          <div className="h-4 w-px bg-border mx-0.5 hidden sm:block"></div>

          <Button 
            variant="ghost" 
            size="icon" 
            className="relative text-text-secondary hover:text-text-primary hover:bg-surface-hover rounded-full w-8 h-8 sm:w-9 sm:h-9" 
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full ring-2 ring-surface"></span>
          </Button>
          
          {/* User Profile Pill */}
          <div className="flex items-center gap-2 pl-1">
            <div className="flex flex-col items-end hidden lg:flex">
              <span className="text-xs sm:text-sm font-semibold text-text-primary leading-tight line-clamp-1">{user?.name || 'Student'}</span>
              <span className="text-[11px] text-text-muted leading-tight">Pro Member</span>
            </div>
            <div className="h-8 w-8 rounded-full bg-primary text-text-inverse flex items-center justify-center font-bold text-xs sm:text-sm shadow-2xs border border-border shrink-0 select-none">
              {(user?.name || 'S').charAt(0).toUpperCase()}
            </div>
          </div>
          
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={handleLogout} 
            className="text-text-secondary hover:text-error hover:bg-error-subtle rounded-full w-8 h-8 sm:w-9 sm:h-9" 
            aria-label="Log out"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </header>

      {/* Main Layout Container */}
      <div className="flex flex-1 overflow-hidden relative w-full">
        
        {/* Mobile Drawer Overlay */}
        {isMobileMenuOpen && (
          <div 
            className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 lg:hidden transition-opacity animate-in fade-in duration-200"
            onClick={() => setIsMobileMenuOpen(false)}
            aria-hidden="true"
          />
        )}

        {/* Sidebar */}
        <aside className={cn(
          "bg-surface border-r border-border shrink-0 transition-transform duration-300 ease-in-out flex flex-col z-50 fixed inset-y-0 left-0 lg:static lg:block lg:translate-x-0 w-64",
          isMobileMenuOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"
        )}>
          {/* Mobile Drawer Header */}
          <div className="h-14 sm:h-16 flex items-center justify-between px-4 border-b border-border lg:hidden bg-surface">
            <div className="flex items-center gap-2 font-bold text-text-primary">
              <div className="w-7 h-7 rounded-lg bg-primary text-text-inverse flex items-center justify-center shadow-xs">
                <BrainCircuit className="w-4 h-4" />
              </div>
              <span className="text-base font-bold">DSA AI Coach</span>
            </div>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setIsMobileMenuOpen(false)} 
              className="text-text-secondary hover:text-text-primary rounded-lg -mr-1" 
              aria-label="Close menu"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
          
          {/* Navigation Links */}
          <div className="flex-1 overflow-y-auto py-3 custom-scrollbar">
            <NavContent />
          </div>

          {/* Sidebar Footer Controls */}
          <div className="p-4 border-t border-border bg-surface-muted/40 space-y-3 shrink-0">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-text-secondary">Theme</span>
              <ThemeToggle size="sm" />
            </div>
            <div className="space-y-1.5 pt-1">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-text-primary">Daily Streak</span>
                <span className="text-warning font-bold">3 Days 🔥</span>
              </div>
              <div className="w-full bg-border rounded-full h-1.5 overflow-hidden">
                <div className="bg-warning h-1.5 rounded-full w-[60%] transition-all"></div>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content Viewport */}
        <main className="flex-1 overflow-y-auto bg-background focus:outline-none min-w-0 w-full">
          <div className="w-full min-w-0">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
