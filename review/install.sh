#!/bin/bash
# SEO Review Board - Universal Installer
# Works with: Hermes, Claude Code, Codex, or any AI agent
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/lennney/seo-review-board/master/install.sh | bash
#   or
#   bash install.sh [target_dir]

set -e

REPO_URL="https://github.com/lennney/seo-review-board"
RAW_URL="https://raw.githubusercontent.com/lennney/seo-review-board/master"
TARGET_DIR="${1:-$HOME/.hermes/skills/seo/ai-team-review}"

echo "=== SEO Review Board Installer ==="
echo ""

# Create target directory
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

echo "Downloading SKILL.md..."
curl -sSL "$RAW_URL/SKILL.md" -o SKILL.md

echo "Downloading adapters..."
mkdir -p adapters
curl -sSL "$RAW_URL/adapters/hermes.md" -o adapters/hermes.md
curl -sSL "$RAW_URL/adapters/claude-code.md" -o adapters/claude-code.md
curl -sSL "$RAW_URL/adapters/codex.md" -o adapters/codex.md

echo "Downloading scenarios..."
mkdir -p scenarios
curl -sSL "$RAW_URL/scenarios/product-review.md" -o scenarios/product-review.md
curl -sSL "$RAW_URL/scenarios/seo-content-review.md" -o scenarios/seo-content-review.md
curl -sSL "$RAW_URL/scenarios/tech-review.md" -o scenarios/tech-review.md

echo "Downloading roles..."
mkdir -p roles
curl -sSL "$RAW_URL/roles/library.md" -o roles/library.md

echo "Downloading references..."
mkdir -p references
curl -sSL "$RAW_URL/references/scoring-system.md" -o references/scoring-system.md
curl -sSL "$RAW_URL/references/data-verification-methods.md" -o references/data-verification-methods.md
curl -sSL "$RAW_URL/references/iterative-review-pattern.md" -o references/iterative-review-pattern.md
curl -sSL "$RAW_URL/references/document-review-iteration.md" -o references/document-review-iteration.md
curl -sSL "$RAW_URL/references/document-consistency-checklist.md" -o references/document-consistency-checklist.md
curl -sSL "$RAW_URL/references/prd-template.md" -o references/prd-template.md
curl -sSL "$RAW_URL/references/product-doc-checklist.md" -o references/product-doc-checklist.md
curl -sSL "$RAW_URL/references/html-prototyping-pattern.md" -o references/html-prototyping-pattern.md
curl -sSL "$RAW_URL/references/ui-review-checklist.md" -o references/ui-review-checklist.md

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Installed to: $TARGET_DIR"
echo "Files: $(find . -type f | wc -l)"
echo ""
echo "Usage:"
echo "  - Hermes: skill already loaded if installed to ~/.hermes/skills/"
echo "  - Claude Code: Copy SKILL.md content to your conversation"
echo "  - Codex: Reference the scenarios/ and roles/ files"
echo "  - Any AI: Read SKILL.md and follow the framework"
echo ""
echo "Documentation: $REPO_URL"
