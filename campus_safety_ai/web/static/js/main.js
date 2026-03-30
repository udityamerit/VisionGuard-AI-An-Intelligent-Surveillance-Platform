document.addEventListener('DOMContentLoaded', function() {
    console.log("AI Campus Safety System Dashboard Initialized");

    // Function to update summary statistics
    function updateStats() {
        if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    // Update AI Metrics
                    const peopleCountEl = document.getElementById('people-count-val');
                    if (peopleCountEl) peopleCountEl.innerText = data.people_count;

                    const campusStatusEl = document.getElementById('campus-status-val');
                    if (campusStatusEl) {
                        campusStatusEl.innerText = data.is_fighting === 'YES' ? '⚠️ VIOLENCE DETECTED' : (data.crowd_status === 'High' ? '🟠 OVERCROWDED' : '✅ NORMAL');
                        campusStatusEl.className = `stat-value h6 mt-2 fw-bold ${data.is_fighting === 'YES' || data.crowd_status === 'High' ? 'text-danger' : 'text-success'}`;
                    }

                    const cpuLoadEl = document.getElementById('cpu-load-val');
                    if (cpuLoadEl) cpuLoadEl.innerText = `${data.cpu}%`;

                    // GPU Load Simulation (still randomized for visual effect if no real GPU data)
                    const gpuLoad = Math.floor(Math.random() * 10) + 20; 
                    const gpuLoadText = document.getElementById('gpu-load');
                    const gpuBar = document.getElementById('gpu-bar');
                    if (gpuLoadText && gpuBar) {
                        gpuLoadText.innerText = `${gpuLoad}%`;
                        gpuBar.style.width = `${gpuLoad}%`;
                    }
                })
                .catch(err => console.error('Error fetching stats:', err));
        }
    }

    // Auto-refresh stats every 5 seconds
    setInterval(updateStats, 5000);
    updateStats();

    // Auto refresh the page every 30 seconds to update alert lists (simpler than Socket.io for now)
    if (window.location.pathname === '/alerts') {
        setTimeout(() => {
            window.location.reload();
        }, 30000);
    }
});
