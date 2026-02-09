import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import AnalyticsLayout from './pages/AnalyticsLayout'
import SessionHistory from './pages/SessionHistory'
import SuccessRate from './pages/SuccessRate'
import BrowserComparison from './pages/BrowserComparison'
import FailureTypes from './pages/FailureTypes'
import './App.css'

const API_URL = 'http://localhost:3001'

function Home() {
  const [bugReport, setBugReport] = useState('')
  const [url, setUrl] = useState('')
  const [githubUrl, setGithubUrl] = useState('')
  const [sessions, setSessions] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const [loading, setLoading] = useState(false)
  const [importing, setImporting] = useState(false)
  const [error, setError] = useState('')

  // Poll for session updates
  useEffect(() => {
    if (!activeSession) return

    const interval = setInterval(async () => {
      const res = await fetch(`${API_URL}/status/${activeSession}`)
      const data = await res.json()
      setSessions(prev => prev.map(s => s.id === activeSession ? data : s))
    }, 2000)

    return () => clearInterval(interval)
  }, [activeSession])

  const handleGitHubImport = async () => {
    if (!githubUrl.trim()) return
    setImporting(true)
    setError('')

    try {
      const res = await fetch(`${API_URL}/github/fetch-issue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: githubUrl })
      })

      if (!res.ok) throw new Error("Failed to fetch issue")

      const data = await res.json()
      setBugReport(`${data.title}\n\n${data.body}`)
      if (data.url) {
        setUrl(data.url)
      } else {
        setError("Issue imported, but no target URL found. Please enter it manually.")
      }
      setGithubUrl('')
    } catch (err) {
      setError(err.message)
    }
    setImporting(false)
  }

  const handleAnalyze = async () => {
    if (!bugReport.trim()) {
      setError("Please describe the bug.")
      return
    }
    if (!url.trim()) {
      setError("URL is required for reproduction.")
      return
    }
    setError('')
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: bugReport, url: url })
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || "Analysis failed")
      }

      const session = await res.json()
      setSessions(prev => [...prev, session])
      setActiveSession(session.id)
      setBugReport('')
      setUrl('')
    } catch (err) {
      console.error('Analysis failed:', err)
      setError(err.message)
    }
    setLoading(false)
  }

  const handleReproduce = async (sessionId) => {
    try {
      await fetch(`${API_URL}/reproduce/${sessionId}`, { method: 'POST' })
    } catch (err) {
      console.error('Reproduction failed:', err)
    }
  }

  const currentSession = sessions.find(s => s.id === activeSession)

  return (
    <div className="home-container">
      {/* Bug Report Input */}
      <section className="panel input-panel">
        <h2>📝 Submit Bug Report</h2>

        {/* GitHub Import Section */}
        <div className="github-import">
          <input
            type="text"
            placeholder="Paste GitHub Issue URL (e.g., https://github.com/owner/repo/issues/1)"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
            className="github-input"
          />
          <button
            onClick={handleGitHubImport}
            disabled={importing || !githubUrl}
            className="btn-secondary btn-sm"
          >
            {importing ? '⏳ Importing...' : '📥 Import'}
          </button>
        </div>

        <div className="divider">OR</div>

        <textarea
          placeholder="Describe the bug... (e.g., 'Login button doesn't work on mobile Safari')"
          value={bugReport}
          onChange={(e) => setBugReport(e.target.value)}
          rows={4}
        />
        <input
          type="url"
          placeholder="URL to test (Required)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className={!url && error ? "error-input" : ""}
        />
        {error && <p className="error-msg">{error}</p>}
        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? '🔄 Analyzing...' : '🚀 Analyze Bug'}
        </button>
      </section>

      {/* Sessions List */}
      <section className="panel sessions-panel">
        <h2>📋 Recent Sessions</h2>
        {sessions.length === 0 ? (
          <p className="empty">No sessions yet.</p>
        ) : (
          <ul className="session-list">
            {sessions.map(session => (
              <li
                key={session.id}
                className={`session-item ${activeSession === session.id ? 'active' : ''}`}
                onClick={() => setActiveSession(session.id)}
              >
                <span className="session-id">#{session.id}</span>
                <span className={`status status-${session.status}`}>{session.status}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Active Session Details */}
      {currentSession && (
        <section className="panel details-panel">
          <div className="details-header">
            <h2>🔍 Session #{currentSession.id}</h2>
            <span className={`status status-${currentSession.status}`}>
              {currentSession.status}
            </span>
          </div>

          {/* Thoughts (AI Reasoning) */}
          {currentSession.thoughts.length > 0 && (
            <div className="thoughts-section">
              <h3>💭 AI Thoughts</h3>
              <div className="thoughts-list">
                {currentSession.thoughts.map((thought, i) => (
                  <div key={i} className="thought">{thought}</div>
                ))}
              </div>
            </div>
          )}

          {/* Logs */}
          <div className="logs-section">
            <h3>📜 Logs</h3>
            <div className="logs">
              {currentSession.logs.map((log, i) => (
                <div key={i} className="log-line">{log}</div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="actions">
            {currentSession.status === 'analyzed' && (
              <button
                className="btn-secondary"
                onClick={() => handleReproduce(currentSession.id)}
              >
                ▶️ Start Reproduction
              </button>
            )}
          </div>

          {/* Dockerfile Output */}
          {currentSession.dockerfile && (
            <div className="dockerfile-section">
              <h3>📦 Generated Dockerfile</h3>
              <pre className="dockerfile">{currentSession.dockerfile}</pre>
            </div>
          )}
        </section>
      )}
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="header">
          <div className="header-left">
            <h1>🤖 Self-Healing Sandbox</h1>
            <p className="subtitle">Autonomous QA Agent</p>
          </div>
          <nav className="header-nav">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/analytics/history" className="nav-link">Analytics</Link>
          </nav>
        </header>

        <main className="main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analytics" element={<AnalyticsLayout />}>
              <Route path="history" element={<SessionHistory />} />
              <Route path="success-rate" element={<SuccessRate />} />
              <Route path="browsers" element={<BrowserComparison />} />
              <Route path="failures" element={<FailureTypes />} />
            </Route>
          </Routes>
        </main>

        <footer className="footer">
          <p>Backend: FastAPI • AI: Gemini • Sandbox: E2B</p>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
