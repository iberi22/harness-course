#!/bin/bash
# init.sh — Bootstrap del proyecto Harness Course
# Proyecto estático: no necesita build, solo verificar tools
set -e

echo "🔧 Inicializando Harness Course..."
echo "📁 Sitio estático GitHub Pages — sin dependencias de build"

# Verificar Python (necesario para harness evaluator)
if command -v python3 &>/dev/null; then
    echo "✅ Python $(python3 --version 2>&1) — evaluador listo"
else
    echo "⚠️  python3 no encontrado — el evaluador no funcionará"
fi

# Verificar gh CLI (opcional, para GitHub Pages)
if command -v gh &>/dev/null; then
    echo "✅ gh CLI $(gh --version 2>&1 | head -1)"
else
    echo "ℹ️  gh CLI no instalado — puedes pushear manualmente"
fi

echo ""
echo "📋 Comandos útiles:"
echo "  python3 scripts/harness_evaluator.py scan .    # Escanear harness"
echo "  python3 scripts/harness_evaluator.py fix .      # Generar archivos faltantes"
echo "  python3 scripts/harness_evaluator.py scan . --json  # JSON compacto para agentes"
echo ""
echo "✅ Proyecto listo — edita los archivos en pages/ y css/"
