#!/usr/bin/env python3
"""
Harness Context Auditor — Deterministic Runtime Inspector for AI Agent Harnesses

Detects what harness is running, analyzes prompt boundaries, injection vectors,
context leakage, tool scoping, and security posture. Zero LLM calls — pure logic.

Usage:
  python3 scripts/harness_auditor.py                    # Auto-detect current harness
  python3 scripts/harness_auditor.py --self              # Same, explicit
  python3 scripts/harness_auditor.py --path /path/to     # Scan a project dir
  python3 scripts/harness_auditor.py --json              # Machine-readable output
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════
# DETECTION: What harness is running?
# ═══════════════════════════════════════════════════════════════════════

HARNESS_SIGNATURES = {
    "hermes-agent": {
        "signals": [
            lambda: os.environ.get("HERMES_HOME") is not None,
            lambda: os.environ.get("_HERMES_GATEWAY") is not None,
            lambda: Path.home().joinpath(".hermes", "config.yaml").exists(),
        ],
        "config_paths": ["~/.hermes/config.yaml", "~/.hermes/.env"],
        "agent_file": "AGENTS.md",
        "home_var": "HERMES_HOME",
    },
    "opencode": {
        "signals": [
            lambda: os.environ.get("OPENCODE_HOME") is not None,
            lambda: Path.home().joinpath(".opencode", "config.yaml").exists(),
        ],
        "config_paths": ["~/.opencode/config.yaml"],
        "agent_file": "AGENTS.md",
        "home_var": "OPENCODE_HOME",
    },
    "claude-code": {
        "signals": [
            lambda: os.environ.get("CLAUDE_CODE_HOME") is not None,
            lambda: Path.home().joinpath(".claude", "claude.md").exists(),
        ],
        "config_paths": ["~/.claude/claude.md", "CLAUDE.md"],
        "agent_file": "CLAUDE.md",
        "home_var": "CLAUDE_CODE_HOME",
    },
    "codex-cli": {
        "signals": [
            lambda: Path.home().joinpath(".codex", "auth.json").exists(),
        ],
        "config_paths": ["~/.codex/auth.json"],
        "agent_file": "AGENTS.md",
        "home_var": "CODEX_HOME",
    },
    "gemini-cli": {
        "signals": [
            lambda: Path.home().joinpath(".config", "gemini", "config.yaml").exists(),
        ],
        "config_paths": ["~/.config/gemini/config.yaml"],
        "agent_file": "AGENTS.md",
        "home_var": "GEMINI_HOME",
    },
    "opencaw": {
        "signals": [
            lambda: Path.home().joinpath(".zeroclaw", "config.toml").exists(),
        ],
        "config_paths": ["~/.zeroclaw/config.toml"],
        "agent_file": "AGENTS.md",
        "home_var": "ZEROCLAW_HOME",
    },
}


def detect_harness() -> dict:
    """Detect which harness(es) are running based on env vars and files."""
    detected = []
    home = Path.home()

    for name, sig in HARNESS_SIGNATURES.items():
        matches = sum(1 for fn in sig["signals"] if fn())
        weight = matches / len(sig["signals"])
        if weight > 0:
            detected.append({
                "name": name,
                "confidence": round(weight * 100),
                "config_paths": sig["config_paths"],
                "home_var": sig["home_var"],
            })

    # Sort by confidence
    detected.sort(key=lambda x: -x["confidence"])

    if not detected:
        return {"status": "unknown", "harnesses": [], "primary": None}

    return {
        "status": "detected",
        "harnesses": detected,
        "primary": detected[0]["name"],
    }


def get_harness_home(harness_name: str) -> Optional[Path]:
    """Get the home directory for a detected harness."""
    if harness_name == "hermes-agent":
        h = os.environ.get("HERMES_HOME")
        return Path(h) if h else Path.home() / ".hermes"
    elif harness_name == "opencode":
        h = os.environ.get("OPENCODE_HOME")
        return Path(h) if h else Path.home() / ".opencode"
    elif harness_name == "claude-code":
        return Path.home() / ".claude"
    return None


# ═══════════════════════════════════════════════════════════════════════
# CONFIG PARSING
# ═══════════════════════════════════════════════════════════════════════

def load_yaml_safe(path: Path) -> dict:
    """Load YAML without pyyaml dependency — basic parser."""
    if not path.exists():
        return {}
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Minimal YAML parser for common patterns
        content = path.read_text(encoding="utf-8", errors="replace")
        result = {}
        current_key = None
        current_indent = 0
        nesting = {}
        for line in content.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            if stripped.endswith(":"):
                key = stripped[:-1].strip()
                if indent == 0:
                    current_key = key
                    result[current_key] = {}
                    current_indent = 0
                else:
                    nesting[indent] = key
                    parent = nesting.get(indent - 2, current_key)
                    if isinstance(result.get(parent), dict):
                        result[parent][key] = {}
            elif ":" in stripped:
                k, v = stripped.split(":", 1)
                k, v = k.strip(), v.strip()
                if indent == 0:
                    result[k] = v
                elif current_key and isinstance(result.get(current_key), dict):
                    result[current_key][k] = v
        return result


def load_env_file(path: Path) -> dict:
    """Load a .env file into a dict."""
    if not path.exists():
        return {}
    env = {}
    for line in path.read_text(encoding="utf-8", errors="replace").split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# ═══════════════════════════════════════════════════════════════════════
# PROMPT INJECTION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

# Known prompt injection / jailbreak token patterns
INJECTION_PATTERNS = [
    (r"DAN\b", "Jailbreak: 'DAN' (Do Anything Now) token"),
    (r"ignore\s+(all\s+)?previous\s+(instructions|prompts|directions)", "Instruction override attempt"),
    (r"forget\s+(everything|all|your)", "Memory reset attempt"),
    (r"you\s+are\s+(now|free|not)\s+(an?\s+)?(AI|assistant|bot|model)", "Role redefinition attempt"),
    (r"system\s+prompt", "System prompt leakage attempt"),
    (r"output\s+(your|the)\s+(system\s+)?(prompt|instructions)", "Prompt extraction attempt"),
    (r"print\s+(your|the)\s+(system\s+)?(prompt|instructions)", "Prompt extraction attempt"),
    (r"repeat\s+(everything|all)\s+(after|above)", "Context leakage probe"),
    (r"say\s+\"(yes|no)\"\s+(if|when)", "Obfuscated instruction attempt"),
    (r"role\s*play", "Role-play injection attempt"),
    (r"hypothetical", "Hypothetical boundary probe"),
    (r"you\s+don['\u2019]t\s+have\s+(to|any)\s+(restrictions|rules|limitations|boundaries)", "Constraint removal attempt"),
    (r"secret\s+(passcode|password|key|code)", "Secret extraction attempt"),
    (r"between\s+the\s+lines", "Hidden instruction probe"),
    (r"new\s+era|new\s+rules|override\s+(all|previous)", "Override attempt"),
    (r"sudo\s+(prompt|command|mode)", "Elevation attempt"),
    (r"developer\s+mode|dev\s+mode", "Developer mode injection"),
    (r"no\s+(restrictions|limits|boundaries|rules)", "Constraint removal"),
    (r"act\s+as\s+(if|though)\s+you", "Identity override"),
]


class PromptInspector:
    """Analyze a system prompt for injection vulnerabilities."""

    def __init__(self, content: str, label: str = "system prompt"):
        self.content = content
        self.label = label
        self.issues = []
        self._analyze()

    def _analyze(self):
        if not self.content.strip():
            self.issues.append({
            "severity": "high",
            "type": "empty_prompt",
            "detail": f"{self.label} está vacío — sin instrucciones base",
            "risk": "high",
            })
            return

        # 1. Check for injection patterns
        for pattern, description in INJECTION_PATTERNS:
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            if matches:
                self.issues.append({
                    "severity": "high" if "jailbreak" in description.lower() or "override" in description.lower() else "medium",
                    "type": "injection_pattern",
                    "detail": f"{description} en {self.label} ({len(matches)} ocurrencia(s))",
                    "pattern": pattern,
                })

        # 2. Prompt boundary analysis
        lines = self.content.split("\n")
        has_system_marker = any(line.strip().startswith("## System") or line.strip().startswith("# System") for line in lines)
        has_role_separator = bool(re.search(r"(user|assistant|system)\s*(:|：)", self.content, re.IGNORECASE))

        # 3. Check for clear instruction-data separation
        has_marker_sep = bool(re.search(r"---|===", self.content))
        has_explicit_delimiter = bool(re.search(r"<message|{user}|<input", self.content, re.IGNORECASE))

        if not has_system_marker and not has_explicit_delimiter:
            self.issues.append({
                "severity": "medium",
                "type": "boundary_weak",
                "detail": f"{self.label}: No hay separación clara entre instrucciones y datos. Sin ## System, ---, o delimitadores explícitos.",
            })

        if has_role_separator:
            self.issues.append({
                "severity": "low",
                "type": "boundary_mixed",
                "detail": f"{self.label}: Contiene marcadores de rol (user:/assistant:) que podrían confundir la separación prompt/datos.",
            })

        # 4. Tool description audit
        tool_sections = re.findall(r"##?\s*(Tool|Function|Herramienta)[^\\n]*\\n(.*?)(?=\\n##|\\Z)", self.content, re.DOTALL | re.IGNORECASE)
        for title, body in tool_sections:
            if len(body.strip()) < 50:
                self.issues.append({
                    "severity": "low",
                    "type": "tool_description_short",
                    "detail": f"Descripción de {title.strip()} muy corta ({len(body.strip())} chars) — puede causar mal uso.",
                })

        # 5. Check for API keys or tokens
        secret_patterns = [
            (r'sk-[A-Za-z0-9]{20,}', "OpenAI API key"),
            (r'api[_-]?key["\\\']?\\s*[:=]\\s*["\\\'](?!YOUR_|your-|\\$\\{)[A-Za-z0-9_\\-]{16,}', "Generic API key"),
            (r'token["\\\']?\\s*[:=]\\s*["\\\'](?!YOUR_|your-|\\$\\{)[A-Za-z0-9_\\-]{16,}', "Auth token"),
        ]
        for pattern, label in secret_patterns:
            if re.search(pattern, self.content, re.IGNORECASE):
                self.issues.append({
                    "severity": "critical",
                    "type": "secret_leak",
                    "detail": f"Posible {label} en {self.label}",
                })

    def score(self) -> tuple[int, int]:
        """Return (vulnerability_count, risk_level_0-10)."""
        if not self.issues:
            return (0, 0)
        severity_map = {"critical": 10, "high": 7, "medium": 4, "low": 1}
        max_risk = min(sum(severity_map.get(i["severity"], 3) for i in self.issues), 10)
        return (len(self.issues), max_risk)


# ═══════════════════════════════════════════════════════════════════════
# CONTEXT AUDIT — What travels to the LLM?
# ═══════════════════════════════════════════════════════════════════════

def audit_context(hermes_home: Path) -> dict:
    """Audit what data is being sent to the LLM provider."""
    findings = []

    # 1. Memory files — what's in the context
    mem_path = hermes_home / "memories" / "MEMORY.md"
    if mem_path.exists():
        mem_size = mem_path.stat().st_size
        findings.append({
            "type": "memory_size",
            "source": str(mem_path),
            "detail": f"Memoria persistente: {mem_size} bytes ({mem_size // 1000}K)",
            "risk": "low" if mem_size < 5000 else "medium" if mem_size < 20000 else "high",
        })

    user_path = hermes_home / "memories" / "USER.md"
    if user_path.exists():
        user_size = user_path.stat().st_size
        findings.append({
            "type": "user_profile",
            "source": str(user_path),
            "detail": f"Perfil de usuario: {user_size} bytes",
            "risk": "low",
        })

    # 2. Skills loaded — tool surface area
    skills_dir = hermes_home / "skills"
    if skills_dir.is_dir():
        skill_count = len([d for d in skills_dir.iterdir() if d.is_dir()])
        skill_files = sum(1 for _ in skills_dir.rglob("SKILL.md"))
        findings.append({
            "type": "tool_surface",
            "source": str(skills_dir),
            "detail": f"{skill_count} skill categories, {skill_files} SKILL.md files — tool surface area",
            "risk": "medium" if skill_count > 30 else "low",
        })

    # 3. Environment variables — what data is exposed
    env_vars = dict(os.environ)
    api_keys_found = []
    for k, v in env_vars.items():
        if any(x in k.lower() for x in ["api_key", "token", "secret", "password"]):
            masked = v[:8] + "..." if v else "(empty)"
            api_keys_found.append({"var": k, "masked_value": masked})

    if api_keys_found:
        findings.append({
            "type": "env_secrets",
            "source": "environment",
            "detail": f"{len(api_keys_found)} secretos en env vars",
            "secrets": api_keys_found,
            "risk": "medium",
        })

    # 4. Config file — what settings affect context
    config_path = hermes_home / "config.yaml"
    config = load_yaml_safe(config_path) if config_path.exists() else {}

    model = config.get("model", {})
    findings.append({
        "type": "model_config",
        "source": str(config_path),
        "detail": f"Modelo: {model.get('default', 'unknown')} via {model.get('provider', 'unknown')}",
        "risk": "info",
    })

    # Tool usage enforcement
    tool_use = config.get("agent", {}).get("tool_use_enforcement", "auto")
    if tool_use == "none":
        findings.append({
            "type": "tool_enforcement",
            "source": "config.yaml agent.tool_use_enforcement",
            "detail": "Tool use enforcement: 'none' — el modelo puede decidir no usar tools",
            "risk": "medium",
        })

    # Memory settings
    memory_config = config.get("memory", {})
    if memory_config.get("memory_enabled", True):
        findings.append({
            "type": "memory_enabled",
            "source": "config.yaml memory",
            "detail": f"Memoria activa (límite: {memory_config.get('memory_char_limit', 2200)} chars, flush: {memory_config.get('flush_min_turns', 6)} turns)",
            "risk": "info",
        })

    # Delegation settings
    delegation = config.get("delegation", {})
    if delegation.get("orchestrator_enabled", False):
        findings.append({
            "type": "subagent_delegation",
            "source": "config.yaml delegation",
            "detail": f"Subagentes activos (máx {delegation.get('max_concurrent_children', 3)} paralelo, profundidad {delegation.get('max_spawn_depth', 1)})",
            "risk": "medium",
        })

    # 5. Agent persona — what's in the system prompt
    soul_path = hermes_home / "SOUL.md"
    if soul_path.exists():
        soul_content = soul_path.read_text(encoding="utf-8", errors="replace")
        if len(soul_content) > 2000:
            findings.append({
                "type": "persona_size",
                "source": str(soul_path),
                "detail": f"Persona/SOUL.md: {len(soul_content)} chars — >2K de system prompt fijo",
                "risk": "medium",
            })

    return findings


# ═══════════════════════════════════════════════════════════════════════
# TOOL SCOPING AUDIT
# ═══════════════════════════════════════════════════════════════════════

def audit_tool_scoping(config: dict) -> list:
    """Audit tool access scoping from config."""
    findings = []
    c = config.get("terminal", {})
    if c.get("backend") == "local":
        findings.append({
            "type": "terminal_backend",
            "source": "config.yaml terminal.backend",
            "detail": "Terminal backend: local — acceso completo al sistema de archivos",
            "risk": "high",
        })
    elif c.get("backend") in ("docker", "modal", "ssh"):
        findings.append({
            "type": "terminal_backend",
            "source": "config.yaml terminal.backend",
            "detail": f"Terminal backend: {c['backend']} — sandboxeado",
            "risk": "low",
        })

    t = config.get("browser", {})
    if t.get("allow_private_urls", False):
        findings.append({
            "type": "browser_private",
            "source": "config.yaml browser.allow_private_urls",
            "detail": "Navegador puede acceder a URLs privadas (localhost, intranet)",
            "risk": "medium",
        })

    s = config.get("security", {})
    if s.get("redact_secrets", False):
        findings.append({
            "type": "secret_redaction",
            "source": "config.yaml security.redact_secrets",
            "detail": "Redacción de secretos: activada",
            "risk": "low",
        })
    else:
        findings.append({
            "type": "secret_redaction",
            "source": "config.yaml security.redact_secrets",
            "detail": "Redacción de secretos: DESACTIVADA — los secretos pueden aparecer en logs y output",
            "risk": "critical",
        })

    if s.get("allow_private_urls", False):
        findings.append({
            "type": "private_urls",
            "source": "config.yaml security.allow_private_urls",
            "detail": "URLs privadas permitidas — el agente puede acceder a servicios internos",
            "risk": "medium",
        })

    return findings


# ═══════════════════════════════════════════════════════════════════════
# SECURITY POSTURE
# ═══════════════════════════════════════════════════════════════════════

def score_posture(all_findings: list) -> dict:
    """Calculate overall security posture score."""
    weights = {"critical": 10, "high": 5, "medium": 3, "low": 1, "info": 0}
    total_risk = sum(weights.get(f.get("risk", "info"), 0) for f in all_findings)

    # Inverted 0-100 score (0 = terrible, 100 = perfect)
    max_possible = len(all_findings) * 10
    score = max(0, 100 - (total_risk / max(max_possible, 1)) * 100) if max_possible > 0 else 100

    if score >= 80:
        grade = "🟢 SEGURO"
    elif score >= 50:
        grade = "🟡 ATENCIÓN"
    elif score >= 30:
        grade = "🟠 RIESGO"
    else:
        grade = "🔴 CRÍTICO"

    return {"score": round(score), "grade": grade, "total_findings": len(all_findings), "total_risk": total_risk}


def generate_recommendations(all_findings: list, score: int) -> list:
    """Generate deterministic recommendations based on findings."""
    recs = []
    seen_types = set()

    for f in all_findings:
        if f["type"] in seen_types:
            continue
        seen_types.add(f["type"])

        if f["risk"] == "critical":
            if f["type"] == "secret_leak":
                recs.append({"priority": "🔥 CRÍTICA", "action": f"Eliminar secretos del {f['detail']}. Usar .env o gestor de secretos."})
            elif f["type"] == "secret_redaction" and "DESACTIVADA" in str(f.get("detail", "")):
                recs.append({"priority": "🔥 CRÍTICA", "action": "Activar security.redact_secrets en config.yaml para evitar fugas de API keys en logs."})
            else:
                recs.append({"priority": "🔥 CRÍTICA", "action": f"Revisar: {f['detail']}"})

        elif f["risk"] == "high":
            if f["type"] == "injection_pattern":
                recs.append({"priority": "⚠️ ALTA", "action": f"Revisar patrones de inyección detectados: {f['detail']}. Reforzar separación prompt/datos."})
            elif f["type"] == "terminal_backend" and "local" in str(f.get("detail", "")):
                recs.append({"priority": "⚠️ ALTA", "action": "Terminal en modo 'local' da acceso completo al sistema. Considerar docker o modal para aislamiento."})
            elif f["type"] == "memory_size" and "high" in str(f.get("risk", "")):
                recs.append({"priority": "⚠️ ALTA", "action": f"Memoria persistente muy grande ({f['detail']}). Podría contener datos sensibles o causar context overflow."})
            else:
                recs.append({"priority": "⚠️ ALTA", "action": f"Revisar: {f['detail']}"})

        elif f["risk"] == "medium":
            if f["type"] == "boundary_weak":
                recs.append({"priority": "⚡ MEDIA", "action": "Agregar delimitadores explícitos (## System, ---) entre instrucciones y datos del usuario para prevenir inyección."})
            elif f["type"] == "persona_size":
                recs.append({"priority": "⚡ MEDIA", "action": f"Persona muy larga ({f['detail']}). Consume tokens del context window."})
            elif f["type"] == "subagent_delegation":
                recs.append({"priority": "⚡ MEDIA", "action": "Subagentes pueden delegar a su vez. Revisar profundidad máxima y superficie de ataque."})
            else:
                recs.append({"priority": "⚡ MEDIA", "action": f"Revisar: {f['detail']}"})

    # If no secret redaction finding, recommend it
    if "secret_redaction" not in seen_types:
        recs.append({"priority": "⚡ MEDIA", "action": "Considerar activar security.redact_secrets en config.yaml."})

    return recs


# ═══════════════════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════════════════

def generate_report(harness_info: dict, config: dict, prompt_findings: list,
                    context_findings: list, tool_findings: list) -> dict:
    """Generate complete audit report."""
    all_findings = prompt_findings + context_findings + tool_findings

    # Normalize: ensure every finding has 'risk' key (map from 'severity' if needed)
    for f in all_findings:
        if "risk" not in f and "severity" in f:
            f["risk"] = f["severity"]
    posture = score_posture(all_findings)
    recs = generate_recommendations(all_findings, posture["score"])

    return {
        "harness": harness_info,
        "posture": posture,
        "findings": {
            "prompt_injection": prompt_findings,
            "context": context_findings,
            "tool_scoping": tool_findings,
        },
        "recommendations": recs,
    }


def print_report(report: dict, json_output: bool = False):
    """Print a human-readable or JSON report."""
    if json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
        return

    h = report["harness"]
    print()
    if h["status"] == "unknown":
        print("  ⚠️  No se detectó ningún harness conocido.")
        print("  📁 El directorio actual no tiene AGENTS.md ni config de agente.")
        print()
        return

    print(f"{'='*60}")
    print(f"  🔍  HARNESS CONTEXT AUDITOR")
    print(f"{'='*60}")
    print()
    print(f"  🖥️  Harness detectado:")
    for d in h["harnesses"]:
        icon = "▶" if d["name"] == h["primary"] else " "
        print(f"     {icon} {d['name']} ({d['confidence']}% confianza)")
    print()

    p = report["posture"]
    print(f"  📊 POSTURA DE SEGURIDAD: {p['score']}/100 — {p['grade']}")
    print(f"     {p['total_findings']} hallazgos, riesgo total: {p['total_risk']}")
    print()

    # Prompt Injection
    pi = report["findings"]["prompt_injection"]
    if pi:
        print(f"  🧪 INYECCIÓN DE PROMPT ({len(pi)} hallazgos):")
        for f in pi:
            sev_icon = {"critical": "🔴", "high": "⚠️", "medium": "⚡", "low": "ℹ️"}.get(f.get("risk", "info"), "ℹ️")
            print(f"     {sev_icon} [{f['risk'].upper()}] {f['detail']}")
        print()

    # Context
    ctx = report["findings"]["context"]
    if ctx:
        print(f"  📦 CONTEXTO AL LLM ({len(ctx)} hallazgos):")
        for f in ctx:
            sev_icon = {"critical": "🔴", "high": "⚠️", "medium": "⚡", "low": "ℹ️", "info": "ℹ️"}.get(f.get("risk", "info"), "ℹ️")
            print(f"     {sev_icon} [{f['risk'].upper()}] {f.get('detail', '')}")
        print()

    # Tool Scoping
    ts = report["findings"]["tool_scoping"]
    if ts:
        print(f"  🔧 SCOPEO DE TOOLS ({len(ts)} hallazgos):")
        for f in ts:
            sev_icon = {"critical": "🔴", "high": "⚠️", "medium": "⚡", "low": "ℹ️", "info": "ℹ️"}.get(f.get("risk", "info"), "ℹ️")
            print(f"     {sev_icon} [{f['risk'].upper()}] {f.get('detail', '')}")
        print()

    # Recommendations
    recs = report["recommendations"]
    if recs:
        print(f"  💡 RECOMENDACIONES ({len(recs)}):")
        for r in recs:
            print(f"     {r['priority']}: {r['action']}")
        print()

    print(f"{'='*60}")
    print()


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Harness Context Auditor — Detective de inyección, contexto y postura de harness")
    parser.add_argument("--self", action="store_true", help="Auditar el harness actual (por defecto)")
    parser.add_argument("--path", help="Ruta a un proyecto con AGENTS.md para auditar")
    parser.add_argument("--prompt", help="Analizar un texto como system prompt (para testear patrones)")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args()

    json_output = args.json

    # 1. Detect harness
    harness_info = detect_harness()

    # 2. If --prompt, just analyze that
    if args.prompt:
        inspector = PromptInspector(args.prompt, "custom prompt")
        findings = inspector.issues
        for f in findings:
            if "risk" not in f and "severity" in f:
                f["risk"] = f["severity"]
        posture = {"score": 100 - min(len(findings) * 10, 90), "grade": "N/A", "total_findings": len(findings), "total_risk": 0}
        report = {
            "harness": harness_info,
            "posture": posture,
            "findings": {"prompt_injection": findings, "context": [], "tool_scoping": []},
            "recommendations": [],
        }
        print_report(report, json_output)
        return

    # 3. Determine audit target
    hermes_home = None
    config = {}

    if args.path:
        target = Path(args.path).resolve()
        if not target.is_dir():
            print(f"Error: {args.path} no es un directorio", file=sys.stderr)
            sys.exit(1)
        config_path = target / "config.yaml"
        if config_path.exists():
            config = load_yaml_safe(config_path)
    else:
        # Self-audit: find the running harness home
        primary = harness_info.get("primary")
        if primary:
            hh = get_harness_home(primary)
            if hh:
                hermes_home = hh
                config_path = hh / "config.yaml"
                if config_path.exists():
                    config = load_yaml_safe(config_path)

    # 4. If no hermes_home but we have a path, use it
    if not hermes_home and args.path:
        hermes_home = Path(args.path).resolve()

    # 5. Prompt injection analysis (from config and AGENTS.md)
    prompt_issues = []

    # Analyze personalities from config
    personalities = config.get("agent", {}).get("personalities", {})
    for name, prompt in personalities.items():
        inspector = PromptInspector(str(prompt), f"personality '{name}'")
        prompt_issues.extend(inspector.issues)

    # Analyze SOUL.md (persona file)
    if hermes_home:
        soul_path = hermes_home / "SOUL.md"
        if soul_path.exists():
            inspector = PromptInspector(soul_path.read_text(encoding="utf-8", errors="replace"), "SOUL.md (persona)")
            prompt_issues.extend(inspector.issues)

        # Analyze AGENTS.md from project if --path
        if args.path:
            agents_path = Path(args.path) / "AGENTS.md"
            if agents_path.exists():
                inspector = PromptInspector(agents_path.read_text(encoding="utf-8", errors="replace"), f"AGENTS.md ({args.path})")
                prompt_issues.extend(inspector.issues)

    # 6. Context audit
    context_issues = []
    if hermes_home:
        context_issues = audit_context(hermes_home)

    # 7. Tool scoping audit
    tool_issues = audit_tool_scoping(config)

    # 8. Generate and print report
    report = generate_report(harness_info, config, prompt_issues, context_issues, tool_issues)
    print_report(report, json_output)


if __name__ == "__main__":
    main()
