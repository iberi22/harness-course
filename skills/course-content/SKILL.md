---
name: course-content
description: Crear y mantener contenido educativo del curso Harness Engineering
version: 1.0.0
license: MIT
---

# Course Content Skill

## Descripción
Skill para crear y mantener las páginas de contenido del curso Harness Engineering (harness-course site).

## Páginas del curso
- `pages/course.html` — Página principal del curso
- `pages/fundamentals.html` — Fundamentos
- `pages/design-patterns.html` — Patrones de diseño
- `pages/resources.html` — Recursos
- `pages/templates.html` — Plantillas

## Para crear una página nueva
1. Crear archivo en `pages/<name>.html`
2. Seguir el template existente (header, sidebar, content area, footer)
3. Importar CSS y JS compartidos
4. Agregar link en la navegación de todas las páginas
5. Verificar sidebar y search están sincronizados

## Convenciones
- CSS Utility-first + componentes en `css/style.css`
- JS módulos en `js/shared.js`
- Sin dependencias externas (no npm, no React, no Tailwind)
- Diseño Linear Dark consistente
