import { Question } from '@/types';
import { api } from './base';
import { applyPagination } from './common';
import { MOCK_QUESTIONS } from './mocks';

export interface QuestionsApiOptions {
  limit?: number;
  offset?: number;
}

export const questionsApi = {
  // Get all questions with optional pagination
  getAll: async (options?: QuestionsApiOptions): Promise<Question[]> => {
    try {
      const params = new URLSearchParams();
      if (options?.limit) params.append('limit', options.limit.toString());
      if (options?.offset) params.append('offset', options.offset.toString());
      
      const response = await api.get(`/api/v1/questions${params.toString() ? `?${params.toString()}` : ''}`);
      return response.data;
    } catch (error) {
      console.log(error);
      console.log('Backend not available, using mock data for questions');
      // Return mock data when backend is not available
      return applyPagination(MOCK_QUESTIONS, options);
    }
  },

  // Get question by ID
  getById: async (id: string): Promise<Question> => {
    try {
      const response = await api.get(`/api/v1/questions/${id}`);
      return response.data;
    } catch (error) {
      const question = MOCK_QUESTIONS.find(q => q.id === id);
      if (!question) {
        throw new Error('Question not found');
      }
      return question;
    }
  },

  // Create new question (admin only)
  create: async (question: Omit<Question, 'id'> & { id: string }): Promise<Question> => {
    const response = await api.post('/api/v1/questions', question);
    return response.data;
  },

  // Update question (admin only)
  update: async (id: string, question: Partial<Omit<Question, 'id'>>): Promise<Question> => {
    const response = await api.put(`/api/v1/questions/${id}`, question);
    return response.data;
  },

  // Delete question (admin only)
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/v1/questions/${id}`);
  },
};