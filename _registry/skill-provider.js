#!/usr/bin/env node
/**
 * Skill Provider for Harness Course
 * Dynamic skill loading and discovery.
 *
 * Usage:
 *   node _registry/skill-provider.js list          # List all skills
 *   node _registry/skill-provider.js get <name>    # Get skill content
 *   node _registry/skill-provider.js path <name>   # Get skill path
 */

const fs = require("fs");
const path = require("path");

const SKILLS_DIR = path.join(__dirname, "..", "skills");

function listSkills() {
  if (!fs.existsSync(SKILLS_DIR)) return [];
  return fs.readdirSync(SKILLS_DIR).filter((d) => {
    const skillFile = path.join(SKILLS_DIR, d, "SKILL.md");
    return fs.statSync(path.join(SKILLS_DIR, d)).isDirectory() && fs.existsSync(skillFile);
  });
}

function getSkill(name) {
  const skillPath = path.join(SKILLS_DIR, name, "SKILL.md");
  if (!fs.existsSync(skillPath)) return null;
  return fs.readFileSync(skillPath, "utf-8");
}

function getSkillPath(name) {
  const p = path.join(SKILLS_DIR, name, "SKILL.md");
  return fs.existsSync(p) ? p : null;
}

const cmd = process.argv[2];
const arg = process.argv[3];

switch (cmd) {
  case "list":
    console.log(listSkills().join("\n"));
    break;
  case "get":
    const content = getSkill(arg);
    if (content) console.log(content);
    else { console.error(`Skill '${arg}' not found`); process.exit(1); }
    break;
  case "path":
    const p = getSkillPath(arg);
    if (p) console.log(p);
    else { console.error(`Skill '${arg}' not found`); process.exit(1); }
    break;
  default:
    console.log("Usage: skill-provider.js <list|get|path> [name]");
}
