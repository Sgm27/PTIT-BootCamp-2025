# Landing Page — VCareMind (Static HTML + Tailwind CDN)

This is a simple static landing page that uses **Tailwind CSS via CDN**. No build tools are required.

## 1) Run locally
Just open `index.html` in your browser (double-click the file).

## 2) Initialize Git (first time)
Open Terminal/PowerShell in the project folder and run:
```bash
git init
git add .
git commit -m "init: landing page"
```

## 3) Create a GitHub repo
- Go to GitHub → New repository → name it, e.g. `landing-page` → **Create repository**.

## 4) Connect and push
Replace `<username>` and `<repo>` then run:
```bash
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

## 5) Next updates
After you edit files, push again:
```bash
git add -A
git commit -m "feat: update hero and features"
git push
```

## Optional: Deploy to Vercel (Static Site)
- Go to Vercel → **New Project** → Import your GitHub repo.
- Framework Preset: **Other** (or let Vercel auto-detect Static).
- Build Command: _None_ (leave empty).
- Output Directory: `/` (root).
- Deploy → you’ll get `https://<project>.vercel.app`.