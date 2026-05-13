"""Project type detector based on existing files.

This module analyzes the file structure of a root directory
to determine the project type and suggest recommended templates.
"""

from __future__ import annotations

from enum import Enum, auto
from pathlib import Path


class ProjectType(Enum):
    """Project types supported by the detector."""

    STATIC_SITE = auto()
    RUST_PROJECT = auto()
    PYTHON_PROJECT = auto()
    NODE_PROJECT = auto()
    TRADING_BOT = auto()
    UNKNOWN = auto()


class ProjectDetector:
    """Detects the project type by inspecting files and directories."""

    # ------------------------------------------------------------------ #
    # Evidence constants
    # ------------------------------------------------------------------ #
    _TRADING_SUBDIRS = {"strategy", "exchange", "trader"}

    # ------------------------------------------------------------------ #
    # Detection
    # ------------------------------------------------------------------ #
    def detect(self, root_path: str) -> tuple[ProjectType, dict[str, list[str]]]:
        """Detects the project type from the root path.

        Args:
            root_path: Path to the project's root directory.

        Returns:
            Tuple with the detected project type and a dictionary
            of evidence listing the found files and directories.
        """
        root = Path(root_path).resolve()
        evidence: dict[str, list[str]] = {
            "files": [],
            "directories": [],
        }

        if not root.exists() or not root.is_dir():
            return ProjectType.UNKNOWN, evidence

        # Collect top-level files and directories
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
            # NODE is checked before RUST to give it priority if it matches
            return ProjectType.NODE_PROJECT, evidence

        # --- PYTHON_PROJECT ---
        if any(f in top_level_files for f in ("setup.py", "pyproject.toml", "requirements.txt")):
            return ProjectType.PYTHON_PROJECT, evidence

        # --- RUST_PROJECT (top-level or subdirectory) ---
        has_cargo_toml = "Cargo.toml" in top_level_files
        if not has_cargo_toml:
            # Search in top-level subdirectories
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

        # Default
        return ProjectType.UNKNOWN, evidence

    # ------------------------------------------------------------------ #
    # Recommendations
    # ------------------------------------------------------------------ #
    def get_recommended_templates(self, project_type: ProjectType) -> list[str]:
        """Returns the list of recommended templates based on the project type.

        Args:
            project_type: Detected project type.

        Returns:
            List of suggested file/template names.
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
    # Utilities
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_project_type_name(project_type: ProjectType) -> str:
        """Returns a readable name for the project type.

        Args:
            project_type: Project type.

        Returns:
            Descriptive string of the type.
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
