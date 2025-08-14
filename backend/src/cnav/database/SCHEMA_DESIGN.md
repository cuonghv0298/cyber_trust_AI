# Clause Schema Design

## Overview

This document describes the database schema design for clauses that support the identifier format `category_id.clause_identifier` (e.g., "1.4a", "2.3b").

## Schema Structure

### RequirementCategory Table

```sql
CREATE TABLE requirement_categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Clause Table

```sql
CREATE TABLE clauses (
    id INTEGER PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES requirement_categories(id),
    clause_identifier VARCHAR(10) NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, clause_identifier)
);
```

### Question Table

```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    audience VARCHAR NOT NULL CHECK (audience IN ('HR', 'IT', 'Owner')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Question-Clause Mapping Table (Many-to-Many)

```sql
CREATE TABLE question_clause_mapping (
    question_id INTEGER NOT NULL REFERENCES questions(id),
    clause_id INTEGER NOT NULL REFERENCES clauses(id),
    PRIMARY KEY (question_id, clause_id)
);
```

## Key Features

### 1. Identifier Format Support

- **Category ID**: Integer from the `requirement_categories.id`
- **Clause Identifier**: String like "4a", "1b", "2c" stored in `clause_identifier`
- **Full Identifier**: Computed as `category_id.clause_identifier` (e.g., "1.4a")

### 2. Hybrid Property

The `full_identifier` hybrid property provides both Python and SQL access:

```python
# Python access
clause = session.query(Clause).first()
print(clause.full_identifier)  # "1.4a"

# SQL expression (for queries)
# Note: Direct querying with hybrid properties requires careful handling
```

### 3. Unique Constraints

- **Primary Key**: Auto-incrementing `id` for database efficiency
- **Unique Constraint**: `(category_id, clause_identifier)` ensures no duplicate clause identifiers within a category

### 4. Audience Types

Questions are categorized by audience using an enum:

```python
class AudienceType(enum.Enum):
    HR = "HR"
    IT = "IT"
    OWNER = "Owner"
```

### 5. Many-to-Many Relationship

Questions and clauses have a many-to-many relationship:
- One question can map to multiple clauses
- One clause can be associated with multiple questions
- The relationship is managed through the `question_clause_mapping` table

### 6. Helper Methods

#### Clause Methods

##### `get_by_full_identifier(session, full_identifier)`
```python
clause = Clause.get_by_full_identifier(session, "1.4a")
```

##### `create_from_identifier(session, full_identifier, name, description)`
```python
clause = Clause.create_from_identifier(session, "1.4a", "Access Control", "Description")
```

##### `add_question(question)` / `remove_question(question)`
```python
clause.add_question(question)
clause.remove_question(question)
```

##### `get_questions_by_audience(audience_type)`
```python
it_questions = clause.get_questions_by_audience(AudienceType.IT)
```

#### Question Methods

##### `get_by_audience(session, audience_type)`
```python
hr_questions = Question.get_by_audience(session, AudienceType.HR)
```

##### `add_clause(clause)` / `remove_clause(clause)`
```python
question.add_clause(clause)
question.remove_clause(clause)
```

## Usage Examples

### Creating Categories and Clauses

```python
# Create category
category = RequirementCategory(
    name="Access Control",
    description="Requirements for access control"
)
session.add(category)
session.flush()  # Get the ID

# Create clause
clause = Clause(
    category_id=category.id,
    clause_identifier="4a",
    name="User Authentication",
    description="Users must authenticate before accessing systems"
)
session.add(clause)
session.commit()

# The full identifier will be "1.4a" (assuming category.id = 1)
print(clause.full_identifier)  # "1.4a"
```

### Creating Questions

```python
# Create a question with audience
question = Question(
    name="Is there a formal process to grant and revoke access?",
    description="Access control process verification",
    audience=AudienceType.IT
)
session.add(question)
session.commit()
```

### Creating Many-to-Many Relationships

```python
# Create relationships between questions and clauses
question.add_clause(clause1)  # Add clause to question
question.add_clause(clause2)  # Add another clause

# Or from the clause side
clause.add_question(question)  # Add question to clause

session.commit()
```

### Querying Clauses

```python
# By full identifier
clause = Clause.get_by_full_identifier(session, "1.4a")

# By category
clauses = session.query(Clause).filter(Clause.category_id == 1).all()

# All clauses with relationships
category = session.query(RequirementCategory).first()
for clause in category.clauses:
    print(f"{clause.full_identifier}: {clause.name}")
```

### Querying Questions

```python
# By audience type
hr_questions = Question.get_by_audience(session, AudienceType.HR)
it_questions = Question.get_by_audience(session, "IT")  # Can use string too

# Questions for a specific clause
for question in clause.questions:
    print(f"[{question.audience.value}] {question.name}")

# Questions for a clause filtered by audience
it_questions_for_clause = clause.get_questions_by_audience(AudienceType.IT)
```

### Complex Queries

```python
# Find all IT questions mapped to Access Control clauses
it_access_questions = session.query(Question).join(
    Question.clauses
).filter(
    Question.audience == AudienceType.IT,
    Clause.category_id == access_control_category.id
).all()

# Find clauses with questions from multiple audiences
for clause in session.query(Clause).all():
    audiences = set(q.audience for q in clause.questions)
    if len(audiences) > 1:
        print(f"Clause {clause.full_identifier} has questions from: {[a.value for a in audiences]}")
```

## Benefits

1. **Flexibility**: Supports any clause identifier format within categories
2. **Uniqueness**: Ensures no duplicate identifiers within categories
3. **Efficiency**: Uses integer primary keys for performance
4. **Relationships**: Proper foreign key relationships with cascade delete
5. **Extensibility**: Easy to add new fields or modify existing ones
6. **Many-to-Many Support**: Questions can map to multiple clauses and vice versa
7. **Audience Segmentation**: Questions are categorized by audience (HR, IT, Owner)
8. **Rich Querying**: Support for complex queries across relationships
9. **Data Integrity**: Proper constraints and enum validation

## Migration Considerations

If migrating from an existing schema:

1. **Data Migration**: Extract category and clause parts from existing full identifiers
2. **Constraint Validation**: Ensure uniqueness constraints don't conflict
3. **Application Updates**: Update code to use new helper methods
4. **Testing**: Verify all identifier formats work correctly

## Examples of Supported Identifiers

- "1.4a" → Category 1, Clause "4a"
- "2.10b" → Category 2, Clause "10b"
- "3.1" → Category 3, Clause "1"
- "15.2c" → Category 15, Clause "2c"

The schema is flexible enough to handle various identifier formats while maintaining data integrity and query performance. 