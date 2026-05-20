---
name: docker-review
description: >
  Review Docker configuration,
  container security and deployment readiness.
---

# Purpose

Audit containerization.

# Scope

Review:

- Dockerfile
- docker-compose
- environment variables

# Checklist

Check:

- image size
- build stages
- secrets
- healthchecks
- volumes
- networking
- non-root user
- restart policy

# Output Format

Critical

High

Medium

Low

Include:

- file
- issue
- recommendation

# Constraints

Do not modify configuration.