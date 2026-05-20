---
name: performance-audit
description: >
  Analyze backend performance and identify bottlenecks.
---

# Purpose

Improve application performance.

# Scope

Review:

- SQL
- API
- serialization
- async
- caching

# Checklist

Database

- N+1
- indexes
- joins
- pagination

API

- payload size
- response time

Python

- duplicated computations
- unnecessary allocations

Redis

- cache opportunities

Async

- blocking calls

# Output Format

Critical

High

Medium

Low

For every issue include:

- component
- impact
- recommendation

# Constraints

Do not optimize prematurely.

Base conclusions on evidence.