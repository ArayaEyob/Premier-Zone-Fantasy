import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaSync, FaFootballBall, FaUsers, FaClock, FaTrophy, FaChartLine } from 'react-icons/fa';
import './StatsDashboard.scss';

const StatsDashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);
    const [autoRefresh, setAutoRefresh] = useState(true);

    const API_BASE_URL = 'http://localhost:5000/api';

    const fetchStats = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await axios.get(`${API_BASE_URL}/stats`);
            setStats(response.data);
            setLastUpdate(new Date());
            
        } catch (err) {
            setError('Failed to fetch stats. Make sure the API server is running.');
            console.error('Stats fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const triggerManualUpdate = async () => {
        try {
            setLoading(true);
            await axios.get(`${API_BASE_URL}/stats/update`);
            
            // Wait a bit for the update to complete, then fetch new data
            setTimeout(() => {
                fetchStats();
            }, 3000);
            
        } catch (err) {
            setError('Failed to trigger stats update');
            console.error('Update trigger error:', err);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();

        // Set up auto-refresh every 5 minutes if enabled
        let interval;
        if (autoRefresh) {
            interval = setInterval(fetchStats, 300000); // 5 minutes
        }

        return () => {
            if (interval) clearInterval(interval);
        };
    }, [autoRefresh]);

    const formatLastUpdate = (date) => {
        if (!date) return 'Never';
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    if (loading && !stats) {
        return (
            <div className="stats-dashboard loading">
                <div className="loading-spinner">
                    <FaSync className="spin" />
                    <p>Loading Premier League stats...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="stats-dashboard error">
                <div className="error-message">
                    <h2>⚠️ Error Loading Stats</h2>
                    <p>{error}</p>
                    <button onClick={fetchStats} className="retry-button">
                        <FaSync /> Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="stats-dashboard">
            {/* Header */}
            <div className="dashboard-header">
                <div className="header-content">
                    <h1><FaChartLine /> Premier League Live Stats</h1>
                    <div className="header-controls">
                        <div className="last-update">
                            <FaClock />
                            <span>Updated: {formatLastUpdate(lastUpdate)}</span>
                        </div>
                        <div className="control-buttons">
                            <button 
                                onClick={() => setAutoRefresh(!autoRefresh)}
                                className={`toggle-button ${autoRefresh ? 'active' : ''}`}
                            >
                                Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
                            </button>
                            <button onClick={fetchStats} className="refresh-button">
                                <FaSync className={loading ? 'spin' : ''} /> Refresh
                            </button>
                            <button onClick={triggerManualUpdate} className="update-button">
                                <FaFootballBall /> Update Data
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Quick Stats Cards */}
            <div className="quick-stats">
                <div className="stat-card">
                    <div className="stat-icon">
                        <FaUsers />
                    </div>
                    <div className="stat-content">
                        <div className="stat-number">{stats?.total_players || 0}</div>
                        <div className="stat-label">Players</div>
                    </div>
                </div>
                
                <div className="stat-card">
                    <div className="stat-icon">
                        <FaFootballBall />
                    </div>
                    <div className="stat-content">
                        <div className="stat-number">{stats?.total_teams || 0}</div>
                        <div className="stat-label">Teams</div>
                    </div>
                </div>
                
                <div className="stat-card highlight">
                    <div className="stat-icon">
                        <FaTrophy />
                    </div>
                    <div className="stat-content">
                        <div className="stat-number">
                            {stats?.top_scorers?.[0]?.Gls || 0}
                        </div>
                        <div className="stat-label">Top Goals</div>
                        <div className="stat-sublabel">
                            {stats?.top_scorers?.[0]?.Player || 'N/A'}
                        </div>
                    </div>
                </div>

                <div className="stat-card highlight">
                    <div className="stat-icon">
                        <FaTrophy />
                    </div>
                    <div className="stat-content">
                        <div className="stat-number">
                            {stats?.top_assists?.[0]?.Ast || 0}
                        </div>
                        <div className="stat-label">Top Assists</div>
                        <div className="stat-sublabel">
                            {stats?.top_assists?.[0]?.Player || 'N/A'}
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="dashboard-content">
                
                {/* Top Scorers */}
                <div className="stats-section">
                    <h2>🥅 Top Scorers</h2>
                    <div className="stats-table">
                        {stats?.top_scorers?.slice(0, 10).map((player, index) => (
                            <div key={index} className="stats-row">
                                <div className="rank">#{index + 1}</div>
                                <div className="player-info">
                                    <div className="player-name">{player.Player}</div>
                                    <div className="player-team">{player.Team}</div>
                                </div>
                                <div className="player-stats">
                                    <span className="goals">{player.Gls}⚽</span>
                                    <span className="assists">{player.Ast}🎯</span>
                                    <span className="points">{player.total_points}pts</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Top Assists */}
                <div className="stats-section">
                    <h2>🎯 Top Assist Providers</h2>
                    <div className="stats-table">
                        {stats?.top_assists?.slice(0, 10).map((player, index) => (
                            <div key={index} className="stats-row">
                                <div className="rank">#{index + 1}</div>
                                <div className="player-info">
                                    <div className="player-name">{player.Player}</div>
                                    <div className="player-team">{player.Team}</div>
                                </div>
                                <div className="player-stats">
                                    <span className="assists primary">{player.Ast}🎯</span>
                                    <span className="goals">{player.Gls}⚽</span>
                                    <span className="points">{player.total_points}pts</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Fantasy Points Leaders */}
                <div className="stats-section">
                    <h2>👑 Fantasy Points Leaders</h2>
                    <div className="stats-table">
                        {stats?.top_points?.slice(0, 10).map((player, index) => (
                            <div key={index} className="stats-row">
                                <div className="rank">#{index + 1}</div>
                                <div className="player-info">
                                    <div className="player-name">{player.Player}</div>
                                    <div className="player-team">{player.Team}</div>
                                </div>
                                <div className="player-stats">
                                    <span className="points primary">{player.total_points}pts</span>
                                    <span className="goals">{player.Gls}⚽</span>
                                    <span className="assists">{player.Ast}🎯</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Team Statistics */}
                <div className="stats-section full-width">
                    <h2>🏟️ Team Statistics</h2>
                    <div className="team-stats-grid">
                        {stats?.team_stats?.sort((a, b) => b.TotalPoints - a.TotalPoints).map((team, index) => (
                            <div key={index} className="team-card">
                                <div className="team-header">
                                    <h3>{team.Team}</h3>
                                    <div className="team-rank">#{index + 1}</div>
                                </div>
                                <div className="team-stats">
                                    <div className="stat-item">
                                        <span className="label">Players:</span>
                                        <span className="value">{team.PlayerCount}</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="label">Goals:</span>
                                        <span className="value">{team.TotalGoals}⚽</span>
                                    </div>
                                    <div className="stat-item">
                                        <span className="label">Assists:</span>
                                        <span className="value">{team.TotalAssists}🎯</span>
                                    </div>
                                    <div className="stat-item primary">
                                        <span className="label">Points:</span>
                                        <span className="value">{team.TotalPoints}pts</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Loading Overlay */}
            {loading && stats && (
                <div className="loading-overlay">
                    <FaSync className="spin" />
                </div>
            )}
        </div>
    );
};

export default StatsDashboard;