# SkillForge AI+

Adaptive Intelligence for Secure Learning

SkillForge AI+ is an AI-powered adaptive learning and developer productivity platform that personalizes education, improves coding efficiency, and ensures secure code execution through cloud-native architecture.

---

## Live Application

Production Deployment  
https://skillforge-ai.vercel.app

If the link is not accessible, run the project locally using the setup instructions below.

---

## Tech Stack

- Next.js
- TypeScript
- React
- AWS Cloud Services
- Secure Sandbox Execution
- Serverless Architecture

Built using the framework provided by :contentReference[oaicite:0]{index=0} and deployed on :contentReference[oaicite:1]{index=1}.

---

## Features

- Adaptive learning paths
- AI-powered explanations
- Smart code debugging assistance
- Productivity and fatigue tracking
- Secure sandbox execution
- Offline and multilingual support
- Scalable cloud-native backend

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/skillforge-ai.git
cd skillforge-ai
```

### 2. Install dependencies

```bash
npm install
```

or

```bash
yarn install
```

or

```bash
pnpm install
```

---

## Run Development Server

```bash
npm run dev
```

Open in browser:

```
http://localhost:3000
```

The page automatically reloads as you edit files.

Main entry point:

```
app/page.tsx
```

---

## Available Scripts

```bash
npm run dev        # start development server
npm run build      # production build
npm run start      # start production server
npm run lint       # lint code
```

---

## Project Structure

```
app/              application routes and pages
components/       reusable UI components
lib/              utilities and helpers
public/           static assets
assets/           logos and images
styles/           global styles
```

---

## Deployment

This project is optimized for deployment on Vercel.

### Deploy with Vercel

```bash
npm run build
```

Then connect the repository to Vercel dashboard for automatic CI/CD.

Steps:

1. Push code to GitHub
2. Import repository into Vercel
3. Select Next.js framework preset
4. Deploy

Each push triggers automatic builds.

---

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=your_api_url
AWS_REGION=your_region
```

---

## Documentation

- requirements.md
- design.md
- architecture/
- docs/
- ppt/

---

## Team

INNO-V-A-TORS

---

## License

MIT License
