// Type-safe constants and their derived types

export const AUDIENCE_OPTIONS = [
  'Owner',
  'Purchaser', 
  'IT',
  'HR',
  'Employee'
] as const;

export const GROUP_TAG_OPTIONS = [
  'CONTEXT',
  'TRAINING',
  'POLICY',
  'HW/SW INV',
  'DISPOSAL',
  'CHANGE',
  'DATA INV',
  'NETWORK',
  'PHYS-ENV',
  'MALWARE',
  'BACKUP',
  'IR/BCP',
  'FIREWALL',
  'WIFI',
  'VENDOR',
  'ACCT MGMT',
  'BYOD',
  'PATCH/VULN'
] as const;

export type AudienceOption = typeof AUDIENCE_OPTIONS[number];
export type GroupTagOption = typeof GROUP_TAG_OPTIONS[number];