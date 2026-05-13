# 📊 Project Status — Harness Course

**Última actualización:** 10 Mayo 2026

## Resumen
- **Tipo:** Sitio estático GitHub Pages + Harness Evaluator CLI
- **Fase:** 1 (Fundación) — estructura lista, contenido en progreso
- **Score Harness:** ~~6.3% 🔴~~ → en recuperación post-fix

## Lo que funciona
- ✅ Sitio publicado en `iberi22.github.io/harness-course/`
- ✅ 5 páginas con diseño Linear Dark completo
- ✅ Search (⌘K), scrollspy, copy-code, accordion
- ✅ Harness Evaluator CLI con 48 checks + POML commands + fix generator
- ✅ Documentación del evaluador en `docs/harness-evaluator-cli.md`

## Lo que falta
- [ ] Contenido instructivo real para cada subsistema
- [ ] Tutorial interactivo
- [ ] Tests (HTML validation, link checker)
- [ ] CI/CD pipeline

## Milestones completados

### IV.3 Project Type Auto-Detection (13-May-2026)

**Descripción:** Implementación de auto-detección de tipo de proyecto para el comando `harness fix`.

**Archivos creados:**
- `src/harness/project_detector.py` — clase `ProjectDetector` con método `detect()` que infiere el tipo de proyecto (Rust, Python, Node, Trading) a partir de archivos presentes en el repo.
- `src/harness/fix-templates/{rust,python,node,trading}/*.poml` — 14 templates POML específicos por tipo de proyecto.

**Funcionalidad:**
- Nuevo flag CLI: `harness fix . --auto`
- Selección automática del template set adecuado según el proyecto detectado.

**Estado:** ✅ Completado

## Riesgos
- El contenido educativo es la parte más cara de producir (requiere LLM)
- El evaluador necesita testeo en más proyectos para validar checks
