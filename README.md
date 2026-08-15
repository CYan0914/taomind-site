# TaoMind — Daily Tao Te Ching & Diamond Sutra, Verse by Verse

Bilingual SEO content site for the [TaoMind](https://apps.apple.com/app/id6800654302) iOS app.
All 113 chapters (81 Tao Te Ching + 32 Diamond Sutra) with original verse, plain-language
commentary (白话精讲) and a reflection question — every page in English and Chinese.

**Live site**: https://cyan0914.github.io/taomind-site/

## Structure

- `generate_site.py` — static-site generator. Reads `library_content.py` (in the
  taomind-Streamlit project) and emits the bilingual pages, sitemap and robots.txt.
- `site/` — generated output; this folder is published to GitHub Pages via the
  Actions workflow in `.github/workflows/pages.yml`.

## Regenerating

```bash
python generate_site.py
git add -A
git commit -m "Update site content"
git push
```

The Pages workflow rebuilds automatically on push.
