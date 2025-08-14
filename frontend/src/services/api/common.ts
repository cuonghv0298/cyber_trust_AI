import { api } from './base';

// File upload helper
export const uploadFile = async (file: File): Promise<string> => {
  // For demo purposes, convert to base64
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

// Health check
export const healthCheck = async (): Promise<{ status: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    return { status: 'unhealthy' };
  }
};

// Generic API error handler
export const handleApiError = (error: any, fallbackMessage: string = 'An error occurred') => {
  if (error.response) {
    // Server responded with error status
    return error.response.data?.detail || error.response.data?.message || fallbackMessage;
  } else if (error.request) {
    // Request made but no response received
    return 'Network error - please check your connection';
  } else {
    // Something else happened
    return error.message || fallbackMessage;
  }
};

// Generic pagination helper
export const applyPagination = <T>(
  items: T[], 
  options?: { limit?: number; offset?: number }
): T[] => {
  let result = [...items];
  
  if (options?.offset && options.offset < result.length) {
    result = result.slice(options.offset);
  }
  if (options?.limit) {
    result = result.slice(0, options.limit);
  }
  
  return result;
};