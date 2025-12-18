import { useState, useEffect } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

function App() {
  const [eventText, setEventText] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])
  const [leaders, setLeaders] = useState([])
  const [activeTab, setActiveTab] = useState('simulate')

  useEffect(() => {
    fetchHistory()
    fetchLeaders()
  }, [])

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/history`)
      const data = await res.json()
      setHistory(data)
    } catch (err) {
      console.error('Failed to fetch history:', err)
    }
  }

  const fetchLeaders = async () => {
    try {
      const res = await fetch(`${API_URL}/leaders`)
      const data = await res.json()
      setLeaders(data)
    } catch (err) {
      console.error('Failed to fetch leaders:', err)
    }
  }

  const runSimulation = async (e) => {
    e.preventDefault()
    if (!eventText.trim()) return

    setLoading(true)
    setResults(null)

    try {
      const res = await fetch(`${API_URL}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: eventText }),
      })
      const data = await res.json()
      setResults(data)
      fetchHistory()
    } catch (err) {
      console.error('Simulation failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 7) return '#e74c3c'
    if (score >= 4) return '#f39c12'
    return '#27ae60'
  }

  return (
    <div className="app">
      <header>
        <h1>Polaris</h1>
        <p>Multi-Agent Crisis Response Simulation</p>
      </header>

      <nav>
        <button
          className={activeTab === 'simulate' ? 'active' : ''}
          onClick={() => setActiveTab('simulate')}
        >
          Simulate
        </button>
        <button
          className={activeTab === 'history' ? 'active' : ''}
          onClick={() => setActiveTab('history')}
        >
          History
        </button>
        <button
          className={activeTab === 'leaders' ? 'active' : ''}
          onClick={() => setActiveTab('leaders')}
        >
          Leaders
        </button>
      </nav>

      <main>
        {activeTab === 'simulate' && (
          <div className="simulate-tab">
            <form onSubmit={runSimulation}>
              <textarea
                value={eventText}
                onChange={(e) => setEventText(e.target.value)}
                placeholder="Describe a geopolitical event... (e.g., 'China announces naval exercises near Taiwan')"
                rows={3}
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Running Simulation...' : 'Run Simulation'}
              </button>
            </form>

            {loading && (
              <div className="loading">
                <p>Analyzing with 4 leader agents...</p>
              </div>
            )}

            {results && (
              <div className="results">
                <h2>Simulation Results</h2>
                <p className="event-text">Event: {results.event_text}</p>

                <div className="leader-cards">
                  {results.results
                    .sort((a, b) => b.escalation_score - a.escalation_score)
                    .map((r, i) => (
                      <div key={i} className="leader-card">
                        <div className="leader-header">
                          <h3>{r.leader}</h3>
                          <span
                            className="score"
                            style={{ backgroundColor: getScoreColor(r.escalation_score) }}
                          >
                            {r.escalation_score.toFixed(1)}
                          </span>
                        </div>
                        <p className="reaction">{r.reaction}</p>
                        <p className="rationale">{r.rationale}</p>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-tab">
            <h2>Past Simulations</h2>
            {history.length === 0 ? (
              <p>No simulations yet.</p>
            ) : (
              <div className="history-list">
                {history.map((h, i) => (
                  <div key={i} className="history-item">
                    <p className="history-event">{h.event_text}</p>
                    <div className="history-meta">
                      <span>Avg Escalation: {h.avg_escalation}</span>
                      <span>{new Date(h.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'leaders' && (
          <div className="leaders-tab">
            <h2>Leader Archetypes</h2>
            <div className="leaders-grid">
              {leaders.map((l, i) => (
                <div key={i} className="leader-profile">
                  <h3>{l.name}</h3>
                  <div className="traits">
                    <div className="trait">
                      <span>Aggression</span>
                      <div className="bar">
                        <div style={{ width: `${l.aggression * 10}%` }}></div>
                      </div>
                    </div>
                    <div className="trait">
                      <span>Diplomacy</span>
                      <div className="bar">
                        <div style={{ width: `${l.diplomacy * 10}%` }}></div>
                      </div>
                    </div>
                    <div className="trait">
                      <span>Risk Tolerance</span>
                      <div className="bar">
                        <div style={{ width: `${l.risk_tolerance * 10}%` }}></div>
                      </div>
                    </div>
                    <div className="trait">
                      <span>Domestic Pressure</span>
                      <div className="bar">
                        <div style={{ width: `${l.domestic_pressure * 10}%` }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
