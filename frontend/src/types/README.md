# Types Module Structure

This directory contains well-organized TypeScript type definitions for the entire frontend application.

## 📁 Structure

```
frontend/src/types/
├── index.ts              # Barrel exports (recommended for imports)
├── question.ts           # Question-related interfaces
├── provision.ts          # Provision-related interfaces
├── answer.ts             # Answer-related interfaces
├── organization.ts       # Organization/Company interfaces
├── evaluation.ts         # Evaluation and compliance interfaces
├── form.ts               # Form data interfaces
├── common.ts             # Shared UI and API types
├── constants.ts          # Type-safe constants
└── README.md             # This file
```

## 🎯 Type Organization

### Core Data Models
- **`question.ts`** - `Question` interface matching backend
- **`provision.ts`** - `Provision` interface matching backend
- **`answer.ts`** - `Answer` interface for questionnaire responses
- **`organization.ts`** - `Organization`, `Company`, and related create/update data types

### Business Logic Types
- **`evaluation.ts`** - `Evaluation`, `ProvisionEvaluation`, `QuestionEvaluation`, `ComplianceReport`
- **`form.ts`** - `QuestionnaireFormData` and other form-related interfaces

### Infrastructure Types
- **`common.ts`** - `UserRole`, `ApiResponse<T>` for shared functionality
- **`constants.ts`** - `AUDIENCE_OPTIONS`, `GROUP_TAG_OPTIONS` and their derived types

## 🚀 Usage

### Recommended: Import from barrel export

```typescript
import { Question, Organization, Evaluation, ApiResponse } from '@/types';
```

### Alternative: Import from specific files (if needed)

```typescript
import { Question } from '@/types/question';
import { Organization } from '@/types/organization';
import { Evaluation } from '@/types/evaluation';
```

## 📋 Interface Relationships

```
Organization
├── Company (extends Organization)
├── OrganizationCreateData
└── OrganizationUpdateData

Question
├── Used in QuestionEvaluation
└── Referenced by Answer.questionId

Evaluation
├── QuestionEvaluation (combines Question + Answer + Evaluation)
├── ProvisionEvaluation (combines Provision + QuestionEvaluation[])
└── ComplianceReport (combines Company + ProvisionEvaluation[])
```

## 🔧 Type Safety Features

### Constants with Type Safety
```typescript
// Strongly typed options
import { AUDIENCE_OPTIONS, AudienceOption } from '@/types';
const audience: AudienceOption = 'Owner'; // ✅ Type-safe
const invalid: AudienceOption = 'Invalid'; // ❌ TypeScript error
```

### Generic API Responses
```typescript
import { ApiResponse, Question } from '@/types';
const response: ApiResponse<Question[]> = await questionsApi.getAll();
```

### Form Type Safety
```typescript
import { QuestionnaireFormData } from '@/types';
const formData: QuestionnaireFormData = {
  "question-1": { answer: "Yes", files: undefined },
  "question-2": { answer: "No", files: fileList }
};
```

## 🔄 Migration from Monolithic Types

### Before (single file)
```typescript
// All 100+ lines in types/index.ts
export interface Question { ... }
export interface Organization { ... }
export interface Evaluation { ... }
// ... many more interfaces
```

### After (modular)
```typescript
// types/question.ts
export interface Question { ... }

// types/organization.ts  
export interface Organization { ... }

// types/evaluation.ts
export interface Evaluation { ... }

// types/index.ts (barrel export)
export * from './question';
export * from './organization';
export * from './evaluation';
```

## ✅ Benefits

- **Maintainability**: Easy to find and modify specific interface types
- **Team Collaboration**: Multiple developers can work on different type files
- **Logical Grouping**: Related interfaces are co-located
- **Import Flexibility**: Use barrel exports or specific imports as needed
- **Type Safety**: Strong TypeScript support with cross-references
- **Documentation**: Each file focuses on a specific domain

## 🎨 Best Practices Followed

- **Single Responsibility**: Each file handles one domain of types
- **Cross-references**: Proper imports between type files when needed
- **Barrel Exports**: Convenient single import point via `index.ts`
- **Naming Conventions**: Clear, descriptive interface names
- **Backend Alignment**: Types match backend API response models
- **Future-proof**: Easy to extend with new type files as needed