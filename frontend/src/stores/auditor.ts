import { create } from 'zustand';
import { Company, Question, Answer, Evaluation, ProvisionEvaluation, ComplianceReport } from '@/types';

interface AuditorState {
  // Companies data
  companies: Company[];
  selectedCompany: Company | null;
  
  // Questions and provisions
  questions: Question[];
  provisions: any[];
  
  // Evaluation state
  answers: Answer[];
  evaluations: Record<string, Evaluation>; // questionId -> evaluation
  provisionEvaluations: Record<string, ProvisionEvaluation>; // provisionId -> provision evaluation
  
  // UI state
  currentProvisionId: string | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  setCompanies: (companies: Company[]) => void;
  setSelectedCompany: (company: Company | null) => void;
  setQuestions: (questions: Question[]) => void;
  setProvisions: (provisions: any[]) => void;
  setAnswers: (answers: Answer[]) => void;
  setCurrentProvisionId: (provisionId: string | null) => void;
  
  // Evaluation actions
  setEvaluation: (questionId: string, evaluation: Evaluation) => void;
  setProvisionEvaluation: (provisionId: string, evaluation: ProvisionEvaluation) => void;
  
  // Computed
  getAnswersForCompany: (companyId: string) => Answer[];
  getEvaluationForQuestion: (questionId: string) => Evaluation | null;
  getProvisionEvaluation: (provisionId: string) => ProvisionEvaluation | null;
  getComplianceReport: (companyId: string) => ComplianceReport | null;
  getOverallComplianceScore: (companyId: string) => number;
  
  // UI helpers
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearEvaluations: () => void;
}

export const useAuditorStore = create<AuditorState>((set, get) => ({
  // Initial state
  companies: [],
  selectedCompany: null,
  questions: [],
  provisions: [],
  answers: [],
  evaluations: {},
  provisionEvaluations: {},
  currentProvisionId: null,
  loading: false,
  error: null,

  // Actions
  setCompanies: (companies) => set({ companies }),

  setSelectedCompany: (company) => set({ 
    selectedCompany: company,
    // Clear previous evaluations when switching companies
    evaluations: {},
    provisionEvaluations: {},
    currentProvisionId: null,
  }),

  setQuestions: (questions) => set({ questions }),

  setProvisions: (provisions) => set({ provisions }),

  setAnswers: (answers) => set({ answers }),

  setCurrentProvisionId: (provisionId) => set({ currentProvisionId: provisionId }),

  // Evaluation actions
  setEvaluation: (questionId, evaluation) => {
    const state = get();
    set({
      evaluations: {
        ...state.evaluations,
        [questionId]: evaluation
      }
    });
  },

  setProvisionEvaluation: (provisionId, evaluation) => {
    const state = get();
    set({
      provisionEvaluations: {
        ...state.provisionEvaluations,
        [provisionId]: evaluation
      }
    });
  },

  // Computed functions
  getAnswersForCompany: (companyId) => {
    const state = get();
    return state.answers.filter(answer => answer.companyId === companyId);
  },

  getEvaluationForQuestion: (questionId) => {
    const state = get();
    return state.evaluations[questionId] || null;
  },

  getProvisionEvaluation: (provisionId) => {
    const state = get();
    return state.provisionEvaluations[provisionId] || null;
  },

  getComplianceReport: (companyId) => {
    const state = get();
    const company = state.companies.find(c => c.id === companyId);
    
    if (!company || !state.selectedCompany) return null;

    const provisionEvaluations = Object.values(state.provisionEvaluations);
    const totalProvisions = provisionEvaluations.length;
    const passedProvisions = provisionEvaluations.filter(pe => pe.overallResult === 'pass').length;
    const overallScore = totalProvisions > 0 ? (passedProvisions / totalProvisions) * 100 : 0;

    return {
      companyId,
      company,
      provisions: provisionEvaluations,
      overallScore,
      totalProvisions,
      passedProvisions,
      completionDate: new Date().toISOString(),
      generatedBy: 'Current Auditor', // This should come from auth context
    };
  },

  getOverallComplianceScore: (companyId) => {
    const state = get();
    const report = state.getComplianceReport(companyId);
    return report?.overallScore || 0;
  },

  // UI helpers
  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  clearEvaluations: () => set({
    evaluations: {},
    provisionEvaluations: {},
    currentProvisionId: null,
  }),
})); 