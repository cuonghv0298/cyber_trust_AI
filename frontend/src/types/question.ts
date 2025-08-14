
export interface Question {
  id: string;
  question: string;
  audience?: string[];
  cyberessentials_requirement?: string;
  group_tag?: string;
  provisions?: string[];
}