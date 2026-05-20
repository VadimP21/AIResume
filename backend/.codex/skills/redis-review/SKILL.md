---
name: redis-review
description: >
  Review Redis usage, key management,
  TTL, caching strategy and concurrency.
---

# Purpose

Audit Redis usage.

# Scope

Review:

- cache
- refresh tokens
- locks
- pub/sub

# Checklist

Check:

- TTL
- key naming
- serialization
- cache invalidation
- race conditions
- memory usage
- security

# Output Format

Critical

High

Medium

Low

For every issue include:

- key/component
- impact
- recommendation

# Constraints

Do not modify code.