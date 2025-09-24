const stats = [
  {
    name: "Total API Calls",
    value: "12,345",
    change: "+12%",
    changeType: "positive",
  },
  {
    name: "Active Agents",
    value: "8",
    change: "+2",
    changeType: "positive",
  },
  {
    name: "Tasks Completed",
    value: "1,234",
    change: "+8%",
    changeType: "positive",
  },
  {
    name: "Success Rate",
    value: "99.2%",
    change: "+0.1%",
    changeType: "positive",
  },
];

export function StatsCards() {
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <div key={stat.name} className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="text-sm font-medium text-gray-500">
                {stat.name}
              </div>
              <div className="text-2xl font-semibold text-gray-900">
                {stat.value}
              </div>
            </div>
          </div>
          <div className="mt-2">
            <span
              className={`text-sm font-medium ${
                stat.changeType === "positive"
                  ? "text-green-600"
                  : "text-red-600"
              }`}
            >
              {stat.change}
            </span>
            <span className="text-sm text-gray-500 ml-1">from last month</span>
          </div>
        </div>
      ))}
    </div>
  );
}
