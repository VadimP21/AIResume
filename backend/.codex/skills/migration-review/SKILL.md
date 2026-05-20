---
name: migration-review
description: >
  Review Alembic migrations for correctness,
  safety and production readiness.
---

# Purpose

Audit database migrations.

# Scope

Review:

- Alembic revisions
- schema changes
- data migrations

# Checklist

Check:

- downgrade support
- indexes
- constraints
- data safety
- locking risks
- backward compatibility

# Output Format

Critical

High

Medium

Low

Include:

- migration
- issue
- recommendation

# Constraints

Do not modify migrations.