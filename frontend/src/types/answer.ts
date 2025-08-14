
export interface Answer {
  questionId: string;
  answer: string;
  files?: File[];
  timestamp: string;
  companyId: string;
}