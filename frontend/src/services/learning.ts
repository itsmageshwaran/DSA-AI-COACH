import { fetchWithAuth } from './api';

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  is_published: boolean;
}

export interface ProgressSummary {
  user_id: string;
  total_lessons_completed: number;
  completion_percentage: number;
  average_score: number | null;
}

export interface RoadmapPhase {
  name: string;
  concept_id: string | null;
  status: 'COMPLETED' | 'CURRENT' | 'LOCKED';
  completed_lessons: number;
  total_lessons: number;
  description: string;
}

export interface RoadmapResponse {
  career_goal: string;
  phases: RoadmapPhase[];
  overall_progress: number;
}

export interface Exercise {
  id: string;
  title: string;
  instructions: string;
  starter_code?: string;
  lesson_id: string;
  difficulty?: string;
  concept_name?: string;
  is_completed?: boolean;
}

export interface ConceptMasteryResponse {
  concept_name: string;
  mastery_percentage: number;
}

export interface AchievementResponse {
  achievement_type: string;
  name: string;
  description: string;
  icon_name: string;
  earned_at: string;
}

export interface RecommendationResponse {
  exercise_id: string;
  title: string;
  difficulty: string;
  topic: string;
  reason: string;
}

export const learningApi = {
  getPaths: async (): Promise<LearningPath[]> => {
    const res = await fetchWithAuth('/learning-paths');
    if (!res.ok) throw new Error('Failed to fetch learning paths');
    return res.json();
  },

  getEnrolledPath: async (): Promise<LearningPath | null> => {
    const res = await fetchWithAuth('/learning-paths/enrolled');
    if (!res.ok) {
      if (res.status === 404) return null;
      throw new Error('Failed to fetch enrolled path');
    }
    return res.json();
  },

  getProgressSummary: async (): Promise<ProgressSummary> => {
    const res = await fetchWithAuth('/progress/me');
    if (!res.ok) {
      return { 
        user_id: '', 
        total_lessons_completed: 0, 
        completion_percentage: 0, 
        average_score: null 
      };
    }
    return res.json();
  },

  getConceptMastery: async (): Promise<ConceptMasteryResponse[]> => {
    const res = await fetchWithAuth('/progress/me/concepts');
    if (!res.ok) {
      return [];
    }
    return res.json();
  },

  getAchievements: async (): Promise<AchievementResponse[]> => {
    const res = await fetchWithAuth('/progress/me/achievements');
    if (!res.ok) {
      return [];
    }
    return res.json();
  },

  getExercises: async (): Promise<Exercise[]> => {
    const res = await fetchWithAuth('/exercises');
    if (!res.ok) throw new Error('Failed to fetch exercises');
    return res.json();
  },

  getExerciseById: async (id: string): Promise<Exercise> => {
    const res = await fetchWithAuth(`/exercises/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch exercise ${id}`);
    return res.json();
  },

  getRoadmap: async (): Promise<RoadmapResponse> => {
    const res = await fetchWithAuth('/recommendations/roadmap');
    if (!res.ok) throw new Error('Failed to fetch roadmap');
    return res.json();
  },

  getNextProblem: async (): Promise<RecommendationResponse | null> => {
    const res = await fetchWithAuth('/recommendations/next-problem');
    if (!res.ok) {
      if (res.status === 404) return null;
      throw new Error('Failed to fetch next problem recommendation');
    }
    return res.json();
  },

  submitExercise: async (exerciseId: string, code: string): Promise<{ submission: any, new_achievements: AchievementResponse[] }> => {
    const res = await fetchWithAuth('/submissions', {
      method: 'POST',
      body: JSON.stringify({ exercise_id: exerciseId, code })
    });
    if (!res.ok) throw new Error('Failed to submit exercise');
    return res.json();
  }
};
