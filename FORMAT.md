# Skill Creation File Format Specification

A Skill Creation File is a **recipe for building a skill** — it tells an AI agent how to *write* a Skill File for a specific domain. It is NOT a skill itself.

---

## Quick Reference

| Section | Required | Min Length | Purpose |
|---|---|---|---|
| `name` (frontmatter) | ✅ | 10 chars | Searchable title |
| `description` (frontmatter) | ✅ | 50 chars | Search index — what gets matched |
| `tags` (frontmatter) | ✅ | 1 tag | Fallback search signal |
| `## What This Builds` | ✅ | 100 chars | Executive summary for synthesis |
| `## Implementation Approach` | ✅ | 200 chars | The core — step-by-step instructions |
| `## Key Concepts` | ❌ | — | Domain knowledge the agent needs |
| `## Edge Cases & Mitigations` | ❌ | — | Highest-value signal per token |
| `## Known Limitations` | ❌ | — | Points to potential child files |
| `## Code Patterns` | ❌ | — | Makes it concrete for technical users |
| `## Pairing Suggestions` | ❌ | — | Cross-linking to other files |
| `## How This Was Made` | ❌ | — | Provenance / attribution |

---

## The Complete Format

```markdown
---
name: "Your Skill Creation File Name"
description: >
  One paragraph describing what skill this builds, who it's
  for, and what domain knowledge it captures. This paragraph
  is the SEARCH INDEX — make it descriptive and keyword-rich.
tags: [relevant, tags, separated, by, commas, meta, creation-file]
category: coding | data_analysis | other
difficulty: beginner | intermediate | advanced
estimated_time: "20-30 minutes"
---

## What This Builds

A short paragraph describing what the output skill will do.

## Key Concepts

Domain knowledge the agent needs before writing the skill.

## Implementation Approach

Step-by-step. Be specific. Tell the agent what to do and avoid.

## What a Naive Agent Gets Wrong

| Mistake | Why It Happens | Fix |
|---|---|---|
| Assumes clean data | Training data is clean | Add validation step |

## Edge Cases & Mitigations

| Edge Case | Mitigation |
|---|---|
| Empty input | Return early with clear message |

## Known Limitations

- Does not handle X (see child: Specialized X)

## Code Patterns

```python
def example():
    pass
```

## Pairing Suggestions

Works well with Related File A.

## How This Was Made

Reverse engineered from Source Skill.
```

---

## 3-Tier Loading

| Level | What's Loaded | Token Cost | Trigger |
|---|---|---|---|
| 1 | Frontmatter (name, description, tags) | ~50 | Always — search index |
| 2 | Body (What This Builds, Approach, Key Concepts) | ~500-2000 | API extraction / synthesis |
| 3 | Extras (Code, Edge Cases, Limitations, Pairing) | ~1000-3000 | File detail page view |

---

## Best Practices

1. **Specific, not generic** — "SQL query builder for PostgreSQL with CTE support" beats "SQL query builder"
2. **Agent-first language** — write for an AI, not a human. Bullet points, clear sections, explicit thresholds
3. **Include the failure modes** — files that document what doesn't work are more valuable
4. **Code patterns as examples** — even pseudocode helps synthesis
5. **Pairing suggestions** — cross-linking increases both files' extraction counts
6. **Keep description under 300 chars** — longer gets truncated in search results
7. **Use YAML frontmatter tags** — power the fallback search
