"""Detector de tipos de proyecto basado en archivos existentes.

Este módulo analiza la estructura de archivos de un directorio raíz
para determinar el tipo de proyecto y sugerir plantillas recomendadas.
"""

from __future__ import annotations

from enum import Enum, auto
from pathlib import Path


class ProjectType(Enum):
    """Tipos de proyecto soportados por el detector."""

    STATIC_SITE = auto()
    RUST_PROJECT = auto()
    PYTHON_PROJECT = auto()
    NODE_PROJECT = auto()
    TRADING_BOT = auto()
    UNKNOWN = auto()


class ProjectDetector:
    """Detecta el tipo de proyecto inspeccionando archivos y directorios."""

    # ------------------------------------------------------------------ #
    # Constantes de evidencia
    # ------------------------------------------------------------------ #
    _TRADING_SUBDIRS = {"strategy", "exchange", "trader"}

    # ------------------------------------------------------------------ #
    # Detección
    # ------------------------------------------------------------------ #
    def detect(self, root_path: str) -> tuple[ProjectType, dict[str, list[str]]]:
        """Detecta el tipo de proyecto a partir de la ruta raíz.

        Args:
            root_path: Ruta del directorio raíz del proyecto.

        Returns:
            Tupla con el tipo de proyecto detectado y un diccionario
            de evidencias que lista los archivos y directorios encontrados.
        """
        root = Path(root_path).resolve()
        evidence: dict[str, list[str]] = {
            "files": [],
            "directories": [],
        }

        if not root.exists() or not root.is_dir():
            return ProjectType.UNKNOWN, evidence

        # Recolectar archivos y directorios top-level
        top_level_files = {f.name for f in root.iterdir() if f.is_file()}
        top_level_dirs = {d.name for d in root.iterdir() if d.is_dir()}

        evidence["files"] = sorted(top_level_files)
        evidence["directories"] = sorted(top_level_dirs)

        # --- STATIC_SITE ---
        has_index_html = "index.html" in top_level_files
        has_css_or_js = any(
            (root / f).suffix in {".css", ".js"}
            for f in top_level_files
        )
        if has_index_html and has_css_or_js:
            return ProjectType.STATIC_SITE, evidence

        # --- NODE_PROJECT ---
        if "package.json" in top_level_files:
            # NODE se chequea antes que RUST para darle prioridad si coincide
            return ProjectType.NODE_PROJECT, evidence

        # --- PYTHON_PROJECT ---
        if any(f in top_level_files for f in ("setup.py", "pyproject.toml", "requirements.txt")):
            return ProjectType.PYTHON_PROJECT, evidence

        # --- RUST_PROJECT (top-level o subdirectorio) ---
        has_cargo_toml = "Cargo.toml" in top_level_files
        if not has_cargo_toml:
            # Buscar en subdirectorios top-level
            for d in top_level_dirs:
                cargo = root / d / "Cargo.toml"
                if cargo.is_file():
                    has_cargo_toml = True
                    evidence.setdefault("cargo_locations", []).append(str(cargo.relative_to(root)))
                    break

        if has_cargo_toml:
            # --- TRADING_BOT ---
            matched_trading_dirs = top_level_dirs & self._TRADING_SUBDIRS
            if len(matched_trading_dirs) >= 2:
                evidence["trading_directories"] = sorted(matched_trading_dirs)
                return ProjectType.TRADING_BOT, evidence
            return ProjectType.RUST_PROJECT, evidence

        # Por defecto
        return ProjectType.UNKNOWN, evidence

    # ------------------------------------------------------------------ #
    # Recomendaciones
    # ------------------------------------------------------------------ #
    def get_recommended_templates(self, project_type: ProjectType) -> list[str]:
        """Retorna la lista de plantillas recomendadas según el tipo de proyecto.

        Args:
            project_type: Tipo de proyecto detectado.

        Returns:
            Lista de nombres de archivos/plantillas sugeridos.
        """
        base = [
            "AGENTS.md",
            "ROADMAP.md",
            ".gitignore",
            "LICENSE",
            "CONTRIBUTING.md",
        ]

        if project_type == ProjectType.STATIC_SITE:
            return base.copy()

        if project_type == ProjectType.RUST_PROJECT:
            return base + ["Dockerfile", "Makefile", "rust-toolchain.toml"]

        if project_type == ProjectType.PYTHON_PROJECT:
            return base + [
                "pyproject.toml",
                "pytest.ini",
                "tox.ini",
                ".pre-commit-config.yaml",
            ]

        if project_type == ProjectType.NODE_PROJECT:
            return base + [
                ".npmrc",
                ".nvmrc",
                ".eslintrc",
                ".prettierrc",
            ]

        if project_type == ProjectType.TRADING_BOT:
            return base + [
                "Dockerfile",
                "Makefile",
                "rust-toolchain.toml",
                ".env.example",
                "restart.sh",
                "health-check.sh",
            ]

        # UNKNOWN
        return base.copy()

    # ------------------------------------------------------------------ #
    # Utilidades
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_project_type_name(project_type: ProjectType) -> str:
        """Retorna un nombre legible para el tipo de proyecto.

        Args:
            project_type: Tipo de proyecto.

        Returns:
            Cadena descriptiva del tipo.
        """
        mapping = {
            ProjectType.STATIC_SITE: "Sitio estático",
            ProjectType.RUST_PROJECT: "Proyecto Rust",
            ProjectType.PYTHON_PROJECT: "Proyecto Python",
            ProjectType.NODE_PROJECT: "Proyecto Node.js",
            ProjectType.TRADING_BOT: "Bot de trading",
            ProjectType.UNKNOWN: "Desconocido",
        }
        return mapping.get(project_type, "Desconocido")
