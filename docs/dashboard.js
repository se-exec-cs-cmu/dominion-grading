// Dashboard functionality
let dashboardData = null;
let chartInstances = {};

async function loadDashboardData() {
    try {
        // Add timestamp to prevent caching
        const response = await fetch(`data.json?t=${Date.now()}`);
        dashboardData = await response.json();
        updateDashboard();
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        document.getElementById('lastUpdate').textContent = 'Failed to load data';
    }
}

function updateDashboard() {
    if (!dashboardData) return;
    
    // Update last update time
    const lastUpdate = dashboardData.lastUpdate ? 
        new Date(dashboardData.lastUpdate).toLocaleString() : 
        'Never';
    document.getElementById('lastUpdate').textContent = lastUpdate;
    
    // Calculate statistics
    const teams = Object.entries(dashboardData.teams || {});
    const totalTeams = teams.length;
    const totalPoints = teams.reduce((sum, [_, team]) => sum + team.totalPoints, 0);
    const allMilestones = new Set();
    teams.forEach(([_, team]) => {
        team.completedMilestones.forEach(m => allMilestones.add(m));
    });
    
    // Update stats
    document.getElementById('totalTeams').textContent = totalTeams;
    document.getElementById('totalMilestones').textContent = allMilestones.size;
    document.getElementById('totalPoints').textContent = totalPoints;
    
    // Find most popular milestone
    const milestoneCounts = {};
    Object.values(dashboardData.milestoneStats || {}).forEach(milestone => {
        milestoneCounts[milestone.name] = milestone.completedBy?.length || 0;
    });
    const popularMilestone = Object.entries(milestoneCounts)
        .sort(([,a], [,b]) => b - a)[0];
    document.getElementById('popularMilestone').textContent = 
        popularMilestone ? `${popularMilestone[0]} (${popularMilestone[1]} teams)` : 'None yet';
    
    // Update leaderboard
    updateLeaderboard(teams);
    
    // Update activity feed
    updateActivityFeed();
    
    // Update milestone grid
    updateMilestoneGrid();
    
    // Update custom milestones section (NEW)
    updateCustomMilestones();
    
    // Update charts
    updateCharts(teams);
}

function updateLeaderboard(teams) {
    const tbody = document.getElementById('rankingsBody');
    tbody.innerHTML = '';
    
    // Sort teams by points
    teams.sort(([,a], [,b]) => b.totalPoints - a.totalPoints);
    
    teams.forEach(([teamName, teamData], index) => {
        const row = tbody.insertRow();
        
        // Add rank class for top 3
        if (index === 0) row.className = 'gold';
        else if (index === 1) row.className = 'silver';
        else if (index === 2) row.className = 'bronze';
        
        // Rank
        row.insertCell(0).textContent = index + 1;
        
        // Team name
        row.insertCell(1).textContent = teamName;
        
        // Points
        const pointsCell = row.insertCell(2);
        pointsCell.textContent = teamData.totalPoints;
        pointsCell.className = 'points';
        
        // Milestones completed
        row.insertCell(3).textContent = teamData.completedMilestones.length;
        
        // Custom achievements column (NEW)
        const customCell = row.insertCell(4);
        const customCount = teamData.customMilestones ? teamData.customMilestones.length : 0;
        if (customCount > 0) {
            customCell.innerHTML = `⭐ ${customCount}`;
            customCell.title = "Custom achievements";
        } else {
            customCell.textContent = '-';
        }
        
        // Last activity (now column 5)
        const lastActivity = teamData.lastSubmission ? 
            new Date(teamData.lastSubmission).toLocaleString() : 
            'No activity';
        row.insertCell(5).textContent = lastActivity;
        
        // Trend (now column 6)
        const trendCell = row.insertCell(6);
        if (teamData.submissions && teamData.submissions.length > 1) {
            const recent = teamData.submissions.slice(-2);
            const pointsGained = recent[1].points - recent[0].points;
            if (pointsGained > 0) {
                trendCell.innerHTML = `<span class="trend-up">↑ +${pointsGained}</span>`;
            } else if (pointsGained === 0) {
                trendCell.innerHTML = '<span class="trend-same">→</span>';
            }
        } else {
            trendCell.innerHTML = '<span class="trend-same">-</span>';
        }
    });
}

function updateActivityFeed() {
    const feed = document.getElementById('activityFeed');
    feed.innerHTML = '';
    
    const timeline = dashboardData.timeline || [];
    const recentEvents = timeline.slice(0, 10);
    
    if (recentEvents.length === 0) {
        feed.innerHTML = '<p class="no-activity">No activity yet</p>';
        return;
    }
    
    recentEvents.forEach(event => {
        const div = document.createElement('div');
        div.className = 'activity-item';
        // Add special class for custom achievements (UPDATED)
        if (event.type === 'custom') {
            div.classList.add('custom-achievement');
        }
        
        const time = new Date(event.timestamp).toLocaleTimeString();
        const points = event.points ? `(+${event.points} pts)` : '';
        
        div.innerHTML = `
            <span class="activity-time">${time}</span>
            <span class="activity-team">${event.team}</span>
            <span class="activity-event">${event.event} ${points}</span>
        `;
        
        feed.appendChild(div);
    });
}

function updateMilestoneGrid() {
    const grid = document.getElementById('milestoneGrid');
    grid.innerHTML = '';
    
    const milestones = dashboardData.milestoneStats || {};
    
    // Define expected milestones if none completed yet
    const allPossibleMilestones = {
        'bug_estate_supply': { name: 'Estate Supply Bug', points: 20 },
        'bug_controller_params': { name: 'Controller Parameters', points: 15 },
        'bug_prompt_formatting': { name: 'Prompt Formatting', points: 10 },
        'test_coverage_player': { name: 'Player Test Coverage', points: 15 },
        'test_coverage_supply': { name: 'Supply Test Coverage', points: 15 },
        'test_coverage_overall': { name: 'Overall Test Coverage', points: 25 },
        'card_laboratory': { name: 'Laboratory Card', points: 25 },
        'card_gardens': { name: 'Gardens Card', points: 30 },
        'card_witch': { name: 'Witch Card', points: 40 }
    };
    
    // Merge with actual data
    Object.entries(allPossibleMilestones).forEach(([id, defaultData]) => {
        const milestone = milestones[id] || { 
            ...defaultData, 
            completedBy: [] 
        };
        
        const div = document.createElement('div');
        div.className = 'milestone-item';
        if (milestone.completedBy.length > 0) {
            div.classList.add('completed');
        }
        
        div.innerHTML = `
            <h4>${milestone.name}</h4>
            <p class="milestone-points">${milestone.points || defaultData.points} points</p>
            <p class="milestone-teams">
                ${milestone.completedBy.length > 0 ? 
                    `Completed by: ${milestone.completedBy.join(', ')}` : 
                    'Not yet completed'}
            </p>
        `;
        
        grid.appendChild(div);
    });
}

// NEW FUNCTION: Update custom milestones section
function updateCustomMilestones() {
    const container = document.getElementById('customMilestonesContainer');
    if (!container) return; // Skip if element doesn't exist
    
    container.innerHTML = '';
    
    const customMilestones = dashboardData.customMilestones || {};
    const customArray = Object.values(customMilestones);
    
    if (customArray.length === 0) {
        container.innerHTML = '<p class="no-custom">No custom achievements yet. Be creative!</p>';
        return;
    }
    
    // Sort by timestamp (newest first)
    customArray.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Show recent custom achievements
    const recentCustom = customArray.slice(0, 10);
    
    recentCustom.forEach(custom => {
        const div = document.createElement('div');
        div.className = 'custom-milestone-item';
        
        const time = new Date(custom.timestamp).toLocaleDateString();
        
        div.innerHTML = `
            <div class="custom-header">
                <span class="custom-team">⭐ ${custom.team}</span>
                <span class="custom-date">${time}</span>
            </div>
            <h4>${custom.name}</h4>
            <p class="custom-description">${custom.description}</p>
        `;
        
        container.appendChild(div);
    });
}

function updateCharts(teams) {
    // Points over time chart
    const pointsCanvas = document.getElementById('pointsChart');
    const pointsContainer = pointsCanvas.parentElement;
    
    // Destroy existing chart if it exists
    if (chartInstances.points) {
        chartInstances.points.destroy();
        chartInstances.points = null;
    }
    
    // Reset canvas size to prevent growth
    pointsCanvas.style.height = '300px';
    pointsCanvas.style.width = '100%';
    
    const pointsCtx = pointsCanvas.getContext('2d');
    
    // Prepare data for points over time
    const datasets = teams.map(([teamName, teamData]) => {
        const submissions = teamData.submissions || [];
        const data = submissions.map((s, index) => ({
            x: index,
            y: s.points
        }));
        
        return {
            label: teamName,
            data: data,
            borderColor: getTeamColor(teamName),
            backgroundColor: getTeamColor(teamName) + '33',
            tension: 0.1
        };
    });
    
    chartInstances.points = new Chart(pointsCtx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2.5,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Submission Number'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Total Points'
                    },
                    beginAtZero: true
                }
            }
        }
    });
    
    // Milestone completion chart
    const completionCanvas = document.getElementById('completionChart');
    const completionContainer = completionCanvas.parentElement;
    
    // Destroy existing chart if it exists
    if (chartInstances.completion) {
        chartInstances.completion.destroy();
        chartInstances.completion = null;
    }
    
    // Reset canvas size to prevent growth
    completionCanvas.style.height = '300px';
    completionCanvas.style.width = '100%';
    
    const completionCtx = completionCanvas.getContext('2d');
    
    const teamNames = teams.map(([name]) => name);
    const completedCounts = teams.map(([_, data]) => data.completedMilestones.length);
    
    chartInstances.completion = new Chart(completionCtx, {
        type: 'bar',
        data: {
            labels: teamNames,
            datasets: [{
                label: 'Milestones Completed',
                data: completedCounts,
                backgroundColor: teamNames.map(name => getTeamColor(name))
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2.5,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function getTeamColor(teamName) {
    const colors = {
        'alpha': '#FF6B6B',
        'beta': '#4ECDC4',
        'gamma': '#45B7D1',
        'delta': '#96CEB4',
        'epsilon': '#FFEAA7',
        'zeta': '#DDA0DD',
        'eta': '#98D8C8',
        'theta': '#F7DC6F'
    };
    
    // Default color if team name not in predefined list
    return colors[teamName.toLowerCase()] || '#95A5A6';
}

// Auto-refresh every 30 seconds
let refreshInterval;

function startAutoRefresh() {
    refreshInterval = setInterval(loadDashboardData, 30000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Handle page visibility to save resources
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        loadDashboardData();
        startAutoRefresh();
    }
});

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    startAutoRefresh();
});