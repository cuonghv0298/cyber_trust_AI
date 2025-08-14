# CNAV Frontend - Cybersecurity Compliance & Audit Platform

This is the frontend application for the CNAV (Cybersecurity Compliance & Audit) platform, built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

### For Companies
- **Company Registration**: Register company details to access the platform
- **Questionnaire Interface**: Answer cybersecurity compliance questions
- **Progress Tracking**: Track completion progress with visual indicators
- **File Uploads**: Upload supporting documents for questions (planned)
- **Auto-save**: Automatic saving of progress while answering questions (planned)

### For Auditors
- **Company Overview**: View all registered companies and their status
- **Compliance Review**: Review and evaluate company submissions (planned)
- **Provision Mapping**: Map questions to compliance provisions (planned)
- **Report Generation**: Generate compliance reports and scores (planned)

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand with persistence
- **Forms**: React Hook Form with validation
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Project Structure

```
src/
├── app/                 # Next.js App Router pages
│   ├── company/        # Company-specific routes
│   │   ├── page.tsx           # Company dashboard
│   │   ├── register/          # Company registration
│   │   └── questionnaire/     # Questionnaire interface
│   ├── auditor/        # Auditor-specific routes
│   │   └── page.tsx           # Auditor dashboard
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Landing page
├── components/         # Reusable UI components (planned)
├── services/          # API service layer
│   └── api.ts         # API calls and data fetching
├── stores/            # Zustand state management
│   ├── company.ts     # Company-related state
│   └── auditor.ts     # Auditor-related state
└── types/             # TypeScript type definitions
    └── index.ts       # Core data models
```

## Routes

### Public Routes
- `/` - Landing page with role selection

### Company Routes
- `/company` - Company dashboard
- `/company/register` - Company registration form
- `/company/questionnaire` - Questionnaire interface

### Auditor Routes
- `/auditor` - Auditor dashboard
- `/auditor/companies/[id]` - Company evaluation (planned)

## Data Models

### Core Entities
- **Question**: Cybersecurity questions with audience targeting
- **Provision**: Compliance clauses and requirements
- **Company**: Registered company information
- **Answer**: Company responses to questions
- **Evaluation**: Auditor assessment of answers

## State Management

The application uses Zustand for state management with the following stores:

### Company Store
- Current company registration
- Questionnaire progress and answers
- Auto-save functionality
- Submission status

### Auditor Store
- Company listings
- Evaluation data
- Provision mappings
- Compliance reports

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Backend Integration

The frontend connects to a FastAPI backend running on `http://localhost:8001` by default. The API endpoints include:

- `GET /api/v1/questions` - Fetch all questions
- `GET /api/v1/provisions` - Fetch all provisions
- Company and answer management (localStorage for demo)

## Environment Variables

Create a `.env.local` file in the root directory:

```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Development Status

### ✅ Completed
- Landing page with role selection
- Company registration flow
- Company dashboard with progress tracking
- Questionnaire interface with navigation
- Auditor dashboard with company listings
- Basic state management and API integration

### 🚧 In Progress
- File upload functionality
- Auto-save implementation
- Question filtering and grouping

### 📋 Planned
- Company evaluation interface for auditors
- Provision-to-question mapping
- Compliance scoring and reporting
- Advanced question types and validation
- Real-time collaboration features
- Export functionality for reports

## Contributing

This project follows standard Next.js development practices. Key areas for contribution:

1. **UI Components**: Building reusable components for forms, tables, and data visualization
2. **State Management**: Enhancing stores with better caching and synchronization
3. **API Integration**: Improving error handling and offline support
4. **User Experience**: Adding animations, loading states, and accessibility features

## License

This project is part of the CNAV platform for cybersecurity compliance management.
