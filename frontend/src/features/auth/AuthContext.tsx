import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { fetchWithAuth } from '../../services/api';

interface UserProfile {
  career_goal: string;
  experience_level: string;
  preferred_language: string;
}

interface User {
  id: string;
  email: string;
  name: string;
  profile?: UserProfile;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (profileData: UserProfile) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if we have a token
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchWithAuth('/users/me')
        .then(res => {
          if (!res.ok) throw new Error('Token invalid');
          return res.json();
        })
        .then(data => {
          setUser({ 
            id: data.id, 
            email: data.email, 
            name: data.full_name || data.email.split('@')[0],
            profile: data.profile 
          });
        })
        .catch(() => {
          localStorage.removeItem('access_token');
          setUser(null);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }

    const handleAuthError = () => {
      setUser(null);
    };

    window.addEventListener('auth-error', handleAuthError);
    return () => window.removeEventListener('auth-error', handleAuthError);
  }, []);

  const login = async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetchWithAuth('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });

    if (!res.ok) {
      let errMsg = 'Login failed. Please check your email and password.';
      try {
        const err = await res.json();
        errMsg = err.error?.message || err.detail || errMsg;
      } catch (_) {}
      throw new Error(errMsg);
    }

    const data = await res.json();
    localStorage.setItem('access_token', data.access_token);
    
    // Fetch real user data
    const userRes = await fetchWithAuth('/users/me');
    if (userRes.ok) {
      const userData = await userRes.json();
      setUser({ 
        id: userData.id, 
        email: userData.email, 
        name: userData.full_name || userData.email.split('@')[0],
        profile: userData.profile
      });
    } else {
      // Fallback
      setUser({ id: 'temp', email, name: email.split('@')[0] });
    }
  };

  const register = async (email: string, password: string) => {
    const res = await fetchWithAuth('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      let errMsg = 'Registration failed';
      try {
        const err = await res.json();
        errMsg = err.error?.message || err.detail || errMsg;
      } catch (_) {}

      // If user already registered, seamlessly attempt login
      if (res.status === 400 && errMsg.toLowerCase().includes('already registered')) {
        try {
          await login(email, password);
          return;
        } catch (_) {
          throw new Error('This email is already registered. Please sign in with your password.');
        }
      }
      throw new Error(errMsg);
    }
    
    // Auto-login after registration
    await login(email, password);
  };

  const updateProfile = async (profileData: UserProfile) => {
    const res = await fetchWithAuth('/users/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Profile update failed');
    }

    const updatedProfile = await res.json();
    setUser(prev => prev ? { ...prev, profile: updatedProfile } : null);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
