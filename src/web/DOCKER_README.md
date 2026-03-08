# Frontend Docker Build Guide

This directory contains the Dockerfile for building and serving the Next.js frontend application with Nginx.

## Architecture

The Dockerfile uses a multi-stage build approach:

1. **Stage 1 (Builder)**: Uses Node.js 20 Alpine to build the Next.js application
2. **Stage 2 (Production)**: Uses Nginx Alpine to serve the static files

## Prerequisites

- Docker installed on your system
- Node.js dependencies defined in `package.json`

## Building the Image

From the `src/web` directory:

```bash
docker build -t skillforge-frontend:latest .
```

## Running the Container

### Standalone Mode

```bash
docker run -p 80:80 skillforge-frontend:latest
```

The application will be available at `http://localhost`

### With Docker Compose

The frontend is integrated into the main `docker-compose.yml` at the project root:

```bash
# From project root
docker-compose up frontend
```

## Configuration

### Nginx Configuration

The `nginx.conf` file includes:

- Static file serving with caching
- Client-side routing support (SPA)
- API proxy to backend service
- Security headers
- Gzip compression

### Next.js Configuration

The `next.config.ts` is configured for static export:

```typescript
{
  output: 'export',
  distDir: 'out',
  images: {
    unoptimized: true,
  },
}
```

## Environment Variables

For production deployments, you may need to configure:

- `NEXT_PUBLIC_API_URL`: Backend API endpoint
- `NEXT_PUBLIC_ENV`: Environment name (development, staging, production)

These should be set at build time as Next.js bakes them into the static build.

## Build Optimization

The Dockerfile includes several optimizations:

1. **Multi-stage build**: Reduces final image size by excluding build dependencies
2. **Layer caching**: Dependencies are installed before copying source code
3. **Alpine base images**: Minimal image size
4. **Static asset caching**: Nginx configured with long cache times for static assets
5. **.dockerignore**: Excludes unnecessary files from build context

## Troubleshooting

### Build fails with "npm ci" error

Ensure `package-lock.json` exists and is committed to the repository.

### Application not loading

1. Check if the build completed successfully
2. Verify nginx is running: `docker logs <container-id>`
3. Check if port 80 is available on your host

### API calls failing

Update the API proxy configuration in `nginx.conf` to point to your backend service.

## Production Deployment

For AWS deployment:

1. Build and tag the image
2. Push to Amazon ECR
3. Deploy to ECS Fargate or serve via S3 + CloudFront

See the main `DEPLOYMENT_GUIDE.md` for detailed AWS deployment instructions.
