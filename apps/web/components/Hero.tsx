"use client";

import { signIn } from "next-auth/react";
import { ArrowRightIcon } from "@heroicons/react/24/outline";

export function Hero() {
  return (
    <div className="relative isolate px-6 pt-14 lg:px-8">
      <div className="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
            AI-Powered MicroSaaS Platform
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Build, deploy, and scale intelligent applications with our
            comprehensive agentic microsaas starter. Everything you need to
            launch your next AI-powered business.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <button
              onClick={() => signIn("google")}
              className="btn-primary flex items-center gap-2"
            >
              Get Started
              <ArrowRightIcon className="h-4 w-4" />
            </button>
            <button className="btn-secondary">Learn More</button>
          </div>
        </div>
      </div>
    </div>
  );
}
