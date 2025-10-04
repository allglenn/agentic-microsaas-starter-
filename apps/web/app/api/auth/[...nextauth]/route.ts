import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import GitHubProvider from 'next-auth/providers/github'
import MicrosoftProvider from 'next-auth/providers/microsoft-entra-id'
import AppleProvider from 'next-auth/providers/apple'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { prisma } from '@/lib/prisma'

const handler = NextAuth({
    adapter: PrismaAdapter(prisma),
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
    callbacks: {
        session: async ({ session, token, user }) => {
            if (session?.user) {
                session.user.id = token?.sub || user?.id
                // Add provider information to session
                session.user.provider = token?.provider
            }
            return session
        },
        jwt: async ({ user, token, account }) => {
            if (user) {
                token.uid = user.id
            }
            if (account) {
                token.provider = account.provider
            }
            return token
        },
        signIn: async ({ user, account, profile }) => {
            // Allow all social sign-ins
            if (account?.provider === 'google' ||
                account?.provider === 'github' ||
                account?.provider === 'microsoft-entra-id' ||
                account?.provider === 'apple') {
                return true
            }
            return true
        },
    },
    session: {
        strategy: 'jwt',
    },
})

export { handler as GET, handler as POST }
