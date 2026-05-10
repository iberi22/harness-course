# Contributing to Harness Course

## Qué es esto
Curso de Harness Engineering — sitio estático, cero dependencias, diseñado para que agentes de IA colaboren.

## Alcance
Aceptamos contribuciones que:
- Mejoren el contenido educativo del curso
- Optimicen el evaluador (nuevos checks, mejor precisión)
- Mantengan compatibilidad: HTML/CSS/JS vanilla, sin frameworks
- Agreguen diseño accesible y responsive

## Proceso
1. **Crea un issue** describiendo el cambio (usa labels: `content`, `tooling`, `design`, `bug`)
2. **Branch:** `feat/descripcion` o `fix/descripcion`
3. **Implementa** — si tocas CSS/JS, verifica que las otras páginas no se rompan
4. **PR contra `main`** con screenshot antes/después si es visual
5. **Review automático:** el PR ejecuta `harness scan . --ci`

## Estándares
- **HTML:** semántico, accesible (aria-labels, headings jerárquicos)
- **CSS:** Utility-first + componentes, sin !important
- **JS:** módulos en shared.js, sin dependencias externas
- **Sin secrets hardcodeados** — usa `.env.example` si necesitas
- **Una feature por PR**

## Tests
- `python3 scripts/harness_evaluator.py scan . --ci` para verificar harness
- Próximamente: HTML validator + link checker en CI
