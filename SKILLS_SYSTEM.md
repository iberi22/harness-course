# SKILLS_SYSTEM.md — Harness Course Skill System

## Overview
This project uses skills and POML recipes for agent task automation. Skills are organized in `skills/` directory with SKILL.md frontmatter. POML recipes in `poml/` provide structured prompts for common tasks.

## Directory Structure
```
skills/
  harness-evaluator-skill/    # Skill to run harness CLI tools
poml/
  harness-scan.poml           # Scan projects with harness CLI
  harness-fix.poml            # Auto-fix projects with harness fix
_registry/
  manifest.yaml               # Central skill catalog
schema/
  recipe.schema.yaml          # POML validation schema
```

## Creating a New Skill
1. Create `skills/<skill-name>/SKILL.md`
2. Add YAML frontmatter with `name`, `description`, `version`
3. Add to `_registry/manifest.yaml`
4. Verify with `harness scan . --json`

## Creating a New POML Recipe
1. Create `poml/<recipe-name>.poml`
2. Follow the POML format (see schema/recipe.schema.yaml)
3. Add XML tags: `<poml>`, `<let name="...">`, `<role>`, `<task>`, `<output-format>`
4. Validate with `harness poml validate .`

## Versioning
All skills should have a version in frontmatter following semver (major.minor.patch).
