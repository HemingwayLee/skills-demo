# skills-demo

A minimal example of a [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills)
that visibly changes how Claude responds.

The skill lives at [`.claude/skills/synthetic-data/SKILL.md`](.claude/skills/synthetic-data/SKILL.md).
It teaches Claude how to generate **synthetic / test data** the way a careful data engineer would.

## What changes with the skill

Prompt: *"Make me 1000 fake users for testing."*

| | Without the skill | With the skill |
|---|---|---|
| How data is made | Often typed out by hand, or a quick one-off snippet | A seeded generator script in `scripts/` that Claude runs |
| Reproducible? | No | Yes: `--seed 42` gives the same file every time |
| Schema | Implicit | Stated up front in a table |
| Realism | Uniform random values | Skewed distributions, weighted categories |
| Edge cases | Rarely | About 5% of rows: nulls, unicode, boundary values |
| Integrity | Unchecked | Foreign keys and constraints checked after generation |
| Output in chat | Lots of rows pasted | A 5-row preview and a short "data card" |

## How to use it

### 1. Install the skill

Skills are folders that contain a `SKILL.md` file. Claude Code finds them in two places:

| Scope | Location |
|---|---|
| This project only (already set up in this repo) | `.claude/skills/synthetic-data/SKILL.md` |
| Every project on your machine | `~/.claude/skills/synthetic-data/SKILL.md` |

To use it everywhere:

```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/synthetic-data ~/.claude/skills/
```

### 2. Start Claude Code in this folder

```bash
cd skills-demo
claude
```

Type `/skills` (or ask *"what skills do you have?"*) to check that `synthetic-data` is listed.

### 3. Use it

**Automatically:** Claude reads each skill's `description` and loads the skill when your request matches it. Just ask:

```
Generate 500 fake e-commerce orders with users and products
```

**Explicitly:** call it by name:

```
/synthetic-data 200 rows of patient appointment records
```

### 4. Compare the results yourself

1. Run the prompt above in this repo, with the skill.
2. Run the same prompt in an empty folder that has no `.claude/skills`, or temporarily rename the skill folder.
3. Compare: does the output have a seed, a schema table, edge cases and a data card?

## Anatomy of a skill file

```markdown
---
name: synthetic-data                 # becomes /synthetic-data
description: Generate realistic ...  # Claude uses this to decide WHEN to load the skill
---

# Instructions                       # loaded only when the skill is used
Step-by-step rules Claude must follow...
```

Tips for writing your own:
- **The description matters most.** Include the words a user would actually type ("fake data", "mock", "test fixtures").
- **Be concrete.** "Use seed 42, write to `data/`" works better than "make it reproducible".
- **Show the output format you want** (like the data card). Claude copies examples closely.
- **Keep it short.** One skill should do one job well.
