---
name: feature-development
description: >
  Implement new functionality following the existing architecture and coding
  standards.
---

# Purpose

Implement a new feature with minimal impact on existing code.

# When to Use

Use when:

- adding endpoints;
- integrating external services;
- implementing business logic;
- extending existing modules.

# Workflow

1. Analyze existing implementation.
2. Explain the solution.
3. List affected files.
4. Wait for confirmation if architecture changes.
5. Implement.
6. Run tests.
7. Run Ruff.
8. Self-review.
9. Summarize changes.

# Checklist

Verify:

- architecture consistency;
- SOLID;
- transaction boundaries;
- async correctness;
- validation;
- security;
- tests.

# Output Format

Return:

## Plan

...

## Files

...

## Implementation Summary

...

## Risks

...

## Verification

- Ruff
- pytest

# Constraints

- Do not modify unrelated code.
- Preserve backward compatibility unless requested.
