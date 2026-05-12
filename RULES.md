# 📐 Coding Rules — Harness Course

## HTML
- Semántico: `<nav>`, `<main>`, `<section>`, `<article>` sobre `<div>`
- Accesible: `aria-label` en nav, `alt` en imágenes, headings en orden (`h1` → `h2` → `h3`)
- Una `<h1>` por página
- Indentación: 2 espacios
- Sin inline styles — todo en `css/style.css`

## CSS
- Utility-first + componentes. Preferir:
  `.flex`, `.grid`, `.gap-*`, `.text-*`, `.p-*`, `.m-*` sobre CSS custom
- Componentes en mayúscula: `.Button`, `.Card`, `.Sidebar`
- Variables CSS en `:root` para colores, spacing, tipografía
- Design tokens: `--color-bg`, `--color-surface`, `--color-accent`, `--color-text`
- Sin `!important`
- Responsive: breakpoints a 768px y 1024px

## JavaScript
- Módulos en `js/shared.js` agrupados por función
- Preferir `const` sobre `let`, nunca `var`
- Event listeners con `addEventListener`, no inline `onclick`
- Search (⌘K), scrollspy, copy-code, accordion como módulos independientes
- Cero dependencias externas — vanilla JS only

## Definition of Done

Para que una tarea se considere COMPLETADA, debe cumplir TODOS estos criterios de aceptación:

- [ ] Código escrito según spec
- [ ] Tests pasan (python3 tests/test_html_validation.py && python3 tests/test_integrity.py)
- [ ] Sin regresiones visuales
- [ ] Documentado en AGENTS.md si aplica
- [ ] Comiteado con mensaje descriptivo (`feat:`, `fix:`, `docs:`, `chore:`)
- [ ] Sin secrets hardcodeados
- [ ] harness scan . --json no muestra nuevos errores

## Git
- Commits: `feat:`, `fix:`, `docs:`, `chore:`, `style:`, `refactor:`
- Branches: `feat/descripcion`, `fix/descripcion`
- Una feature por commit
- Sin secrets en commits (usa `.env.example`)
