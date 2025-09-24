const features = [
  {
    name: "AI Agents",
    description:
      "Intelligent agents that can process tasks, make decisions, and interact with users autonomously.",
    icon: "🤖",
  },
  {
    name: "Vector Database",
    description:
      "Built-in pgvector support for semantic search and AI-powered recommendations.",
    icon: "🔍",
  },
  {
    name: "Real-time Processing",
    description:
      "Background task processing with Celery and Redis for scalable operations.",
    icon: "⚡",
  },
  {
    name: "Cloud Ready",
    description:
      "Deploy to Google Cloud Run with Terraform infrastructure as code.",
    icon: "☁️",
  },
  {
    name: "Modern Stack",
    description:
      "Next.js, FastAPI, and Python with TypeScript support throughout.",
    icon: "⚛️",
  },
  {
    name: "Authentication",
    description:
      "Secure authentication with NextAuth.js and Google OAuth integration.",
    icon: "🔐",
  },
];

export function Features() {
  return (
    <div className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-primary-600">
            Everything you need
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Complete microsaas platform
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            A production-ready starter that includes all the essential
            components for building and scaling AI-powered applications.
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
            {features.map((feature) => (
              <div key={feature.name} className="flex flex-col">
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
                  <span className="text-2xl">{feature.icon}</span>
                  {feature.name}
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">{feature.description}</p>
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  );
}
