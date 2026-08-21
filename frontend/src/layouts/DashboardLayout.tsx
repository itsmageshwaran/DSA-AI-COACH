import { useState } from 'react';
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

const NAVIGATION = [
  { name: 'Home', to: '/', icon: LayoutDashboard },
  { name: 'My Roadmap', to: '/learn', icon: BookOpen },
  { name: 'Problems', to: '/problems', icon: Code2 },
  { name: 'Progress', to: '/progress', icon: TrendingUp },
  { name: 'AI Coach', to: '/coach', icon: BrainCircuit },
];

export function DashboardLayout() {
  const [isSidebarOpen] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

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
            "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-200",
            isActive 
              ? "bg-accent-subtle text-accent shadow-xs" 
              : "text-text-secondary hover:bg-surface-hover hover:text-text-primary"
          )}
        >
          <item.icon className="w-5 h-5 shrink-0" />
          <span className={cn(
            "truncate transition-all duration-300", 
            !isSidebarOpen && "hidden md:hidden lg:block" // In a fully built collapsable sidebar this would hide
          )}>
            {item.name}
          </span>
        </NavLink>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans text-text-primary">
      {/* Top Header */}
      <header className="h-16 bg-surface border-b border-border flex items-center justify-between px-4 lg:px-6 shrink-0 z-20 sticky top-0">
        <div className="flex items-center gap-4">
          <button 
            className="lg:hidden p-2 text-text-secondary hover:bg-surface-hover rounded-md transition-colors"
            onClick={() => setIsMobileMenuOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2 text-primary font-bold text-xl tracking-tight">
            <div className="w-8 h-8 rounded-lg bg-primary text-text-inverse flex items-center justify-center shadow-sm">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <span className="hidden sm:inline-block">DSA AI Coach</span>
          </div>
        </div>
        
        <div className="flex items-center gap-3 lg:gap-6">
          <div className="relative hidden md:block w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <Input 
              type="text" 
              placeholder="Search concepts or problems..." 
              className="pl-9 h-9 bg-surface-muted border-transparent focus-visible:border-border focus-visible:bg-surface"
            />
          </div>
          
          <div className="flex items-center gap-2 lg:gap-4">
            <Button variant="ghost" size="icon" className="relative text-text-secondary rounded-full">
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full ring-2 ring-surface"></span>
            </Button>
            
            <div className="hidden sm:block h-6 w-px bg-border mx-1"></div>
            
            <div className="flex items-center gap-3 pl-1 lg:pl-0">
              <div className="flex flex-col items-end hidden md:flex">
                <span className="text-sm font-semibold text-text-primary">{user?.name || 'Student'}</span>
                <span className="text-xs text-text-muted">Pro Member</span>
              </div>
              <div className="h-8 w-8 rounded-full bg-primary text-text-inverse flex items-center justify-center font-semibold text-sm shadow-sm cursor-pointer border border-border">
                {(user?.name || 'S').charAt(0).toUpperCase()}
              </div>
            </div>
            
            <Button variant="ghost" size="icon" onClick={handleLogout} className="text-text-secondary hover:text-error hover:bg-error-subtle rounded-full ml-1">
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden relative">
        
        {/* Mobile Drawer Overlay */}
        {isMobileMenuOpen && (
          <div 
            className="fixed inset-0 bg-primary/20 backdrop-blur-sm z-30 lg:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
          />
        )}

        {/* Sidebar */}
        <aside className={cn(
          "bg-surface border-r border-border shrink-0 transition-all duration-300 ease-in-out flex flex-col z-40 fixed inset-y-0 left-0 lg:static lg:block",
          isMobileMenuOpen ? "translate-x-0 w-64 shadow-2xl" : "-translate-x-full lg:translate-x-0",
          isSidebarOpen ? "lg:w-64" : "lg:w-20"
        )}>
          <div className="h-16 flex items-center justify-between px-4 border-b border-border lg:hidden">
            <span className="font-bold text-primary">Menu</span>
            <Button variant="ghost" size="icon" onClick={() => setIsMobileMenuOpen(false)} className="-mr-2">
              <X className="w-5 h-5" />
            </Button>
          </div>
          
          <div className="flex-1 overflow-y-auto py-4">
            <NavContent />
          </div>

          <div className="p-4 border-t border-border bg-surface-muted/30">
            <div className={cn("flex items-center gap-3", !isSidebarOpen && "lg:hidden")}>
              <div className="flex-1">
                <p className="text-xs font-medium text-text-primary">Learning Streak</p>
                <div className="w-full bg-border rounded-full h-1.5 mt-2">
                  <div className="bg-warning h-1.5 rounded-full w-[60%]"></div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto bg-background focus:outline-none">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
