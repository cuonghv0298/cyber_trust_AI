import { Organization } from '@/types';

export const MOCK_ORGANIZATIONS: Organization[] = [
  {
    id: "1",
    organisation_name: "Tech Solutions Pte Ltd",
    acra_number_uen: "201234567H",
    annual_turnover: 5000000,
    number_of_employees: 150,
    date_of_self_assessment: "2024-01-15",
    scope_of_certification: "IT services and software development",
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-15T10:30:00Z"
  },
  {
    id: "2",
    organisation_name: "Singapore Manufacturing Co.",
    acra_number_uen: "199876543B",
    annual_turnover: 12000000,
    number_of_employees: 350,
    date_of_self_assessment: "2024-02-20",
    scope_of_certification: "Manufacturing operations and quality control systems",
    created_at: "2023-12-10T09:15:00Z",
    updated_at: "2024-02-20T14:20:00Z"
  },
  {
    id: "3",
    organisation_name: "Digital Marketing Hub",
    acra_number_uen: "202445678C",
    annual_turnover: 2500000,
    number_of_employees: 75,
    date_of_self_assessment: "2024-03-10",
    scope_of_certification: "Digital marketing services and customer data management",
    created_at: "2024-01-20T11:30:00Z",
    updated_at: "2024-03-10T16:45:00Z"
  },
  {
    id: "4",
    organisation_name: "Healthcare Systems Ltd",
    acra_number_uen: "200567890D",
    annual_turnover: 8000000,
    number_of_employees: 200,
    date_of_self_assessment: "2024-01-30",
    scope_of_certification: "Healthcare information systems and patient data management",
    created_at: "2023-11-15T08:00:00Z",
    updated_at: "2024-01-30T12:00:00Z"
  },
  {
    id: "5",
    organisation_name: "Small Business Consultancy",
    acra_number_uen: "202112345E",
    annual_turnover: 800000,
    number_of_employees: 25,
    date_of_self_assessment: "2024-02-28",
    scope_of_certification: "Business consultancy and financial advisory services",
    created_at: "2024-02-01T10:00:00Z",
    updated_at: "2024-02-28T17:30:00Z"
  }
];