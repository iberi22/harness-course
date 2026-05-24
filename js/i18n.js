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
      'nav.community': 'Comunidad',

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

      // Community page
      'community.title': 'Community Harness Scores',
      'community.description': 'A community-driven harness score submission system. Submit your project, get it scanned, and compare your agent-readiness with the community.',
      'community.tag_vision': 'vision',
      'community.tag_open': 'open-registry',
      'community.tag_community': 'community',
      'community.vision_title': 'Vision',
      'community.vision_body': 'We envision a public registry where any developer or team can submit their project\'s Harness Score via GitHub issues. Once submitted, the score is reviewed, verified, and listed so the community can benchmark against each other. This transparent, open-source approach helps raise the bar for agent-readiness across the entire ecosystem. The <strong>official leaderboard</strong> showcases top-tier curated repos, while the <strong>community leaderboard</strong> welcomes contributions from anyone who wants to measure and improve their project.',
      'community.tag_guide': 'guide',
      'community.tag_steps': 'steps',
      'community.submit_title': 'How to Submit',
      'community.submit_intro': 'Follow these simple steps to get your project listed in the community leaderboard:',
      'community.step1_title': 'Scan your project',
      'community.step1_desc': 'Run harness scan . --json in your project root to generate a complete Harness Score report with subsystem breakdowns.',
      'community.step2_title': 'Open a GitHub issue',
      'community.step2_desc': 'Go to github.com/iberi22/harness-course/issues and create a new issue using the "Submit Score" template.',
      'community.step3_title': 'Paste your results',
      'community.step3_desc': 'Include the full JSON output from the scan along with your repository URL. Our maintainers will verify the score and add it to the community list.',
      'community.step4_title': 'Get listed',
      'community.step4_desc': 'Once approved, your project appears in the community leaderboard below. You can resubmit anytime your score improves!',
      'community.tag_table': 'table',
      'community.tag_submissions': 'submissions',
      'community.scores_title': 'Community Scores',
      'community.scores_desc': 'Below are community-submitted projects. The <strong>official leaderboard</strong> remains the primary benchmark; this table is a growing collection of community-driven scores. Submit yours today!',
      'community.table_project': 'Project',
      'community.table_score': 'Score',
      'community.table_date': 'Date Submitted',
      'community.table_status': 'Status',
      'community.table_note': 'Scores are verified by maintainers. The official leaderboard at /leaderboard contains curated top-tier projects.',
      'community.tag_benefits': 'benefits',
      'community.tag_why': 'why',
      'community.benefits_title': 'Benefits of Participating',
      'community.benefits_intro': 'Why should you submit your project to the community registry? Here\'s what you gain:',
      'community.benefit1_title': 'Bragging Rights',
      'community.benefit1_desc': 'Show the world your project\'s agent-readiness score. A high Harness Score is a badge of quality that sets your project apart.',
      'community.benefit2_title': 'Discoverability',
      'community.benefit2_desc': 'Get listed alongside other agent-ready projects. Developers and agents looking for well-structured repos will find yours.',
      'community.benefit3_title': 'Improve Agent-Readiness',
      'community.benefit3_desc': 'The process of running the scanner and addressing its recommendations directly improves your project\'s ability to be operated by AI agents.',
      'community.benefit4_title': 'Contribute to Standards',
      'community.benefit4_desc': 'Help build open-source agent engineering standards. The more projects in the registry, the better we can define what "agent-ready" means.',
      'community.tag_github': 'github',
      'community.tag_submit': 'submit',
      'community.github_title': 'GitHub Integration',
      'community.github_body': 'Ready to submit your project? Click the button below to create a new issue with our pre-filled score submission template. Fill in your details and a maintainer will review your submission.',
      'community.submit_heading': 'Submit Your Project',
      'community.submit_prompt': 'Use the issue template to submit your Harness Score JSON and repository details.',
      'community.submit_button': '📤 Submit Score',
      'community.github_note': 'Make sure your repository is public so our maintainers can verify the scan results.',
      'community.faq_title': 'Preguntas Frecuentes',
      'community.faq_intro': 'Preguntas comunes sobre el registro comunitario de scores.',
      'community.faq1_q': '¿Cuánto tarda la verificación?',
      'community.faq1_a': 'Generalmente 24-48 horas. Nuestros mantenedores revisan tu scan y lo validan contra tu repositorio antes de listarlo.',
      'community.faq2_q': '¿Puedo enviar múltiples veces?',
      'community.faq2_a': '¡Por supuesto! Cada vez que tu Harness Score mejore, abre un nuevo issue con tu scan actualizado. Actualizaremos tu listing.',
      'community.faq3_q': '¿Mi score es público?',
      'community.faq3_a': 'Sí. Todos los scores enviados se muestran públicamente en esta página. Al enviar, consientes que tu proyecto, score y URL sean listados.',
      'community.faq4_q': '¿Si mi proyecto es privado?',
      'community.faq4_a': 'Actualmente solo verificamos repositorios públicos. Los repos privados no pueden ser validados por nuestros mantenedores.',
      'community.faq5_q': '¿Puedo enviar el proyecto de otra persona?',
      'community.faq5_a': 'Solo envía proyectos que te pertenezcan o para los que tengas permiso explícito del dueño. Los envíos no autorizados serán eliminados.',
      'community.related_title': 'Related Resources',
      'community.related_leaderboard_title': '🏆 Official Leaderboard',
      'community.related_leaderboard_desc': 'View the top-ranked projects curated by the Harness Engineering team.',
      'community.related_tutorial_title': '🎮 Interactive Tutorial',
      'community.related_tutorial_desc': 'Learn how to take your project from 45% to 80%+ with a guided tutorial.',
      'community.related_casestudy_title': '🧠 Case Study',
      'community.related_casestudy_desc': 'How agents-flows-recipes achieved a high Harness Score — lessons learned.',
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
      'nav.community': 'Community',

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

      // Community page (EN)
      'community.title': '🌐 Community Harness Scores',
      'community.description': 'A community-driven harness score submission system. Submit your project, get it scanned, and compare your agent-readiness with the community.',
      'community.tag_vision': 'vision',
      'community.tag_open': 'open-registry',
      'community.tag_community': 'community',
      'community.vision_title': 'Vision',
      'community.vision_body': 'We envision a public registry where any developer or team can submit their project\'s Harness Score via GitHub issues. Once submitted, the score is reviewed, verified, and listed so the community can benchmark against each other. This transparent, open-source approach helps raise the bar for agent-readiness across the entire ecosystem. The <strong>official leaderboard</strong> showcases top-tier curated repos, while the <strong>community leaderboard</strong> welcomes contributions from anyone who wants to measure and improve their project.',
      'community.tag_guide': 'guide',
      'community.tag_steps': 'steps',
      'community.submit_title': 'How to Submit',
      'community.submit_intro': 'Follow these simple steps to get your project listed in the community leaderboard:',
      'community.step1_title': 'Scan your project',
      'community.step1_desc': 'Run harness scan . --json in your project root to generate a complete Harness Score report with subsystem breakdowns.',
      'community.step2_title': 'Open a GitHub issue',
      'community.step2_desc': 'Go to github.com/iberi22/harness-course/issues and create a new issue using the "Submit Score" template.',
      'community.step3_title': 'Paste your results',
      'community.step3_desc': 'Include the full JSON output from the scan along with your repository URL. Our maintainers will verify the score and add it to the community list.',
      'community.step4_title': 'Get listed',
      'community.step4_desc': 'Once approved, your project appears in the community leaderboard below. You can resubmit anytime your score improves!',
      'community.tag_table': 'table',
      'community.tag_submissions': 'submissions',
      'community.scores_title': 'Community Scores',
      'community.scores_desc': 'Below are community-submitted projects. The <strong>official leaderboard</strong> remains the primary benchmark; this table is a growing collection of community-driven scores. Submit yours today!',
      'community.table_project': 'Project',
      'community.table_score': 'Score',
      'community.table_date': 'Date Submitted',
      'community.table_status': 'Status',
      'community.table_note': 'Scores are verified by maintainers. The official leaderboard at /leaderboard contains curated top-tier projects.',
      'community.tag_benefits': 'benefits',
      'community.tag_why': 'why',
      'community.benefits_title': 'Benefits of Participating',
      'community.benefits_intro': 'Why should you submit your project to the community registry? Here\'s what you gain:',
      'community.benefit1_title': 'Bragging Rights',
      'community.benefit1_desc': 'Show the world your project\'s agent-readiness score. A high Harness Score is a badge of quality that sets your project apart.',
      'community.benefit2_title': 'Discoverability',
      'community.benefit2_desc': 'Get listed alongside other agent-ready projects. Developers and agents looking for well-structured repos will find yours.',
      'community.benefit3_title': 'Improve Agent-Readiness',
      'community.benefit3_desc': 'The process of running the scanner and addressing its recommendations directly improves your project\'s ability to be operated by AI agents.',
      'community.benefit4_title': 'Contribute to Standards',
      'community.benefit4_desc': 'Help build open-source agent engineering standards. The more projects in the registry, the better we can define what "agent-ready" means.',
      'community.tag_github': 'github',
      'community.tag_submit': 'submit',
      'community.github_title': 'GitHub Integration',
      'community.github_body': 'Ready to submit your project? Click the button below to create a new issue with our pre-filled score submission template. Fill in your details and a maintainer will review your submission.',
      'community.submit_heading': 'Submit Your Project',
      'community.submit_prompt': 'Use the issue template to submit your Harness Score JSON and repository details.',
      'community.submit_button': '📤 Submit Score',
      'community.github_note': 'Make sure your repository is public so our maintainers can verify the scan results.',
      'community.faq_title': 'Frequently Asked Questions',
      'community.faq_intro': 'Common questions about the community score registry.',
      'community.faq1_q': 'How long does verification take?',
      'community.faq1_a': 'Typically 24-48 hours. Our maintainers review your scan output and validate it against your repository before listing.',
      'community.faq2_q': 'Can I submit multiple times?',
      'community.faq2_a': 'Absolutely! Each time your Harness Score improves, open a new issue with your updated scan. We\'ll update your listing.',
      'community.faq3_q': 'Is my score public?',
      'community.faq3_a': 'Yes. All submitted scores are displayed publicly on this page. By submitting, you consent to having your project name, score, and URL listed.',
      'community.faq4_q': 'What if my project is private?',
      'community.faq4_a': 'We currently only verify public repositories. Private repos cannot be validated by our maintainers.',
      'community.faq5_q': 'Can I submit someone else\'s project?',
      'community.faq5_a': 'Only submit projects you own or have explicit permission from the owner. Unauthorized submissions will be removed.',
      'community.related_title': 'Related Resources',
      'community.related_leaderboard_title': '🏆 Official Leaderboard',
      'community.related_leaderboard_desc': 'View the top-ranked projects curated by the Harness Engineering team.',
      'community.related_tutorial_title': '🎮 Interactive Tutorial',
      'community.related_tutorial_desc': 'Learn how to take your project from 45% to 80%+ with a guided tutorial.',
      'community.related_casestudy_title': '🧠 Case Study',
      'community.related_casestudy_desc': 'How agents-flows-recipes achieved a high Harness Score — lessons learned.',
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
