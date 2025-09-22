#!/bin/bash
# Make executable: chmod +x generate_release_notes.sh

REPO="${REPO:-firmsoil/slsa}"
FROM_TAG="${FROM_TAG:-v0.1.0}"
TO_TAG="${TO_TAG:-v1.0.0}"
LLM_PROVIDER="${LLM_PROVIDER:-openai}"

generate-release-notes --repo "$REPO" --from-tag "$FROM_TAG" --to-tag "$TO_TAG" --llm-provider "$LLM_PROVIDER"
echo "Release notes generated in release_notes.txt"
