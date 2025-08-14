// Form data types for various UI components

export interface QuestionnaireFormData {
  [questionId: string]: {
    answer: string;
    files?: FileList;
  };
}