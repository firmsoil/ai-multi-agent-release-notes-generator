#!/bin/bash
# Make executable: chmod +x generate_release_notes.sh

REPO="firmsoil/slsa"
FROM_TAG="v1.0-rc2"
TO_TAG="v1.0.0"

generate-release-notes --repo "$REPO" --from-tag "$FROM_TAG" --to-tag "$TO_TAG"
echo "Release notes generated in release_notes.txt"
