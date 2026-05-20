---
name: celery-review
description: >
  Review Celery tasks, reliability,
  retries, idempotency and architecture.
---

# Purpose

Audit background jobs.

# Scope

Review:

- Celery tasks
- worker configuration
- retry strategy
- broker usage

# Checklist

Check:

- idempotency
- retries
- countdown/backoff
- error handling
- task serialization
- logging
- monitoring
- long-running tasks

# Output Format

Critical

High

Medium

Low

Include:

- task
- issue
- impact
- recommendation

# Constraints

Do not modify tasks.