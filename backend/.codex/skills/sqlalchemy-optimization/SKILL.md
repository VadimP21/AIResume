---
name: sqlalchemy-optimization
description: >
  Analyze SQLAlchemy ORM usage and optimize queries, relationships,
  transactions, and async performance.
---

# Purpose

Review SQLAlchemy code for correctness and performance.

# When to Use

Use:

- before release;
- after implementing new database logic;
- when performance degrades.

# Scope

Review:

- Repositories
- Models
- Relationships
- Queries
- Transactions

# Checklist

## Queries

Check:

- N+1 queries
- duplicated queries
- unnecessary joins
- full table scans
- missing pagination

## Loading

Prefer:

- selectinload()
- joinedload()

Avoid:

- lazy loading in API responses

## Transactions

Verify:

- commit()
- rollback()
- flush()
- refresh()
- transaction boundaries

## Async

Verify:

- AsyncSession
- await usage
- no sync database calls

## Performance

Check:

- indexes
- batching
- bulk operations
- serialization overhead

# Output Format

Critical

High

Medium

Low

For every issue include:

- file
- query
- impact
- recommendation

# Constraints

Do not modify code.