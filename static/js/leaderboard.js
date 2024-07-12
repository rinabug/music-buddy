document.addEventListener('DOMContentLoaded', () => {
    function loadLeaderboard() {
        fetch('/get_leaderboard')
            .then(response => response.json())
            .then(data => {
                const leaderboardContent = document.getElementById('leaderboardContent');
                leaderboardContent.innerHTML = `
                    <ol>
                        ${data.map(item => `<li>${item.username}: ${item.score} points</li>`).join('')}
                    </ol>
                `;
            })
            .catch(error => console.error('Error loading leaderboard:', error));
    }

    loadLeaderboard();
    setInterval(loadLeaderboard, 60000); // Refresh every minute
});