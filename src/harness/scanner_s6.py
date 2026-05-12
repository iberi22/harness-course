    # ═══════════════════════════════════════════════════════════════════
    # S6: Skills
    # ═══════════════════════════════════════════════════════════════════

    def _scan_skills(self) -> None:
        sub = Subsystem("skills", "🧠 Skills",
                        "El proyecto debe tener un catálogo de skills bien estructurado.")
        checks = []

        c = HarnessCheck("6.1", "Directorio skills/", "skills/ con subdirectorios y SKILL.md", 3.0)
        skills_dir = self.root / "skills"
        if skills_dir.is_dir():
            skill_items = [d for d in skills_dir.iterdir() if d.is_dir()]
            skill_files = list(skills_dir.rglob("SKILL.md"))
            c.passed = len(skill_files) > 0
            c.files_found = [str(d.relative_to(self.root)) for d in skill_items[:8]]
            c.detail = f"{len(skill_files)} SKILL.md en {len(skill_items)} subdirectorios"
        else:
            c.passed = False
            c.detail = "No existe directorio skills/"
        checks.append(c)

        c = HarnessCheck("6.2", "SKILL.md frontmatter", "Todos los SKILL.md tienen YAML frontmatter", 2.0)
        skill_mds = list((self.root / "skills").rglob("SKILL.md")) if (self.root / "skills").is_dir() else []
        if skill_mds:
            all_have_fm = all(self._has_valid_frontmatter(f) for f in skill_mds)
            c.passed = all_have_fm
            c.files_found = [str(f.relative_to(self.root)) for f in skill_mds[:5]]
            c.detail = f"Todos los {len(skill_mds)} SKILL.md con frontmatter" if all_have_fm else "Algunos SKILL.md sin frontmatter válido"
        else:
            c.passed = False
            c.detail = "No hay SKILL.md para validar"
        checks.append(c)

        c = HarnessCheck("6.3", "Skill provider", "Script para cargar skills dinámicamente", 1.0)
        self._check_file(c, "_registry/skill-provider.js", "_registry/skill-provider.py", "_registry/provider")
        checks.append(c)

        c = HarnessCheck("6.4", "Variedad de skills", "Al menos 5 skills en skills/", 0.5)
        if skills_dir.is_dir():
            skill_subdirs = [d.name for d in skills_dir.iterdir() if d.is_dir()]
            c.passed = len(skill_subdirs) >= 5
            c.files_found = skill_subdirs[:10]
            c.detail = f"{len(skill_subdirs)} skills"
        else:
            c.passed = False
            c.detail = "No hay skills/"
        checks.append(c)

        c = HarnessCheck("6.5", "SKILLS_SYSTEM.md", "Documentación del sistema de skills", 0.5)
        self._check_file(c, "SKILLS_SYSTEM.md", "SKILLS.md")
        checks.append(c)

        c = HarnessCheck("6.6", "Skills versionados", "Skills con versión semver en frontmatter", 0.5)
        versioned = 0
        for f in skill_mds:
            fm = self._parse_frontmatter(f)
            if fm and "version" in fm:
                versioned += 1
        if skill_mds:
            c.passed = versioned == len(skill_mds)
            c.detail = f"{versioned}/{len(skill_mds)} skills versionados"
        else:
            c.passed = False
            c.detail = "No hay skills"
        checks.append(c)

        sub.checks = checks
        self.subsystems.append(sub)
