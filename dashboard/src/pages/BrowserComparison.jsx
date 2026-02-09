import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const API_URL = 'http://localhost:3001'

export default function BrowserComparison() {
    const [browserStats, setBrowserStats] = useState({})
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch(`${API_URL}/analytics/browsers`)
            .then(res => res.json())
            .then(data => {
                setBrowserStats(data.browsers || {})
                setLoading(false)
            })
            .catch(err => {
                console.error(err)
                setLoading(false)
            })
    }, [])

    if (loading) return <div>Loading...</div>

    // Transform data for recharts
    const data = Object.keys(browserStats).map(browser => ({
        name: browser,
        total: browserStats[browser].total,
        success: browserStats[browser].success,
        successRate: browserStats[browser].total > 0
            ? Math.round((browserStats[browser].success / browserStats[browser].total) * 100)
            : 0
    }))

    return (
        <div className="analytics-page">
            <h2>🌐 Browser Comparison</h2>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="total" fill="#8884d8" name="Total Runs" />
                    <Bar dataKey="success" fill="#82ca9d" name="Successes" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    )
}
