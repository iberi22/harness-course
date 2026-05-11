#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# Harness Course CLI — Installer
# ═══════════════════════════════════════════════════════════════════
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/iberi22/harness-course/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/iberi22/harness-course/main/install.sh | bash -s -- --user
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

REPO="iberi22/harness-course"
BRANCH="main"
INSTALL_DIR="${HARNESS_HOME:-$HOME/.harness-course}"
PYTHON="${PYTHON:-python3}"
VENV_DIR="$INSTALL_DIR/venv"

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BOLD}🔧 Harness Course CLI — Installer${NC}"
echo ""

# ── Detect target ──────────────────────────────────────────────
TARGET="${1:-system}"
if [ "$TARGET" = "--user" ] || [ "$TARGET" = "user" ]; then
    TARGET="user"
    echo -e "${YELLOW}📦 User install (~/.local/bin)${NC}"
else
    echo -e "${YELLOW}📦 System install (requires sudo)${NC}"
fi

# ── Check Python ────────────────────────────────────────────────
if ! command -v "$PYTHON" &>/dev/null; then
    echo "❌ Python no encontrado. Instala Python 3.10+ primero."
    echo "   apt install python3 python3-pip python3-venv   (Debian/Ubuntu)"
    echo "   brew install python                             (macOS)"
    exit 1
fi

PY_VER=$("$PYTHON" --version 2>&1 | grep -oP '\d+\.\d+')
echo -e "  Python: $PYTHON $PY_VER ✓"

# ── Create venv ────────────────────────────────────────────────
mkdir -p "$INSTALL_DIR"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "  Creando virtualenv en $VENV_DIR..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# ── Install from GitHub ────────────────────────────────────────
echo -e "  Instalando harness-course desde GitHub..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet "git+https://github.com/$REPO.git@$BRANCH"

echo -e "  ${GREEN}✅ Instalado${NC}"

# ── Create symlink ─────────────────────────────────────────────
HARNESS_BIN="$VENV_DIR/bin/harness"

if [ "$TARGET" = "user" ]; then
    mkdir -p "$HOME/.local/bin"
    TARGET_DIR="$HOME/.local/bin"
else
    TARGET_DIR="/usr/local/bin"
fi

if [ -f "$HARNESS_BIN" ]; then
    if [ "$TARGET" = "system" ]; then
        sudo ln -sf "$HARNESS_BIN" "$TARGET_DIR/harness"
    else
        ln -sf "$HARNESS_BIN" "$TARGET_DIR/harness"
    fi
    echo -e "  Symlink: $TARGET_DIR/harness → $HARNESS_BIN"
fi

# ── Verify ─────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}✅ Instalación completa${NC}"
echo ""
if command -v harness &>/dev/null; then
    harness --version
    echo ""
    echo -e "  ${BOLD}Usa:${NC} harness scan ~/projects/mi-proyecto"
    echo -e "  ${BOLD}Docs:${NC} harness --help"
    echo -e "  ${BOLD}Sitio:${NC} https://iberi22.github.io/harness-course/"
else
    echo -e "  ${YELLOW}⚠️  'harness' no está en PATH. Agrega:${NC}"
    echo "     export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "     Luego: harness scan . --help"
fi
echo ""
echo -e "  Para desinstalar: rm -rf $INSTALL_DIR ${TARGET_DIR}/harness"
