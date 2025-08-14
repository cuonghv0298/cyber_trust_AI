import { Company, Organization, CompanyRegistrationData, OrganizationCreateData } from '@/types/organization';
import { organizationsApi } from './organizations';

// Utility functions to convert between Company and Organization interfaces
const organizationToCompany = (org: Organization): Company => ({
  ...org,
  name: org.organisation_name, // Map organisation_name to name for backward compatibility
  registrationDate: org.created_at,
  status: 'active' as const, // Default status since backend doesn't track this yet
});

const companyRegistrationToOrganization = (companyData: CompanyRegistrationData): OrganizationCreateData => ({
  organisation_name: companyData.name,
  // Note: Backend organization doesn't have contactPerson/contactEmail fields
  // These would need to be handled separately or the backend extended
  scope_of_certification: companyData.industry, // Map industry to scope for now
});

/**
 * @deprecated Use organizationsApi directly for new code
 * This API is kept for backward compatibility with existing frontend code
 */
export const companiesApi = {
  // Register new company (backward compatibility wrapper)
  register: async (companyData: Omit<Company, 'id' | 'registrationDate' | 'status'>): Promise<Company> => {
    try {
      // Try to convert to organization format
      const orgData = companyRegistrationToOrganization(companyData as CompanyRegistrationData);
      const organization = await organizationsApi.create(orgData);
      return organizationToCompany(organization);
    } catch (error) {
      // Fallback to localStorage for demo purposes
      const newCompany: Company = {
        id: Date.now().toString(),
        ...companyData,
        name: companyData.name || (companyData as any).organisation_name || 'Unknown Company',
        organisation_name: companyData.name || (companyData as any).organisation_name || 'Unknown Company',
        registrationDate: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        status: 'active',
      };
      
      const companies = JSON.parse(localStorage.getItem('companies') || '[]');
      companies.push(newCompany);
      localStorage.setItem('companies', JSON.stringify(companies));
      
      return newCompany;
    }
  },

  // Get all companies (backward compatibility wrapper)
  getAll: async (): Promise<Company[]> => {
    try {
      const organizations = await organizationsApi.getAll();
      return organizations.map(organizationToCompany);
    } catch (error) {
      // Fallback to localStorage for demo purposes
      const companies = JSON.parse(localStorage.getItem('companies') || '[]');
      return companies;
    }
  },

  // Get company by ID (backward compatibility wrapper)
  getById: async (id: string): Promise<Company | null> => {
    try {
      const organization = await organizationsApi.getById(id);
      return organizationToCompany(organization);
    } catch (error) {
      // Fallback to localStorage for demo purposes
      const companies = JSON.parse(localStorage.getItem('companies') || '[]');
      return companies.find((c: Company) => c.id === id) || null;
    }
  },

  // Update company status (frontend-specific, not backed by API yet)
  updateStatus: async (id: string, status: Company['status']): Promise<Company> => {
    // This is frontend-specific functionality - backend doesn't have status field
    // Store in localStorage for demo purposes
    const companies = JSON.parse(localStorage.getItem('companies') || '[]');
    const companyIndex = companies.findIndex((c: Company) => c.id === id);
    if (companyIndex !== -1) {
      companies[companyIndex].status = status;
      localStorage.setItem('companies', JSON.stringify(companies));
      return companies[companyIndex];
    }
    throw new Error('Company not found');
  },

  // Search companies by name (backward compatibility wrapper)
  searchByName: async (namePattern: string): Promise<Company[]> => {
    try {
      const organizations = await organizationsApi.searchByName(namePattern);
      return organizations.map(organizationToCompany);
    } catch (error) {
      console.log('Search failed, returning empty results');
      return [];
    }
  },

  // Search companies by employee count (backward compatibility wrapper)
  searchByEmployeeCount: async (minEmployees: number, maxEmployees: number): Promise<Company[]> => {
    try {
      const organizations = await organizationsApi.searchByEmployeeCount(minEmployees, maxEmployees);
      return organizations.map(organizationToCompany);
    } catch (error) {
      console.log('Search failed, returning empty results');
      return [];
    }
  },
};