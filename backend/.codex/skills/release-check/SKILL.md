---
name: release-check
description: >
  Perform a final release readiness audit.
---

# Purpose

Verify production readiness.

# Checklist

Verify:

- tests
- Ruff
- migrations
- Docker
- environment
- logging
- monitoring
- security
- performance
- API compatibility

# Output Format

## Ready

...

## Blocking Issues

...

## Recommendations

...

# Constraints

Do not deploy.

Only report findings.