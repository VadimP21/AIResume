---
name: project-analysis
description: >
  Analyze the project architecture, request flow, module responsibilities,
  dependencies, and integrations without modifying the code.
---

# Purpose

Understand how the project works before making changes.

This skill is intended for initial project exploration, onboarding, or
analysis before implementing new functionality.

# When to Use

Use this skill:

- at the beginning of a new session;
- before implementing a feature;
- before investigating a bug;
- before performing a large refactoring.

# Scope

Analyze:

- project structure;
- architecture;
- module responsibilities;
- request flow;
- dependency injection;
- database access;
- authentication;
- external integrations;
- background tasks.

Do not modify files.

# Checklist

## Architecture

Identify:

- architectural style;
- project layers;
- module boundaries;
- dependency flow.

## Request Flow

Describe:

Client

↓

Middleware

↓

Router

↓

Service

↓

Repository

↓

Database

↓

Response

## Modules

Explain responsibility of each module.

## Authentication

Describe:

- JWT flow
- Refresh tokens
- Authorization
- Current user loading

## Database

Describe:

- models
- relationships
- transactions
- repositories

## External Services

Identify:

- Redis
- Celery
- Docker
- APIs

# Output Format

Return:

## Architecture

...

## Request Flow

...

## Modules

...

## Database

...

## Authentication

...

## External Integrations

...

## Risks

...

# Constraints

- Do not modify code.
- Do not speculate.
- Base conclusions only on inspected code.