const activities = [
  {
    id: 1,
    type: "agent",
    description: 'AI agent completed task: "Process customer inquiry"',
    timestamp: "2 minutes ago",
    status: "completed",
  },
  {
    id: 2,
    type: "api",
    description: "API call to OpenAI GPT-4 completed successfully",
    timestamp: "5 minutes ago",
    status: "completed",
  },
  {
    id: 3,
    type: "task",
    description: 'Background task "Send email notification" queued',
    timestamp: "10 minutes ago",
    status: "pending",
  },
  {
    id: 4,
    type: "agent",
    description: 'AI agent started processing: "Analyze user feedback"',
    timestamp: "15 minutes ago",
    status: "processing",
  },
];

export function RecentActivity() {
  return (
    <div className="card">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Recent Activity
      </h3>
      <div className="flow-root">
        <ul className="-mb-8">
          {activities.map((activity, activityIdx) => (
            <li key={activity.id}>
              <div className="relative pb-8">
                {activityIdx !== activities.length - 1 ? (
                  <span
                    className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                    aria-hidden="true"
                  />
                ) : null}
                <div className="relative flex space-x-3">
                  <div>
                    <span
                      className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                        activity.status === "completed"
                          ? "bg-green-500"
                          : activity.status === "processing"
                          ? "bg-blue-500"
                          : "bg-yellow-500"
                      }`}
                    >
                      <span className="text-white text-xs font-bold">
                        {activity.type === "agent"
                          ? "🤖"
                          : activity.type === "api"
                          ? "🔌"
                          : "📋"}
                      </span>
                    </span>
                  </div>
                  <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                    <div>
                      <p className="text-sm text-gray-500">
                        {activity.description}
                      </p>
                    </div>
                    <div className="text-right text-sm whitespace-nowrap text-gray-500">
                      {activity.timestamp}
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
