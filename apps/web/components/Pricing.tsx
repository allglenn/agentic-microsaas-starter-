const tiers = [
  {
    name: "Starter",
    id: "starter",
    href: "#",
    priceMonthly: "$29",
    description:
      "Perfect for getting started with your first AI-powered application.",
    features: [
      "Up to 1,000 API calls/month",
      "Basic AI agents",
      "Email support",
      "Standard infrastructure",
    ],
    mostPopular: false,
  },
  {
    name: "Professional",
    id: "professional",
    href: "#",
    priceMonthly: "$99",
    description: "For growing businesses that need more power and features.",
    features: [
      "Up to 10,000 API calls/month",
      "Advanced AI agents",
      "Priority support",
      "Enhanced infrastructure",
      "Custom integrations",
    ],
    mostPopular: true,
  },
  {
    name: "Enterprise",
    id: "enterprise",
    href: "#",
    priceMonthly: "Custom",
    description: "For large organizations with specific requirements.",
    features: [
      "Unlimited API calls",
      "Custom AI models",
      "Dedicated support",
      "Private infrastructure",
      "Custom integrations",
      "SLA guarantee",
    ],
    mostPopular: false,
  },
];

export function Pricing() {
  return (
    <div className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-base font-semibold leading-7 text-primary-600">
            Pricing
          </h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
            Choose the right plan for you
          </p>
        </div>
        <div className="isolate mx-auto mt-16 grid max-w-md grid-cols-1 gap-y-8 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-3 lg:gap-x-8">
          {tiers.map((tier) => (
            <div
              key={tier.id}
              className={`card ${
                tier.mostPopular ? "ring-2 ring-primary-600" : ""
              }`}
            >
              {tier.mostPopular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-primary-600 text-white px-3 py-1 text-sm font-medium rounded-full">
                    Most popular
                  </span>
                </div>
              )}
              <h3 className="text-lg font-semibold leading-8 text-gray-900">
                {tier.name}
              </h3>
              <p className="mt-4 text-sm leading-6 text-gray-600">
                {tier.description}
              </p>
              <p className="mt-6 flex items-baseline gap-x-1">
                <span className="text-4xl font-bold tracking-tight text-gray-900">
                  {tier.priceMonthly}
                </span>
                {tier.priceMonthly !== "Custom" && (
                  <span className="text-sm font-semibold leading-6 text-gray-600">
                    /month
                  </span>
                )}
              </p>
              <button
                className={`mt-6 w-full ${
                  tier.mostPopular ? "btn-primary" : "btn-secondary"
                }`}
              >
                Get started
              </button>
              <ul className="mt-8 space-y-3 text-sm leading-6 text-gray-600">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex gap-x-3">
                    <span className="text-primary-600">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
