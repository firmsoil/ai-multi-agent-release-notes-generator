#!/bin/bash
# Generate Release Notes Script
# Make executable: chmod +x generate_release_notes.sh

# Default values
REPO="${REPO:-firmsoil/slsa}"
FROM_TAG="${FROM_TAG:-v0.1.0}"
TO_TAG="${TO_TAG:-v1.0.0}"
LLM_PROVIDER="${LLM_PROVIDER:-openai}"
FORMAT="${FORMAT:-markdown}"
OUTPUT="${OUTPUT:-release_notes.txt}"

echo "🚀 Generating Release Notes..."
echo "   Repository: $REPO"
echo "   From: $FROM_TAG"
echo "   To: $TO_TAG"
echo "   LLM Provider: $LLM_PROVIDER"
echo "   Format: $FORMAT"
echo "   Output: $OUTPUT"
echo ""

generate-release-notes \
  --repo "$REPO" \
  --from-tag "$FROM_TAG" \
  --to-tag "$TO_TAG" \
  --llm-provider "$LLM_PROVIDER" \
  --format "$FORMAT" \
  --output "$OUTPUT"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Release notes generated successfully in $OUTPUT"
    
    if [ "$FORMAT" = "confluence" ]; then
        echo ""
        echo "📋 To use in Confluence:"
        echo "   1. Open Confluence page editor"
        echo "   2. Click '</>' (Insert markup)"
        echo "   3. Paste the contents of $OUTPUT"
        echo "   4. Click 'Insert'"
    fi
else
    echo ""
    echo "❌ Failed to generate release notes"
    exit 1
fi
