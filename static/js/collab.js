document.addEventListener('DOMContentLoaded', () => {
    loadPlaylists();
    loadChat();
});

function loadPlaylists() {
    fetch('/api/playlists')
        .then(response => response.json())
        .then(data => {
            const playlistContent = document.getElementById('playlistContent');
            playlistContent.innerHTML = data.map(item => `<p>${item.name}: ${item.songs.join(', ')}</p>`).join('');
        })
        .catch(error => console.error('Error loading playlists:', error));
}

function loadChat() {
    fetch('/api/chat')
        .then(response => response.json())
        .then(data => {
            const chatContent = document.getElementById('chatContent');
            chatContent.innerHTML = data.map(item => `<p>${item.user}: ${item.message}</p>`).join('');
        })
        .catch(error => console.error('Error loading chat:', error));
}
