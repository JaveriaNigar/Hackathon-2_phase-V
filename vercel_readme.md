# Deploying to Vercel

## Quick Setup

1. Create a new project on [Vercel](https://vercel.com)
2. Import your `Nextjs-Todo-Frontend` repository
3. Vercel will automatically detect this is a Next.js project

## Environment Variables

Set the following environment variables in your Vercel project settings:

- `NEXT_PUBLIC_API_BASE_URL`: Set this to your deployed backend URL (e.g., `https://your-replit-app.repl.co/api`)

## Build Configuration

The project is configured to work with Vercel's standard Next.js deployment. No special configuration is needed beyond setting the environment variables.

## Deployment Process

1. Link your GitHub repository to Vercel
2. Vercel will automatically deploy on every push to the main branch
3. Preview deployments will be created for pull requests
4. The production domain will be assigned automatically, or you can configure a custom domain

## Custom Domain (Optional)

If you want to use a custom domain:

1. Go to your project settings in Vercel
2. Navigate to the "Domains" section
3. Add your custom domain
4. Update your DNS settings as instructed by Vercel

## Monitoring

Vercel provides built-in analytics and error monitoring. You can access these from your project dashboard.