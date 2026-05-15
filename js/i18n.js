/* === Harness Course — i18n Translation System === */

(function () {
  'use strict';

  var DEFAULT_LANG = 'es';

  var DICTIONARY = {
    es: {
      // Sidebar
      'brand.sub': 'Design skills for agents',
      'search.placeholder': 'Filtrar nav...',
      'nav.course': 'Curso',
      'nav.home': 'Inicio',
      'nav.fundamentals': 'Fundamentos',
      'nav.design_patterns': 'Patrones de Diseño',
      'nav.full_course': 'Curso Completo',
      'nav.subsystems': 'Subsistemas',
      'nav.scope': 'Alcance',
      'nav.instructions': 'Instrucciones',
      'nav.state': 'Estado',
      'nav.verification': 'Verificación',
      'nav.lifecycle': 'Ciclo de Vida',
      'nav.skills_poml': 'Skills',
      'nav.resources': 'Recursos',
      'nav.templates': 'Plantillas',
      'nav.case_study': 'Caso de Estudio',
      'nav.agents_flows': 'Flujos de Agentes',
      'nav.agent_recipes': 'Recetas de Agentes',
      'nav.leaderboard': 'Clasificación',
      'nav.interactive': 'Interactivo',
      'nav.tutorial': 'Tutorial',

      // Hero
      'hero.description': 'Un enfoque sistemático para diseñar el entorno alrededor de agentes de IA, extrayendo patrones de diseño de OpenClaw y aplicándolos a sistemas de trading autónomos y memoria de agentes.',
      'hero.start_course': 'Empezar Curso',
      'hero.view_patterns': 'Ver Patrones',
      'hero.full_course': 'Curso Completo',

      // Stats
      'stats.lectures': 'Lecciones',
      'stats.subsystems': 'Subsistemas',
      'stats.patterns': 'Patrones',
      'stats.gotchas': 'Trampas',
      'stats.case_studies': 'Casos de Estudio',

      // Content headings
      'content.what_is': '¿Qué es Harness Engineering?',
      'content.what_body': 'Harness Engineering es la disciplina de diseñar el entorno alrededor de un agente de IA para que pueda trabajar de manera confiable. No se trata de hacer el modelo más inteligente — se trata de crear un sistema cerrado de trabajo donde el agente tenga instrucciones claras, estado persistente, verificación automática, límites de alcance, y un ciclo de vida definido.',
      'content.subsystems_title': 'Los 5 Subsistemas del Harness',
      'content.subsystems_body': 'Todo harness se compone de cinco subsistemas fundamentales:',
      'content.subsys.instructions': 'AGENTS.md, CLAUDE.md, jerarquía de docs/ — el "recetario" que le dice al agente cómo trabajar.',
      'content.subsys.state': 'feature_list.json, progress.md, session-handoff — la "estación de preparación" que mantiene el estado.',
      'content.subsys.verification': 'Tests, type checks, comandos de verificación — la "ventana de control de calidad" que valida el trabajo.',
      'content.subsys.scope': 'One-feature-at-a-time, definition of done — los "límites de la tarea" que evitan el overreach.',
      'content.subsys.lifecycle': 'init.sh, clean-state checklists, handoff procedures — la "gestión de sesión" para continuidad.',

      'content.case_study': 'Caso de Estudio',
      'content.case_desc': 'Sistema inteligente de mantenimiento automatizado de software. MCP Server, IA agente, base de conocimiento híbrida (Neo4j + ChromaDB), dashboard Streamlit — todo orquestado con Docker. Un ejemplo completo de harness engineering aplicado.',

      'content.why': '¿Por qué importa?',
      'content.without': 'Sin Harness',
      'content.with': 'Con Harness',
      'content.without.1': 'Agente olvida preferencias entre sesiones',
      'content.without.2': 'Instrucciones gigantes que el agente ignora',
      'content.without.3': 'Sin verificación — bugs pasan desapercibidos',
      'content.without.4': 'Overreach: el agente cambia lo que no debe',
      'content.without.5': 'Sesiones rotas sin continuidad',
      'content.with.1': 'Memoria persistente con jerarquía de prioridad',
      'content.with.2': 'Progressive disclosure: la info justa a tiempo',
      'content.with.3': 'Verificación automática antes de "done"',
      'content.with.4': 'Scope definido: una feature a la vez',
      'content.with.5': 'Handoff limpio entre sesiones',

      // Footer
      'footer.text': 'Harness Engineering Course — Basado en',
      'footer.and': 'y',

      // 404
      '404.subtitle': 'Página no encontrada.',
      '404.back_home': 'Volver al inicio',
    },
    en: {
      // Sidebar
      'brand.sub': 'Design skills for agents',
      'search.placeholder': 'Filter nav...',
      'nav.course': 'Course',
      'nav.home': 'Home',
      'nav.fundamentals': 'Fundamentals',
      'nav.design_patterns': 'Design Patterns',
      'nav.full_course': 'Full Course',
      'nav.subsystems': 'Subsystems',
      'nav.scope': 'Scope',
      'nav.instructions': 'Instructions',
      'nav.state': 'State',
      'nav.verification': 'Verification',
      'nav.lifecycle': 'Lifecycle',
      'nav.skills_poml': 'Skills',
      'nav.resources': 'Resources',
      'nav.templates': 'Templates',
      'nav.case_study': 'Case Study',
      'nav.agents_flows': 'Agents Flows',
      'nav.agent_recipes': 'Agent Recipes',
      'nav.leaderboard': 'Leaderboard',
      'nav.interactive': 'Interactive',
      'nav.tutorial': 'Tutorial',

      // Hero
      'hero.description': 'A systematic approach to designing the environment around AI agents, extracting design patterns from OpenClaw and applying them to autonomous trading systems and agent memory.',
      'hero.start_course': 'Start Course',
      'hero.view_patterns': 'View Patterns',
      'hero.full_course': 'Full Course',

      // Stats
      'stats.lectures': 'Lectures',
      'stats.subsystems': 'Subsystems',
      'stats.patterns': 'Patterns',
      'stats.gotchas': 'Gotchas',
      'stats.case_studies': 'Case Studies',

      // Content headings
      'content.what_is': 'What is Harness Engineering?',
      'content.what_body': 'Harness Engineering is the discipline of designing the environment around an AI agent so it can work reliably. It is not about making the model smarter — it is about creating a closed work system where the agent has clear instructions, persistent state, automatic verification, scope limits, and a defined lifecycle.',
      'content.subsystems_title': 'The 5 Harness Subsystems',
      'content.subsystems_body': 'Every harness is composed of five fundamental subsystems:',
      'content.subsys.instructions': 'AGENTS.md, CLAUDE.md, docs/ hierarchy — the "cookbook" that tells the agent how to work.',
      'content.subsys.state': 'feature_list.json, progress.md, session-handoff — the "prep station" that keeps state.',
      'content.subsys.verification': 'Tests, type checks, verification commands — the "quality control window" that validates work.',
      'content.subsys.scope': 'One-feature-at-a-time, definition of done — the "task limits" that prevent overreach.',
      'content.subsys.lifecycle': 'init.sh, clean-state checklists, handoff procedures — the "session management" for continuity.',

      'content.case_study': 'Case Study',
      'content.case_desc': 'Intelligent automated software maintenance system. MCP Server, AI agent, hybrid knowledge base (Neo4j + ChromaDB), Streamlit dashboard — all orchestrated with Docker. A complete example of applied harness engineering.',

      'content.why': 'Why does it matter?',
      'content.without': 'Without Harness',
      'content.with': 'With Harness',
      'content.without.1': 'Agent forgets preferences between sessions',
      'content.without.2': 'Giant instructions the agent ignores',
      'content.without.3': 'No verification — bugs go unnoticed',
      'content.without.4': 'Overreach: agent changes what it should not',
      'content.without.5': 'Broken sessions without continuity',
      'content.with.1': 'Persistent memory with priority hierarchy',
      'content.with.2': 'Progressive disclosure: the right info at the right time',
      'content.with.3': 'Automatic verification before "done"',
      'content.with.4': 'Defined scope: one feature at a time',
      'content.with.5': 'Clean handoff between sessions',

      // Footer
      'footer.text': 'Harness Engineering Course — Based on',
      'footer.and': 'and',

      // 404
      '404.subtitle': 'Page not found.',
      '404.back_home': 'Back to Home',
    }
  };

  function getStoredLang() {
    try {
      return localStorage.getItem('harness-lang') || DEFAULT_LANG;
    } catch (e) {
      return DEFAULT_LANG;
    }
  }

  function setStoredLang(lang) {
    try {
      localStorage.setItem('harness-lang', lang);
    } catch (e) {
      // ignore
    }
  }

  function applyTranslations(lang) {
    var dict = DICTIONARY[lang] || DICTIONARY[DEFAULT_LANG];
    var elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (dict[key] !== undefined) {
        el.textContent = dict[key];
      }
    });

    // Handle placeholder translations
    var placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
    placeholderElements.forEach(function (el) {
      var key = el.getAttribute('data-i18n-placeholder');
      if (dict[key] !== undefined) {
        el.setAttribute('placeholder', dict[key]);
      }
    });

    // Update toggle buttons active state
    var toggleEs = document.querySelector('.lang-toggle [data-lang="es"]');
    var toggleEn = document.querySelector('.lang-toggle [data-lang="en"]');
    if (toggleEs) toggleEs.classList.toggle('active', lang === 'es');
    if (toggleEn) toggleEn.classList.toggle('active', lang === 'en');

    // Update html lang attribute
    document.documentElement.setAttribute('lang', lang);
  }

  window.setLanguage = function (lang) {
    if (!DICTIONARY[lang]) return;
    setStoredLang(lang);
    applyTranslations(lang);
  };

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      applyTranslations(getStoredLang());
    });
  } else {
    applyTranslations(getStoredLang());
  }
})();
