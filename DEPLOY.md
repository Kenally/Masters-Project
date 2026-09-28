# Deploying to Render (get a public link anyone can click)

This gives you a URL like `https://ai-ethics-readiness-tool.onrender.com` that
works for anyone, no install required on their end. Render's free tier is
used here, it's good for a thesis demo but note the free tier sleeps after
15 minutes of inactivity (takes ~30 seconds to wake up on the next visit),
and its filesystem resets on redeploy, so treat this as a demo, not
permanent production storage. For anything long-term, upgrade the plan or
add a proper hosted database.

## One-time setup

### 1. Push this folder to GitHub

If you don't already have a GitHub account, create one at github.com (free).

From inside the `django_app` folder:

```
git init
git add .
git commit -m "Initial commit"
```

Then create a new empty repository on GitHub (github.com/new), and push:

```
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render

1. Go to https://render.com and sign up (you can sign in with your GitHub account).
2. Click **New +** -> **Blueprint**.
3. Connect the GitHub repository you just pushed.
4. Render will detect `render.yaml` in this folder automatically and set
   everything up: the build command, the start command, and a generated
   `SECRET_KEY`.
5. Click **Apply**. The first build takes a few minutes (installing
   dependencies, running migrations, loading the association rules).
6. Once it says "Live", your URL is shown at the top of the service page,
   something like `https://ai-ethics-readiness-tool.onrender.com`.

That's it, share that link with anyone. They just click it and use the app
in their browser, nothing to install.

## Updating after retraining the model

If you collect more survey responses and retrain (see the analysis
folder's README), you need to:

1. Copy the new `model.pkl` and `rules.json` from
   `analysis/../django_app/assessment/ml/` into this `django_app/assessment/ml/`
   folder (if they're not already the same folder in your setup).
2. Commit and push:
   ```
   git add .
   git commit -m "Retrained model with more responses"
   git push
   ```
3. Render automatically rebuilds and redeploys on every push to `main`.

## Troubleshooting

- **Build fails on Render**: check the build logs in the Render dashboard,
  the most common cause is a typo in `requirements.txt` or a Python version
  mismatch (this project targets Python 3.11).
- **Site loads but assessment says "no trained model found"**: make sure
  `assessment/ml/model.pkl` was committed to git, run `git status` locally
  to check it isn't being ignored.
- **Changes not showing up**: Render only redeploys on a new push to the
  connected branch, confirm your commit actually pushed with `git log` and
  check the Render dashboard shows a new deploy in progress.
