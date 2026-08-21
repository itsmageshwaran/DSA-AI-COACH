import { Routes, Route } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { DashboardPage } from './pages/DashboardPage';
import { LearningPathPage } from './pages/LearningPathPage';
import { ProblemLibraryPage } from './pages/ProblemLibraryPage';
import { ProblemWorkspacePage } from './pages/ProblemWorkspacePage';
import { AuthPage } from './pages/AuthPage';
import { ProgressPage } from './pages/ProgressPage';
import { OnboardingPage } from './pages/OnboardingPage';
import { ProtectedRoute } from './features/auth/ProtectedRoute';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />
      
      <Route element={<ProtectedRoute />}>
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="learn" element={<LearningPathPage />} />
          <Route path="problems" element={<ProblemLibraryPage />} />
          <Route path="coach" element={<div className="p-8">AI Coach (Coming Soon)</div>} />
          <Route path="progress" element={<ProgressPage />} />
        </Route>
        <Route path="/workspace/:problemId" element={<ProblemWorkspacePage />} />
      </Route>
    </Routes>
  );
}

export default App;
