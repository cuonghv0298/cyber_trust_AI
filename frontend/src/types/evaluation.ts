import { Question } from './question';
import { Answer } from './answer';
import { Provision } from './provision';
import { Company } from './organization';

export interface Evaluation {
  questionId: string;
  answer: string;
  result: 'pass' | 'fail' | 'pending';
  reason?: string;
  auditorNotes?: string;
  evaluatedBy?: string;
  evaluatedAt?: string;
}

export interface ProvisionEvaluation {
  provisionId: string;
  provision: Provision;
  questions: QuestionEvaluation[];
  overallResult: 'pass' | 'fail' | 'partial';
  passPercentage: number;
}

export interface QuestionEvaluation {
  question: Question;
  answer: Answer;
  evaluation: Evaluation;
}

export interface ComplianceReport {
  companyId: string;
  company: Company;
  provisions: ProvisionEvaluation[];
  overallScore: number;
  totalProvisions: number;
  passedProvisions: number;
  completionDate: string;
  generatedBy: string;
}