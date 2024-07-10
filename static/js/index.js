document.addEventListener('DOMContentLoaded', async function() {
    // Fetch leaderboard data
    try {
        const leaderboardResponse = await fetch('/api/leaderboard');
        const leaderboardData = await leaderboardResponse.json();
        if (leaderboardResponse.ok) {
            displayLeaderboard(leaderboardData);
        } else {
            throw new Error('Failed to fetch leaderboard data');
        }
    } catch (error) {
        console.error('Error fetching leaderboard data:', error);
    }

    // Fetch trivia data
    try {
        const triviaResponse = await fetch('/api/trivia');
        const triviaData = await triviaResponse.json();
        if (triviaResponse.ok) {
            displayTrivia(triviaData);
        } else {
            throw new Error('Failed to fetch trivia data');
        }
    } catch (error) {
        console.error('Error fetching trivia data:', error);
    }
});

function displayLeaderboard(leaderboardData) {
    const leaderboardContainer = document.getElementById('leaderboardContent');
    let html = '<ol>';
    leaderboardData.forEach(user => {
        html += `<li>${user.username} - ${user.points}</li>`;
    });
    html += '</ol>';
    leaderboardContainer.innerHTML = html;
}

function displayTrivia(triviaData) {
    const triviaContainer = document.getElementById('triviaContent');
    let html = '<ul>';
    triviaData.forEach(question => {
        html += `<li>${question.text}</li>`;
    });
    html += '</ul>';
    triviaContainer.innerHTML = html;
}