/**
 * DEPRECATED: This file is kept for backward compatibility
 * 
 * NEW STRUCTURE:
 * Use individual API modules from './api/' directory:
 * - import { questionsApi } from '@/services/api/questions'
 * - import { provisionsApi } from '@/services/api/provisions'  
 * - import { companiesApi } from '@/services/api/companies'
 * - import { organizationsApi } from '@/services/api/organizations'
 * - import { answersApi } from '@/services/api/answers'
 * - import { uploadFile, healthCheck } from '@/services/api/common'
 * 
 * Or use the barrel export:
 * - import { questionsApi, provisionsApi, ... } from '@/services/api'
 */

// Re-export everything from the modular API structure
export { questionsApi, type QuestionsApiOptions } from './api/questions';
export { provisionsApi } from './api/provisions';
export { companiesApi } from './api/companies'; // Backward compatibility
export { organizationsApi, type OrganizationsApiOptions } from './api/organizations'; // New API
export { answersApi } from './api/answers';
export { uploadFile, healthCheck, handleApiError } from './api/common';
export { MOCK_QUESTIONS, MOCK_PROVISIONS, MOCK_ORGANIZATIONS } from './api/mocks';

// Export the base api instance
import { api } from './api/base';
export { api };
export default api;