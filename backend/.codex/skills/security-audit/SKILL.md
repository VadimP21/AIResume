---
name: security-audit
description: >
  Audit the project for authentication, authorization, secrets management,
  and common OWASP risks.
---

# Purpose

Identify security vulnerabilities.

# Checklist

## Authentication

Check:

- JWT validation
- expiration
- refresh tokens

## Authorization

Check:

- ownership
- permissions
- privilege escalation

## Secrets

Verify:

- environment variables
- secret exposure
- logging

## Database

Check:

- SQL Injection
- parameterized queries

## API

Check:

- information leakage
- sensitive responses
- unsafe error messages

## Dependencies

Identify known risky usage.

# Output Format

Critical

High

Medium

Low

Include:

- file
- vulnerability
- impact
- mitigation

# Constraints

- Do not modify code.
- Do not report theoretical issues without evidence.