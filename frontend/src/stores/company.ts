import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Company, Answer, Question } from '@/types';

interface CompanyState {
  // Current company data
  currentCompany: Company | null;
  
  // Questionnaire state
  questions: Question[];
  answers: Record<string, { answer: string; files?: File[] }>;
  currentQuestionIndex: number;
  isSubmitted: boolean;
  
  // Progress tracking
  completedQuestions: Set<string>;
  
  // Actions
  setCurrentCompany: (company: Company | null) => void;
  setQuestions: (questions: Question[]) => void;
  setAnswer: (questionId: string, answer: string, files?: File[]) => void;
  setCurrentQuestionIndex: (index: number) => void;
  markQuestionCompleted: (questionId: string) => void;
  submitAnswers: () => void;
  resetQuestionnaire: () => void;
  
  // Computed
  getProgress: () => number;
  getCurrentQuestion: () => Question | null;
  isQuestionCompleted: (questionId: string) => boolean;
  canSubmit: () => boolean;
}

export const useCompanyStore = create<CompanyState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentCompany: null,
      questions: [],
      answers: {},
      currentQuestionIndex: 0,
      isSubmitted: false,
      completedQuestions: new Set(),

      // Actions
      setCurrentCompany: (company) => set({ currentCompany: company }),

      setQuestions: (questions) => set({ questions, currentQuestionIndex: 0 }),

      setAnswer: (questionId, answer, files) => {
        const state = get();
        const newAnswers = {
          ...state.answers,
          [questionId]: { answer, files: files || [] }
        };
        
        // Mark question as completed if answer is provided
        const newCompletedQuestions = new Set(state.completedQuestions);
        if (answer.trim()) {
          newCompletedQuestions.add(questionId);
        } else {
          newCompletedQuestions.delete(questionId);
        }

        set({ 
          answers: newAnswers, 
          completedQuestions: newCompletedQuestions 
        });
      },

      setCurrentQuestionIndex: (index) => set({ currentQuestionIndex: index }),

      markQuestionCompleted: (questionId) => {
        const state = get();
        const newCompletedQuestions = new Set(state.completedQuestions);
        newCompletedQuestions.add(questionId);
        set({ completedQuestions: newCompletedQuestions });
      },

      submitAnswers: () => set({ isSubmitted: true }),

      resetQuestionnaire: () => set({
        answers: {},
        currentQuestionIndex: 0,
        isSubmitted: false,
        completedQuestions: new Set(),
      }),

      // Computed functions
      getProgress: () => {
        const state = get();
        if (state.questions.length === 0) return 0;
        return (state.completedQuestions.size / state.questions.length) * 100;
      },

      getCurrentQuestion: () => {
        const state = get();
        return state.questions[state.currentQuestionIndex] || null;
      },

      isQuestionCompleted: (questionId) => {
        const state = get();
        return state.completedQuestions.has(questionId);
      },

      canSubmit: () => {
        const state = get();
        return state.questions.length > 0 && 
               state.completedQuestions.size === state.questions.length;
      },
    }),
    {
      name: 'company-store',
      // Only persist essential data, not the entire state
      partialize: (state) => ({
        currentCompany: state.currentCompany,
        answers: state.answers,
        isSubmitted: state.isSubmitted,
        completedQuestions: Array.from(state.completedQuestions),
      }),
      // Rehydrate Set from array
      onRehydrateStorage: () => (state) => {
        if (state && Array.isArray(state.completedQuestions)) {
          (state as any).completedQuestions = new Set(state.completedQuestions);
        }
      },
    }
  )
); 