// Shared types for UI state and API responses

export type UserRole = 'company' | 'auditor';

export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}