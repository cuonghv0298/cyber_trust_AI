import { Answer } from '@/types';

// Answers API (will need to be implemented in backend)
export const answersApi = {
  // Submit answers for a company
  submit: async (companyId: string, answers: Omit<Answer, 'timestamp' | 'companyId'>[]): Promise<Answer[]> => {
    const submittedAnswers: Answer[] = answers.map(answer => ({
      ...answer,
      companyId,
      timestamp: new Date().toISOString(),
    }));

    // Store in localStorage for demo purposes
    const key = `answers_${companyId}`;
    localStorage.setItem(key, JSON.stringify(submittedAnswers));
    
    return submittedAnswers;
  },

  // Get answers for a company
  getByCompanyId: async (companyId: string): Promise<Answer[]> => {
    const key = `answers_${companyId}`;
    const answers = JSON.parse(localStorage.getItem(key) || '[]');
    return answers;
  },

  // Update specific answer
  update: async (companyId: string, questionId: string, answer: Partial<Answer>): Promise<Answer> => {
    const key = `answers_${companyId}`;
    const answers = JSON.parse(localStorage.getItem(key) || '[]');
    const answerIndex = answers.findIndex((a: Answer) => a.questionId === questionId);
    
    if (answerIndex !== -1) {
      answers[answerIndex] = { ...answers[answerIndex], ...answer };
      localStorage.setItem(key, JSON.stringify(answers));
      return answers[answerIndex];
    }
    
    throw new Error('Answer not found');
  },
};