
// Organization/Company models (matching backend OrganizationResponse)
export interface Organization {
  id: string;
  organisation_name: string;
  acra_number_uen?: string;
  annual_turnover?: number;
  number_of_employees?: number;
  date_of_self_assessment?: string; // ISO date string
  scope_of_certification?: string;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface Company extends Organization {
  // Alias for easier frontend usage
  name: string;
  registrationDate: string;
  status: 'active' | 'completed' | 'pending';
  contactEmail?: string;
  contactPerson?: string;
}

export interface OrganizationCreateData {
  organisation_name: string;
  acra_number_uen?: string;
  annual_turnover?: number;
  number_of_employees?: number;
  date_of_self_assessment?: string;
  scope_of_certification?: string;
}

export interface OrganizationUpdateData {
  organisation_name?: string;
  acra_number_uen?: string;
  annual_turnover?: number;
  number_of_employees?: number;
  date_of_self_assessment?: string;
  scope_of_certification?: string;
}

// Backward compatibility for existing frontend forms
export interface CompanyRegistrationData {
  name: string;
  contactPerson: string;
  contactEmail: string;
  industry?: string;
  size?: string;
}