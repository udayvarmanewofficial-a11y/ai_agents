import api from './api';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string;
  task_type: string;
  status: string;
  llm_provider: string;
  model_name: string;
  use_custom_rag?: boolean;
  research_output?: any;
  plan_output?: any;
  review_output?: any;
  final_output?: any;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface CreateTaskRequest {
  title: string;
  description: string;
  task_type: string;
  llm_provider: string;
  model_name?: string;
  use_custom_rag?: boolean;
}

export interface ModifyTaskRequest {
  modification_request: string;
  llm_provider?: string;
  model_name?: string;
  use_custom_rag?: boolean;
}

export const taskService = {
  createTask: async (data: CreateTaskRequest): Promise<Task> => {
    const response = await api.post('/api/v1/tasks/create', data);
    return response.data;
  },

  getTask: async (taskId: string): Promise<Task> => {
    const response = await api.get(`/api/v1/tasks/${taskId}`);
    return response.data;
  },

  listTasks: async (skip = 0, limit = 20): Promise<Task[]> => {
    const response = await api.get('/api/v1/tasks/', {
      params: { skip, limit },
    });
    return response.data;
  },

  modifyTask: async (taskId: string, data: ModifyTaskRequest): Promise<Task> => {
    const response = await api.post(`/api/v1/tasks/${taskId}/modify`, data);
    return response.data;
  },

  deleteTask: async (taskId: string): Promise<void> => {
    await api.delete(`/api/v1/tasks/${taskId}`);
  },
};
