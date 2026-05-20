---
name: async-audit
description: >
  Audit asynchronous code for correctness, performance,
  concurrency issues, and SQLAlchemy async usage.
---

# Purpose

Review async implementation.

# Scope

Review:

- async functions
- AsyncSession
- awaits
- background tasks
- concurrency

# Checklist

Check:

- missing await
- blocking I/O
- sync code inside async
- session lifetime
- connection leaks
- race conditions
- cancellation handling
- timeout handling

# Output Format

Critical

High

Medium

Low

For every issue include:

- file
- description
- impact
- recommendation

# Constraints

Do not modify code.