import { useState, useEffect } from 'react'

const API_URL = 'http://localhost:3001'

export default function SessionHistory() {
    const [history, setHistory] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch(`${API_URL}/analytics/history`)
            .then(res => res.json())
            .then(data => {
                setHistory(data.history || [])
                setLoading(false)
            })
            .catch(err => {
                console.error(err)
                setLoading(false)
            })
    }, [])

    if (loading) return <div className="loading">Loading history...</div>

    return (
        <div className="analytics-page">
            <h2>📜 Session History</h2>
            {history.length === 0 ? (
                <p>No sessions found.</p>
            ) : (
                <table className="history-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Status</th>
                            <th>Bug Description</th>
                            <th>URL</th>
                            <th>Browser</th>
                            <th>Artifacts</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history.map(session => (
                            <tr key={session.id}>
                                <td><code>#{session.id}</code></td>
                                <td>
                                    <span className={`status status-${session.status}`}>
                                        {session.status}
                                    </span>
                                </td>
                                <td className="desc-cell" title={session.bug_report?.description}>
                                    {session.bug_report?.description?.substring(0, 50)}...
                                </td>
                                <td>
                                    {session.bug_report?.url ? (
                                        <a href={session.bug_report.url} target="_blank" rel="noopener noreferrer">
                                            Link
                                        </a>
                                    ) : '-'}
                                </td>
                                <td>{session.bug_report?.browser || 'chromium'}</td>
                                <td>
                                    {session.dockerfile ? '🐳 Dockerfile' : '-'}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    )
}
