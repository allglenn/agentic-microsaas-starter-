# Web Application (Next.js)

This is the frontend application built with Next.js 14, TypeScript, and Tailwind CSS.

## 🚀 Features

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **NextAuth.js** for authentication
- **Prisma** for database operations
- **Responsive Design** with modern UI components

## 🛠️ Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

1. **Install dependencies**:
   ```bash
   cd apps/web
   npm install
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Generate Prisma client**:
   ```bash
   npx prisma generate
   ```

4. **Run database migrations**:
   ```bash
   npx prisma db push
   ```

5. **Start development server**:
   ```bash
   npm run dev
   ```

The application will be available at http://localhost:3000

## 📁 Project Structure

```
apps/web/
├── app/                    # Next.js App Router
│   ├── api/               # API routes
│   ├── dashboard/         # Dashboard pages
│   ├── components/        # React components
│   └── lib/               # Utility functions
├── prisma/                # Database schema
├── public/                # Static assets
└── styles/                # Global styles
```

## 🎨 Components

### Core Components

- **Hero**: Landing page hero section
- **Features**: Feature showcase
- **Pricing**: Pricing plans
- **DashboardHeader**: Dashboard navigation
- **StatsCards**: Analytics cards
- **RecentActivity**: Activity feed

### Styling

The application uses Tailwind CSS with custom components defined in `globals.css`:

- `.btn-primary`: Primary button style
- `.btn-secondary`: Secondary button style
- `.card`: Card container style

## 🔐 Authentication

Authentication is handled by NextAuth.js with Google OAuth:

1. Set up Google OAuth credentials
2. Configure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
3. Users can sign in with their Google account

## 🗄️ Database

The web app uses Prisma to interact with PostgreSQL:

- **Users**: User accounts and profiles
- **Agents**: AI agents configuration
- **Tasks**: Task management
- **ApiCalls**: API usage tracking

## 🚀 Deployment

### Local Development

```bash
npm run dev
```

### Production Build

```bash
npm run build
npm start
```

### Docker

```bash
docker build -t web-app .
docker run -p 3000:3000 web-app
```

## 📝 Scripts

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run lint`: Run ESLint

## 🔧 Configuration

### Environment Variables

```env
# NextAuth.js
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_secret_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_microsaas

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Tailwind Configuration

Custom colors and utilities are defined in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        50: '#eff6ff',
        500: '#3b82f6',
        600: '#2563eb',
        700: '#1d4ed8',
      },
    },
  },
}
```

## 🧪 Testing

```bash
npm run test
```

## 📊 Performance

- **Image Optimization**: Next.js automatic image optimization
- **Code Splitting**: Automatic code splitting by route
- **Static Generation**: Pre-rendered pages for better performance
- **Bundle Analysis**: Use `npm run analyze` to analyze bundle size

## 🔍 SEO

- **Metadata**: Automatic metadata generation
- **Open Graph**: Social media sharing optimization
- **Sitemap**: Automatic sitemap generation
- **Robots.txt**: Search engine crawling configuration