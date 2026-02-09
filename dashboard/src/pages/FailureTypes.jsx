import { useState, useEffect } from 'react'

const API_URL = 'http://localhost:3001'

export default function FailureTypes() {
    const [failures, setFailures] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch(`${API_URL}/analytics/history`)
            .then(res => res.json())
            .then(data => {
                const failedSessions = (data.history || []).filter(s => s.status === 'failed' || s.status === 'error')

                // Count failure types
                const counts = {}
                failedSessions.forEach(s => {
                    let type = "Unknown Error"
                    // Simple heuristic logic (could be improved with dedicated failure classification in backend)
                    const lastLog = s.logs[s.logs.length - 1] || ""
                    if (lastLog.includes("Timeout")) type = "Timeout ⏱️"
                    else if (lastLog.includes("Selector")) type = "Element Not Found 🔍"
                    else if (lastLog.includes("Network")) type = "Network Error 🌐"
                    else if (lastLog.includes("SyntaxError")) type = "Script Engine Error 🐍"

                    counts[type] = (counts[type] || 0) + 1
                })

                setFailures(Object.entries(counts).map(([name, count]) => ({ name, count })))
                setLoading(false)
            })
            .catch(err => {
                console.error(err)
                setLoading(false)
            })
    }, [])

    if (loading) return <div>Loading...</div>

    return (
        <div className="analytics-page">
            <h2>⚠️ Failure Analysis</h2>
            {failures.length === 0 ? (
                <p>No failures recorded! 🎉</p>
            ) : (
                <ul className="failure-list">
                    {failures.map((f, i) => (
                        <li key={i} className="failure-item">
                            <span className="failure-name">{f.name}</span>
                            <span className="failure-count">{f.count}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}
