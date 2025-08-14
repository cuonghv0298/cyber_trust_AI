# API Services Module Structure

This directory contains the modularized API services for better maintainability and organization.

## 📁 Structure

```typescript
frontend/src/services/api/
├── index.ts              # Barrel exports (recommended for new code)
├── base.ts               # Axios configuration and interceptors
├── common.ts             # Shared utilities (uploadFile, healthCheck, etc.)
├── questions.ts          # Questions API endpoints
├── provisions.ts         # Provisions API endpoints
├── companies.ts          # Companies API endpoints (backward compatibility)
├── organizations.ts      # Organizations API endpoints (matches backend)
├── answers.ts            # Answers API endpoints
├── mocks/
│   ├── index.ts          # Mock data barrel exports
│   ├── questions.ts      # Mock questions data
│   ├── provisions.ts     # Mock provisions data
│   └── organizations.ts  # Mock organizations data
└── README.md             # This file
```

## 🚀 Usage

### Option 1: Import from barrel export (Recommended)

```typescript
import { questionsApi, provisionsApi, organizationsApi, answersApi } from '@/services/api';
import { uploadFile, healthCheck } from '@/services/api';
```

### Option 2: Import directly from specific modules

```typescript
import { questionsApi } from '@/services/api/questions';
import { organizationsApi } from '@/services/api/organizations';
import { uploadFile } from '@/services/api/common';
```

### Option 3: Legacy import (Backward compatibility)

```typescript
// This still works but is deprecated for companies
import { questionsApi, companiesApi } from '@/services/api';
```

## 📋 API Modules

### `questionsApi`

- `getAll(options?: QuestionsApiOptions)` - Get all questions with pagination
- `getById(id: string)` - Get question by ID
- `create(question)` - Create new question
- `update(id, question)` - Update existing question
- `delete(id)` - Delete question

### `provisionsApi`

- `getAll()` - Get all provisions
- `getById(id)` - Get provision by ID
- `create(provision)` - Create new provision
- `update(id, provision)` - Update existing provision
- `delete(id)` - Delete provision

### `organizationsApi` (NEW - matches backend)

- `getAll(options?: OrganizationsApiOptions)` - Get all organizations with pagination
- `getById(id: string)` - Get organization by ID
- `create(orgData: OrganizationCreateData)` - Create new organization
- `update(id, orgData: OrganizationUpdateData)` - Update existing organization
- `delete(id)` - Delete organization
- `searchByName(namePattern: string)` - Search organizations by name pattern
- `searchByEmployeeCount(min: number, max: number)` - Search by employee count range

### `companiesApi` (DEPRECATED - backward compatibility)

- `register(companyData)` - Register new company
- `getAll()` - Get all companies
- `getById(id)` - Get company by ID
- `updateStatus(id, status)` - Update company status
- `searchByName(namePattern)` - Search companies by name
- `searchByEmployeeCount(min, max)` - Search by employee count

### `answersApi`

- `submit(companyId, answers)` - Submit answers for a company
- `getByCompanyId(companyId)` - Get answers for a company
- `update(companyId, questionId, answer)` - Update specific answer

### Common Utilities

- `uploadFile(file: File)` - File upload helper
- `healthCheck()` - API health check
- `handleApiError(error)` - Generic error handler

## 🛠 Configuration

The base API configuration is in `base.ts`:

- Base URL: `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'`
- Default headers: `Content-Type: application/json`
- Interceptors for auth and error handling

## 🧪 Mock Data

Mock data is available for testing when the backend is unavailable:

- `MOCK_QUESTIONS` - Sample questions
- `MOCK_PROVISIONS` - Sample provisions
- `MOCK_ORGANIZATIONS` - Sample organizations

## 🔄 Migration Guide

### From old `api.ts` structure:

```typescript
// Old way
import { questionsApi } from '@/services/api';

// New way (recommended)
import { questionsApi } from '@/services/api';  // Still works!
// OR
import { questionsApi } from '@/services/api/questions';
```

### From `companiesApi` to `organizationsApi`:

```typescript
// Old way (still works)
import { companiesApi } from '@/services/api';

// New way (recommended for new code)
import { organizationsApi } from '@/services/api';
```

No breaking changes - all existing imports continue to work!

## 🎯 Benefits

- **Maintainability**: Each API module is focused on a single resource
- **Testability**: Easier to unit test individual API modules
- **Team Collaboration**: Multiple developers can work on different APIs
- **Code Organization**: Clear separation of concerns
- **Tree Shaking**: Better bundle optimization with ES modules
- **Type Safety**: Better TypeScript support with focused interfaces
- **Backend Alignment**: New organizationsApi matches backend implementation exactly

## 📝 Notes

- The original `../api.ts` file is kept for backward compatibility
- Backend routing issues are documented in respective API modules
- Mock data automatically falls back when backend is unavailable
- `companiesApi` is deprecated - use `organizationsApi` for new development
- Organization data includes rich fields like ACRA number, annual turnover, employee count, etc.