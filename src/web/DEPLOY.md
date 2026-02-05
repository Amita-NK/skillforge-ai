# 🚀 How to Deploy SkillForge AI to the Web

To get a real `www.your-app.com` link accessible from your phone and laptop anywhere, follow these steps. We will use **Vercel**, the creators of Next.js, as it is free and the easiest way to host this app.

## Option A: The "No Code" Way (Easiest)

1.  **Create a GitHub Repository**
    *   Go to [GitHub.com](https://github.com/new) and create a new repository called `skillforge-ai`.
    *   Do *not* add a README or .gitignore (we already have them).

2.  **Push your code**
    *   Open your terminal in the `web` folder.
    *   Run these commands (replace `YOUR-USERNAME` with your GitHub username):
        ```bash
        git remote add origin https://github.com/YOUR-USERNAME/skillforge-ai.git
        git branch -M main
        git push -u origin main
        ```

3.  **Deploy on Vercel**
    *   Go to [Vercel.com](https://vercel.com/new) and sign up/login with GitHub.
    *   You will see your `skillforge-ai` project. Click **Import**.
    *   Click **Deploy**.
    *   🎉 Wait 1 minute. You will get a link like `https://skillforge-ai.vercel.app`.

## Option B: The "Hacker" Way (Using CLI)

If you have the Vercel CLI installed, you can just run:

```bash
npx vercel
```

1.  Select **Yes** to set up and deploy.
2.  Link to your existing project? **No**.
3.  Name? **skillforge-ai**.
4.  Directory? **./** (default).
5.  Settings? **No** (defaults are fine).

## Option C: Netlify (Alternative)

1.  Drag and drop the `web` folder into [Netlify Drop](https://app.netlify.com/drop) (Works for static sites, but since we use Next.js server features, **Option A is much better**).

---
**Note on Environment Variables:**
Currently, we are mocking the AI responses, so you don't need API keys. If you add real OpenAI integration later, you will need to add `OPENAI_API_KEY` in the Vercel Project Settings.
