import { Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { DashboardPage } from './pages/DashboardPage';
import { LearningPathPage } from './pages/LearningPathPage';
import { TopicLearningPage } from './pages/TopicLearningPage';
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
      <Route path="/auth" element={<AuthPage />} />
      
      <Route element={<ProtectedRoute />}>
        <Route path="/onboarding" element={<OnboardingPage />} />
        
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="learn" element={<LearningPathPage />} />
          <Route path="roadmap" element={<LearningPathPage />} />
          <Route path="topics/:topicId" element={<TopicLearningPage />} />
          <Route path="learn/:topicId" element={<TopicLearningPage />} />
          <Route path="problems" element={<ProblemLibraryPage />} />
          <Route path="progress" element={<ProgressPage />} />
          <Route path="coach" element={<Navigate to="/progress" replace />} />
        </Route>

        <Route path="/workspace/:problemId" element={<ProblemWorkspacePage />} />
        <Route path="/problems/:problemId" element={<ProblemWorkspacePage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
