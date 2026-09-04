#!/usr/bin/env bash
# Rebuild the page from the dataset and deploy it to Cloudflare Pages.
#
# This is a direct-upload Pages project, not git-connected: pushing to GitHub
# does not redeploy the site. Run this.
set -euo pipefail
cd "$(dirname "$0")"

python3 build_page.py

: "${CLOUDFLARE_API_TOKEN:?set it, e.g. export CLOUDFLARE_API_TOKEN=\"\$(cat ../../Who_Owns_Hackney/.credentials/cloudflare_api_token.txt)\"}"
export CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-801632497c85ee6a80eda6c95b6cc0eb}"

# Pages, not Workers: the account token carries Pages:Edit but not Workers
# Scripts:Edit, so `wrangler deploy` fails with authentication error 10000.
npx --yes wrangler@latest pages deploy public \
  --project-name holborn-st-pancras-map --branch main --commit-dirty=true

echo "Live: https://holborn-st-pancras-map.pages.dev"
