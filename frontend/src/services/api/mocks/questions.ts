import { Question } from '@/types';

export const MOCK_QUESTIONS: Question[] = [
  {
    id: "1",
    question: "Who are your primary customers? Is it B2B or B2C? What are the services provided?",
    audience: ["Owner"],
    cyberessentials_requirement: "Understanding business context",
    group_tag: "CONTEXT",
    provisions: ["A.8.4(a)"]
  },
  {
    id: "2", 
    question: "What is Operating System used for end user and application currently?",
    audience: ["Owner", "IT"],
    cyberessentials_requirement: "Asset inventory",
    group_tag: "HW/SW INV",
    provisions: ["A.8.4(a)", "A.8.4(b)"]
  },
  {
    id: "3",
    question: "Do you know whether the OS used is already end of support?",
    audience: ["IT"],
    cyberessentials_requirement: "Patch management",
    group_tag: "PATCH/VULN",
    provisions: ["A.8.4(b)"]
  },
  {
    id: "4",
    question: "Anyone looking at whether the used OS not more supported by vendor eg Microsoft?",
    audience: ["IT"],
    cyberessentials_requirement: "Vulnerability management",
    group_tag: "PATCH/VULN",
    provisions: ["A.8.4(b)"]
  },
  {
    id: "5",
    question: "Any asset inventory list? Both hardware and software. Who is managing it?",
    audience: ["Owner", "IT"],
    cyberessentials_requirement: "Asset management",
    group_tag: "HW/SW INV",
    provisions: ["A.8.4(a)"]
  },
  {
    id: "6",
    question: "Are there any machines running somewhere that you might not be aware? Who should be the one who gives the information?",
    audience: ["IT"],
    cyberessentials_requirement: "Asset discovery",
    group_tag: "HW/SW INV",
    provisions: ["A.8.4(a)"]
  },
  {
    id: "7",
    question: "Are there any security controls (i.e EDR) installed in machines?",
    audience: ["Owner", "IT"],
    cyberessentials_requirement: "Malware protection",
    group_tag: "MALWARE",
    provisions: ["A.8.4(b)"]
  },
  {
    id: "8",
    question: "Any VA scans conducted? Can share the frequency and remediations. Who is managing it?",
    audience: ["IT"],
    cyberessentials_requirement: "Vulnerability scanning",
    group_tag: "PATCH/VULN",
    provisions: ["A.8.4(b)"]
  },
  {
    id: "9",
    question: "Is there a business continuity plan in place?",
    audience: ["Owner"],
    cyberessentials_requirement: "Business continuity",
    group_tag: "IR/BCP",
    provisions: ["A.8.4(a)", "A.8.4(b)"]
  },
  {
    id: "10",
    question: "What are the company's critical functions?",
    audience: ["Owner", "IT"],
    cyberessentials_requirement: "Business impact analysis",
    group_tag: "IR/BCP",
    provisions: ["A.8.4(a)"]
  }
];