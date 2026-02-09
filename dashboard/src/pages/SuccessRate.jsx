import { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const API_URL = 'http://localhost:3001'
const COLORS = ['#10b981', '#ef4444', '#f59e0b']

export default function SuccessRate() {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetch(`${API_URL}/analytics/success-rate`)
            .then(res => res.json())
            .then(data => {
                setStats(data)
                setLoading(false)
            })
            .catch(err => {
                console.error(err)
                setLoading(false)
            })
    }, [])

    if (loading) return <div className="loading">Loading stats...</div>

    const data = stats ? [
        { name: 'Success', value: stats.success },
        { name: 'Failed', value: stats.failed },
        { name: 'Error', value: stats.error },
    ] : []

    return (
        <div className="analytics-page">
            <h2>📈 Success Rate Analysis</h2>

            <div className="stats-cards">
                <div className="stat-card">
                    <h3>Total Sessions</h3>
                    <p className="stat-value">{stats?.total || 0}</p>
                </div>
                <div className="stat-card success">
                    <h3>Success Rate</h3>
                    <p className="stat-value">{stats?.success_rate}%</p>
                </div>
            </div>

            <div className="chart-container">
                <h3>Outcome Distribution</h3>
                <div style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer>
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                outerRadius={100}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    )
}
