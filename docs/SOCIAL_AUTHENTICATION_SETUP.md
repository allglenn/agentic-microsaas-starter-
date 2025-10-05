# 🔐 Social Authentication Setup Guide

This guide will help you set up social authentication (Google, GitHub, Microsoft, Apple) for your Agentic MicroSaaS platform.

## 🚀 Quick Start

### 1. Environment Setup

Copy the environment file and add your OAuth credentials:

```bash
cp social-auth.env.example .env.local
```

### 2. OAuth Provider Setup

#### Google OAuth (Required)

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/apis/credentials
   - Select your project or create a new one

2. **Create OAuth 2.0 Credentials:**
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Application type: "Web application"
   - Name: "Agentic MicroSaaS"
   - Authorized redirect URIs:
     - `http://localhost:3000/api/auth/callback/google` (development)
     - `https://yourdomain.com/api/auth/callback/google` (production)

3. **Copy Credentials:**
   ```env
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

#### GitHub OAuth (Optional)

1. **Go to GitHub Developer Settings:**
   - Visit: https://github.com/settings/developers
   - Click "New OAuth App"

2. **Create OAuth App:**
   - Application name: "Agentic MicroSaaS"
   - Homepage URL: `http://localhost:3000` (or your domain)
   - Authorization callback URL: `http://localhost:3000/api/auth/callback/github`

3. **Copy Credentials:**
   ```env
   GITHUB_CLIENT_ID=your-github-client-id
   GITHUB_CLIENT_SECRET=your-github-client-secret
   ```

#### Microsoft OAuth (Optional)

1. **Go to Azure Portal:**
   - Visit: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
   - Click "New registration"

2. **Register Application:**
   - Name: "Agentic MicroSaaS"
   - Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
   - Redirect URI: `http://localhost:3000/api/auth/callback/microsoft-entra-id`

3. **Get Credentials:**
   - Go to "Certificates & secrets" → "New client secret"
   - Copy the Application (client) ID and secret

4. **Copy Credentials:**
   ```env
   MICROSOFT_CLIENT_ID=your-microsoft-client-id
   MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
   MICROSOFT_TENANT_ID=common
   ```

#### Apple OAuth (Optional)

1. **Go to Apple Developer Portal:**
   - Visit: https://developer.apple.com/account/resources/identifiers/list
   - Click "+" to create a new identifier

2. **Create Services ID:**
   - Identifier: `com.yourcompany.agentic-microsaas`
   - Description: "Agentic MicroSaaS"
   - Enable "Sign In with Apple"
   - Primary App ID: Select your app
   - Domains: `yourdomain.com`
   - Return URLs: `https://yourdomain.com/api/auth/callback/apple`

3. **Create Private Key:**
   - Go to "Keys" → "Create a key"
   - Key Name: "Agentic MicroSaaS Sign In"
   - Enable "Sign In with Apple"
   - Download the .p8 file

4. **Generate Client Secret:**
   ```bash
   # Install the Apple JWT generator
   npm install -g apple-signin-auth
   
   # Generate client secret
   apple-signin-auth generate-client-secret \
     --key-id YOUR_KEY_ID \
     --team-id YOUR_TEAM_ID \
     --private-key-path path/to/AuthKey_XXXXXXXXXX.p8
   ```

5. **Copy Credentials:**
   ```env
   APPLE_CLIENT_ID=com.yourcompany.agentic-microsaas
   APPLE_CLIENT_SECRET=your-generated-client-secret
   ```

## 🎨 Frontend Integration

### Using the SocialLogin Component

```tsx
import { SocialLogin } from '@/components/SocialLogin';

export default function LoginPage() {
  return (
    <div className="max-w-md mx-auto">
      <h1>Sign In</h1>
      
      {/* Your existing login form */}
      <form>
        {/* Email/password fields */}
      </form>
      
      {/* Social login buttons */}
      <SocialLogin mode="login" />
    </div>
  );
}
```

### Using Individual Provider Buttons

```tsx
import { 
  GoogleLoginButton, 
  GitHubLoginButton,
  MicrosoftLoginButton,
  AppleLoginButton 
} from '@/components/SocialLogin';

export default function LoginPage() {
  return (
    <div>
      <GoogleLoginButton />
      <GitHubLoginButton />
      <MicrosoftLoginButton />
      <AppleLoginButton />
    </div>
  );
}
```

## 🔧 Backend Integration

The NextAuth configuration is already set up in `app/api/auth/[...nextauth]/route.ts`:

```typescript
import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import GitHubProvider from 'next-auth/providers/github'
import MicrosoftProvider from 'next-auth/providers/microsoft-entra-id'
import AppleProvider from 'next-auth/providers/apple'

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
    MicrosoftProvider({
      clientId: process.env.MICROSOFT_CLIENT_ID!,
      clientSecret: process.env.MICROSOFT_CLIENT_SECRET!,
      tenantId: process.env.MICROSOFT_TENANT_ID!,
    }),
    AppleProvider({
      clientId: process.env.APPLE_CLIENT_ID!,
      clientSecret: process.env.APPLE_CLIENT_SECRET!,
    }),
  ],
  // ... rest of configuration
})
```

## 🚀 Testing

### 1. Start Development Server

```bash
npm run dev
```

### 2. Test Social Login

1. Visit `http://localhost:3000/api/auth/signin`
2. Click on any social provider button
3. Complete the OAuth flow
4. You should be redirected to `/dashboard`

### 3. Check User Data

After successful login, check the user data in your database:

```sql
SELECT * FROM users WHERE email = 'user@example.com';
```

## 🔒 Security Considerations

### 1. Environment Variables

- Never commit OAuth secrets to version control
- Use different credentials for development and production
- Rotate secrets regularly

### 2. Redirect URIs

- Always use HTTPS in production
- Validate redirect URIs to prevent open redirects
- Use specific domains, not wildcards

### 3. User Data

- Validate user data from OAuth providers
- Handle missing or incomplete profile information
- Implement proper error handling

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**
   - Check that your redirect URI matches exactly in the OAuth app settings
   - Ensure you're using the correct protocol (http/https)

2. **"Client ID not found"**
   - Verify your environment variables are set correctly
   - Check that the OAuth app is enabled

3. **"Access denied"**
   - User may have denied permission during OAuth flow
   - Check OAuth app permissions and scopes

4. **Apple Sign-In not working**
   - Ensure you're using HTTPS in production
   - Check that the Apple Developer account is active
   - Verify the client secret is valid and not expired

### Debug Mode

Enable NextAuth debug mode:

```env
NEXTAUTH_DEBUG=true
```

## 📚 Additional Resources

- [NextAuth.js Documentation](https://next-auth.js.org/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Microsoft OAuth Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [Apple Sign-In Documentation](https://developer.apple.com/sign-in-with-apple/)

## 🎯 Next Steps

1. **Set up OAuth apps** for your chosen providers
2. **Add environment variables** to your `.env.local`
3. **Test the integration** in development
4. **Deploy to production** with production OAuth apps
5. **Monitor usage** and user feedback

Your social authentication is now ready to use! 🎉
