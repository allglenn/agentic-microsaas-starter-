"use client";

import { signIn } from "next-auth/react";
import { FaGoogle, FaGithub, FaMicrosoft, FaApple } from "react-icons/fa";

interface SocialLoginProps {
  mode?: "login" | "register";
  className?: string;
}

export function SocialLogin({
  mode = "login",
  className = "",
}: SocialLoginProps) {
  const handleSocialLogin = (provider: string) => {
    signIn(provider, {
      callbackUrl: "/dashboard",
      redirect: true,
    });
  };

  const socialProviders = [
    {
      id: "google",
      name: "Google",
      icon: FaGoogle,
      color: "bg-red-500 hover:bg-red-600",
      textColor: "text-white",
    },
    {
      id: "github",
      name: "GitHub",
      icon: FaGithub,
      color: "bg-gray-800 hover:bg-gray-900",
      textColor: "text-white",
    },
    {
      id: "microsoft-entra-id",
      name: "Microsoft",
      icon: FaMicrosoft,
      color: "bg-blue-600 hover:bg-blue-700",
      textColor: "text-white",
    },
    {
      id: "apple",
      name: "Apple",
      icon: FaApple,
      color: "bg-black hover:bg-gray-900",
      textColor: "text-white",
    },
  ];

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-300" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-white text-gray-500">
            {mode === "login" ? "Or continue with" : "Or sign up with"}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {socialProviders.map((provider) => {
          const Icon = provider.icon;
          return (
            <button
              key={provider.id}
              onClick={() => handleSocialLogin(provider.id)}
              className={`w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium ${provider.color} ${provider.textColor} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200`}
            >
              <Icon className="h-5 w-5 mr-2" />
              {provider.name}
            </button>
          );
        })}
      </div>

      <div className="text-xs text-gray-500 text-center">
        By continuing, you agree to our{" "}
        <a href="/terms" className="text-indigo-600 hover:text-indigo-500">
          Terms of Service
        </a>{" "}
        and{" "}
        <a href="/privacy" className="text-indigo-600 hover:text-indigo-500">
          Privacy Policy
        </a>
      </div>
    </div>
  );
}

// Individual provider buttons for more flexibility
export function GoogleLoginButton({ className = "" }: { className?: string }) {
  return (
    <button
      onClick={() => signIn("google", { callbackUrl: "/dashboard" })}
      className={`w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium bg-red-500 hover:bg-red-600 text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200 ${className}`}
    >
      <FaGoogle className="h-5 w-5 mr-2" />
      Continue with Google
    </button>
  );
}

export function GitHubLoginButton({ className = "" }: { className?: string }) {
  return (
    <button
      onClick={() => signIn("github", { callbackUrl: "/dashboard" })}
      className={`w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium bg-gray-800 hover:bg-gray-900 text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 ${className}`}
    >
      <FaGithub className="h-5 w-5 mr-2" />
      Continue with GitHub
    </button>
  );
}

export function MicrosoftLoginButton({
  className = "",
}: {
  className?: string;
}) {
  return (
    <button
      onClick={() =>
        signIn("microsoft-entra-id", { callbackUrl: "/dashboard" })
      }
      className={`w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 ${className}`}
    >
      <FaMicrosoft className="h-5 w-5 mr-2" />
      Continue with Microsoft
    </button>
  );
}

export function AppleLoginButton({ className = "" }: { className?: string }) {
  return (
    <button
      onClick={() => signIn("apple", { callbackUrl: "/dashboard" })}
      className={`w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium bg-black hover:bg-gray-900 text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200 ${className}`}
    >
      <FaApple className="h-5 w-5 mr-2" />
      Continue with Apple
    </button>
  );
}
