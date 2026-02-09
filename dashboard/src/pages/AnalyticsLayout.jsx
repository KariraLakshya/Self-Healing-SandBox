import { Outlet, Link, useLocation } from 'react-router-dom'

export default function AnalyticsLayout() {
    const location = useLocation()

    return (
        <div className="analytics-layout">
            <nav className="analytics-nav">
                <Link to="/" className="nav-link">🏠 Home</Link>
                <div className="nav-divider">|</div>
                <Link
                    to="/analytics/history"
                    className={`nav-link ${location.pathname === '/analytics/history' ? 'active' : ''}`}
                >
                    📜 History
                </Link>
                <Link
                    to="/analytics/success-rate"
                    className={`nav-link ${location.pathname === '/analytics/success-rate' ? 'active' : ''}`}
                >
                    📈 Success Rate
                </Link>
                <Link
                    to="/analytics/browsers"
                    className={`nav-link ${location.pathname === '/analytics/browsers' ? 'active' : ''}`}
                >
                    🌐 Browsers
                </Link>
                <Link
                    to="/analytics/failures"
                    className={`nav-link ${location.pathname === '/analytics/failures' ? 'active' : ''}`}
                >
                    ⚠️ Failures
                </Link>
            </nav>

            <div className="analytics-content">
                <Outlet />
            </div>
        </div>
    )
}
