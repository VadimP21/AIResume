---
name: api-review
description: >
  Review FastAPI HTTP endpoints for correctness, consistency, security,
  validation, and architecture.
---

# Purpose

Review the API layer without modifying code.

# Scope

Review:

- Routers
- Dependencies
- Schemas
- Authentication
- Authorization
- Exception handling

# Checklist

## API Design

Check:

- REST conventions
- endpoint naming
- HTTP methods
- status codes
- versioning

## Validation

Check:

- request models
- response models
- field constraints
- validation errors

## Authentication

Verify:

- JWT validation
- current user dependency

## Authorization

Verify:

- ownership
- roles
- permissions

## Architecture

Verify:

- no business logic in routers
- proper DI
- service usage

## Performance

Check:

- unnecessary queries
- blocking async code

# Output Format

Critical

High

Medium

Low

For every finding:

- file
- endpoint
- description
- impact
- recommendation

# Constraints

Do not modify files.