import Link from 'next/link'

export default function Home() {
  return (
    <main className="max-w-lg mx-auto p-4 pb-20">
      {/* Weather Bar */}
      <div className="bg-green-600 text-white rounded-xl p-4 mb-4">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm opacity-80">Today</p>
            <p className="text-3xl font-bold">72°F</p>
            <p className="text-sm">Partly cloudy</p>
          </div>
          <div className="text-right">
            <p className="text-sm">🌧️ 40% rain</p>
            <p className="text-sm">💨 12 mph</p>
            <p className="text-sm">💧 65%</p>
          </div>
        </div>
      </div>

      {/* Weekly Advisor Preview */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold mb-2">This Week's Actions</h2>
        <div className="space-y-2">
          <ActionCard
            priority="critical"
            title="Frost Protection Needed"
            summary="Temperature dropping to 28°F Thursday night. Cover sensitive crops."
            category="weather"
          />
          <ActionCard
            priority="high"
            title="Apply Nitrogen Before Rain"
            summary="Rain expected Friday. Apply nitrogen to North Field before then."
            category="fertilization"
          />
          <ActionCard
            priority="medium"
            title="Schedule Irrigation"
            summary="Soil moisture low. No rain expected for 5 days."
            category="irrigation"
          />
        </div>
      </div>

      {/* Field Status */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold mb-2">Your Fields</h2>
        <div className="space-y-2">
          <FieldCard name="North Field" crop="Corn" stage="V6" status="growing" />
          <FieldCard name="South Forty" crop="Soybeans" stage="V3" status="growing" />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
        <nav className="max-w-lg mx-auto flex justify-around py-2">
          <NavItem href="/" label="Home" active />
          <NavItem href="/advisor" label="Advisor" />
          <NavItem href="/fields" label="Fields" />
          <NavItem href="/settings" label="Settings" />
          <NavItem href="/my-harvest" label="My Harvest" />
        </nav>
      </div>
    </main>
  )
}

function ActionCard({ priority, title, summary, category }: {
  priority: string
  title: string
  summary: string
  category: string
}) {
  const colors = {
    critical: 'border-red-500 bg-red-50',
    high: 'border-orange-500 bg-orange-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-green-500 bg-green-50',
  }

  return (
    <div className={`border-l-4 rounded-r-lg p-3 ${colors[priority as keyof typeof colors]}`}>
      <div className="flex justify-between items-start">
        <div>
          <p className="font-medium">{title}</p>
          <p className="text-sm text-gray-600 mt-1">{summary}</p>
        </div>
        <div className="flex gap-2 ml-2">
          <button className="text-green-600 text-sm font-medium px-3 py-1 rounded-full bg-green-100">
            Done
          </button>
          <button className="text-gray-500 text-sm font-medium px-3 py-1 rounded-full bg-gray-100">
            Skip
          </button>
        </div>
      </div>
    </div>
  )
}

function FieldCard({ name, crop, stage, status }: {
  name: string
  crop: string
  stage: string
  status: string
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-3 flex justify-between items-center">
      <div>
        <p className="font-medium">{name}</p>
        <p className="text-sm text-gray-500">{crop} — {stage}</p>
      </div>
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        status === 'growing' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
      }`}>
        {status}
      </span>
    </div>
  )
}

function NavItem({ href, label, active }: { href: string; label: string; active?: boolean }) {
  return (
    <Link href={href} className={`flex flex-col items-center py-1 ${
      active ? 'text-green-600' : 'text-gray-500'
    }`}>
      <span className="text-xs">{label}</span>
    </Link>
  )
}
