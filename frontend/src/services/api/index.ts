// Barrel exports for API modules
export { questionsApi } from './questions';
export { provisionsApi } from './provisions';
export { companiesApi } from './companies'; // Backward compatibility wrapper
export { organizationsApi } from './organizations'; // New proper API
export { answersApi } from './answers';

// Export shared utilities
export { uploadFile, healthCheck, handleApiError } from './common';

// Export base API instance if needed
export { api as default, api } from './base';

// Export types for API options
export type { QuestionsApiOptions } from './questions';
export type { OrganizationsApiOptions } from './organizations';

// Re-export mock data if needed for testing
export * from './mocks';