---
name: database-review
description: >
  Review PostgreSQL schema, models, constraints,
  relationships and database design.
---

# Purpose

Audit database design.

# Scope

Review:

- ORM models
- PostgreSQL schema
- indexes
- constraints
- relationships

# Checklist

## Schema

Check:

- normalization
- naming
- nullable fields
- defaults

## Relationships

Verify:

- OneToOne
- OneToMany
- ManyToMany

## Constraints

Check:

- PK
- FK
- UNIQUE
- CHECK

## Indexes

Verify:

- missing indexes
- duplicate indexes
- unnecessary indexes

## Data Integrity

Check:

- cascade rules
- orphan records
- consistency

# Output Format

Critical

High

Medium

Low

For every issue include:

- table/model
- description
- recommendation

# Constraints

Do not modify schema.