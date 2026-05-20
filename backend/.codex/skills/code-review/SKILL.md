---
name: code-review
description: >
  Perform a comprehensive senior-level backend code review.
---

# Purpose

Find correctness, architecture, security, and performance issues.

# Checklist

Review:

- bugs
- SOLID
- Clean Architecture
- async
- transactions
- SQLAlchemy
- security
- performance
- readability
- tests

# Severity

Critical

High

Medium

Low

# Output Format

For every issue include:

- severity
- file
- line (if available)
- description
- impact
- recommendation

# Constraints

- Never modify code.
- Do not guess.
- Report only verified findings.