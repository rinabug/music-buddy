document.addEventListener('DOMContentLoaded', () => {
    loadFriends();
    loadBadges();
});

function loadFriends() {
    fetch('/api/friends')
        .then(response => response.json())
        .then(data => {
            const friendsContent = document.getElementById('friendsContent');
            friendsContent.innerHTML = data.map(item => `<p>${item.name}</p>`).join('');
        })
        .catch(error => console.error('Error loading friends:', error));
}

function loadBadges() {
    fetch('/api/badges')
        .then(response => response.json())
        .then(data => {
            const badgesContent = document.getElementById('badgesContent');
            badgesContent.innerHTML = data.map(item => `<p>${item.name}</p>`).join('');
        })
        .catch(error => console.error('Error loading badges:', error));
}
