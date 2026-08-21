import { fetchWithAuth } from './api';

export interface TestCaseInput {
  input_data: Record<string, any>;
  expected_output?: any;
}

export interface ExecutionResult {
  success: boolean;
  error?: string;
  output?: string;
  execution_time_ms: number;
  memory_used_kb: number;
  test_results: Array<{
    passed: boolean;
    input_data: Record<string, any>;
    expected: any;
    actual: any;
    error?: string;
    execution_time_ms: number;
  }>;
}

export interface ExecutionRunRequest {
  code: string;
  language?: string;
  test_cases: TestCaseInput[];
  entrypoint?: string;
}

export interface ExecutionRunResponse {
  execution: ExecutionResult;
}

export interface ExecutionSubmitRequest {
  exercise_id: string;
  code: string;
  language?: string;
  entrypoint?: string;
  custom_test_cases?: TestCaseInput[];
}

export interface ExecutionSubmitResponse {
  submission_id: string;
  exercise_id: string;
  status: string;
  execution: ExecutionResult;
  progress_updated: boolean;
  new_achievements?: any[];
  mastery_update?: {
    concept: string;
    old_percentage: number;
    new_percentage: number;
  };
  next_problem?: {
    exercise_id: string | null;
    title: string;
    difficulty: string;
    concept: string;
    reason: string;
  };
}

export const executionApi = {
  run: async (request: ExecutionRunRequest): Promise<ExecutionRunResponse> => {
    const res = await fetchWithAuth('/execution/run', {
      method: 'POST',
      body: JSON.stringify(request)
    });
    if (!res.ok) throw new Error('Failed to run code');
    return res.json();
  },

  submit: async (request: ExecutionSubmitRequest): Promise<ExecutionSubmitResponse> => {
    const res = await fetchWithAuth('/execution/submit', {
      method: 'POST',
      body: JSON.stringify(request)
    });
    if (!res.ok) throw new Error('Failed to submit code');
    return res.json();
  }
};
