import { Provision } from '@/types';

export const MOCK_PROVISIONS: Provision[] = [
  {
    id: "A.8.4(a)",
    section: "A",
    subsection: "8", 
    clause: "4",
    subclause: "a",
    provision: "The organisation shall identify business-critical systems and those containing essential business information and perform backup.",
    keywords: ["backup", "business-critical", "systems", "information"],
    questions: ["1", "2", "5", "6", "9", "10"]
  },
  {
    id: "A.8.4(b)",
    section: "A",
    subsection: "8",
    clause: "4", 
    subclause: "b",
    provision: "The backups shall be performed on a regular basis, with the backup frequency aligned to the business requirements and how many days' worth of data the organisation can afford to lose.",
    keywords: ["backup", "frequency", "business requirements", "data retention"],
    questions: ["2", "3", "4", "7", "8", "9"]
  }
];