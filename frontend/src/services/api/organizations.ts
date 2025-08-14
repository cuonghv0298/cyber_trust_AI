import { Organization, OrganizationCreateData, OrganizationUpdateData } from '@/types';
import { api } from './base';
import { applyPagination } from './common';
import { MOCK_ORGANIZATIONS } from './mocks';

export interface OrganizationsApiOptions {
  limit?: number;
  offset?: number;
}

export interface OrganizationSearchByNameOptions {
  namePattern: string;
}

export interface OrganizationSearchByEmployeeCountOptions {
  minEmployees: number;
  maxEmployees: number;
}

export const organizationsApi = {
  // Get all organizations with optional pagination
  getAll: async (options?: OrganizationsApiOptions): Promise<Organization[]> => {
    try {
      const params = new URLSearchParams();
      if (options?.limit) params.append('limit', options.limit.toString());
      if (options?.offset) params.append('offset', options.offset.toString());
      
      const response = await api.get(`/api/v1/organizations${params.toString() ? `?${params.toString()}` : ''}`);
      return response.data;
    } catch (error) {
      console.log('Backend not available, using mock data for organizations');
      return applyPagination(MOCK_ORGANIZATIONS, options);
    }
  },

  // Get organization by ID
  getById: async (id: string): Promise<Organization> => {
    try {
      const response = await api.get(`/api/v1/organizations/${id}`);
      return response.data;
    } catch (error) {
      const organization = MOCK_ORGANIZATIONS.find(org => org.id === id);
      if (!organization) {
        throw new Error('Organization not found');
      }
      return organization;
    }
  },

  // Create new organization
  create: async (organizationData: OrganizationCreateData): Promise<Organization> => {
    try {
      const response = await api.post('/api/v1/organizations', organizationData);
      return response.data;
    } catch (error) {
      // For demo purposes, create mock organization
      const newOrg: Organization = {
        id: Date.now().toString(),
        ...organizationData,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      return newOrg;
    }
  },

  // Update organization
  update: async (id: string, organizationData: OrganizationUpdateData): Promise<Organization> => {
    try {
      const response = await api.put(`/api/v1/organizations/${id}`, organizationData);
      return response.data;
    } catch (error) {
      const organization = MOCK_ORGANIZATIONS.find(org => org.id === id);
      if (!organization) {
        throw new Error('Organization not found');
      }
      return {
        ...organization,
        ...organizationData,
        updated_at: new Date().toISOString(),
      };
    }
  },

  // Delete organization
  delete: async (id: string): Promise<void> => {
    try {
      await api.delete(`/api/v1/organizations/${id}`);
    } catch (error) {
      // For mock purposes, just log the deletion
      console.log(`Would delete organization with ID: ${id}`);
    }
  },

  // Search organizations by name pattern
  searchByName: async (namePattern: string): Promise<Organization[]> => {
    try {
      const response = await api.get(`/api/v1/organizations/search/by-name/${encodeURIComponent(namePattern)}`);
      return response.data;
    } catch (error) {
      console.log('Backend not available, using mock data for organization search by name');
      return MOCK_ORGANIZATIONS.filter(org => 
        org.organisation_name.toLowerCase().includes(namePattern.toLowerCase())
      );
    }
  },

  // Search organizations by employee count range
  searchByEmployeeCount: async (minEmployees: number, maxEmployees: number): Promise<Organization[]> => {
    try {
      const response = await api.get(`/api/v1/organizations/search/by-employee-count/${minEmployees}/${maxEmployees}`);
      return response.data;
    } catch (error) {
      console.log('Backend not available, using mock data for organization search by employee count');
      return MOCK_ORGANIZATIONS.filter(org => {
        const empCount = org.number_of_employees || 0;
        return empCount >= minEmployees && empCount <= maxEmployees;
      });
    }
  },
};