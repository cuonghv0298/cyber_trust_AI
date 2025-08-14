import { Provision } from '@/types';
import { api } from './base';
import { MOCK_PROVISIONS } from './mocks';

export const provisionsApi = {
  // Get all provisions (no pagination support in backend yet)
  getAll: async (): Promise<Provision[]> => {
    try {
      const response = await api.get('/api/v1/provisions');
      return response.data;
    } catch (error) {
      console.log('Backend not available, using mock data for provisions');
      return MOCK_PROVISIONS;
    }
  },

  // Get provision by ID
  // Note: Backend has incorrect routing - should be fixed to GET /{id} instead of GET /provisions/{id}
  getById: async (id: string): Promise<Provision> => {
    try {
      // Using the current backend implementation (which has double prefix issue)
      const response = await api.get(`/api/v1/provisions/provisions/${id}`);
      return response.data;
    } catch (error) {
      const provision = MOCK_PROVISIONS.find(p => p.id === id);
      if (!provision) {
        throw new Error('Provision not found');
      }
      return provision;
    }
  },

  // Create new provision (admin only)
  // Note: Backend has incorrect routing - should be fixed to POST / instead of POST /provisions
  create: async (provision: Omit<Provision, 'id'> & { id: string }): Promise<Provision> => {
    // Using the current backend implementation (which has double prefix issue)
    const response = await api.post('/api/v1/provisions/provisions', provision);
    return response.data;
  },

  // Update provision (admin only)
  // Note: Backend has incorrect routing - should be fixed to PUT /{id} instead of PUT /provisions/{id}
  update: async (id: string, provision: Partial<Omit<Provision, 'id'>>): Promise<Provision> => {
    // Using the current backend implementation (which has double prefix issue)
    const response = await api.put(`/api/v1/provisions/provisions/${id}`, provision);
    return response.data;
  },

  // Delete provision (admin only)
  // Note: Backend has incorrect routing - should be fixed to DELETE /{id} instead of DELETE /provisions/{id}
  delete: async (id: string): Promise<void> => {
    // Using the current backend implementation (which has double prefix issue)
    await api.delete(`/api/v1/provisions/provisions/${id}`);
  },
};