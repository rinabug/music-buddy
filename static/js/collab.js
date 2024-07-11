document.addEventListener('DOMContentLoaded', function() {
    // Example: Function to dynamically load chat messages
    function loadChatMessages() {
        fetch('/get_chat_messages')  // Assuming you have an endpoint to get chat messages
            .then(response => response.json())
            .then(messages => {
                const chatContent = document.getElementById('chatContent');
                chatContent.innerHTML = '';
                messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.textContent = `${msg.user}: ${msg.text}`;
                    chatContent.appendChild(messageDiv);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    // Load chat messages initially
    loadChatMessages();

    // Example: Function to handle sending chat messages
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(chatForm);
            fetch('/send_chat_message', {  // Assuming you have an endpoint to send chat messages
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    loadChatMessages();  // Reload chat messages after sending a new one
                    chatForm.reset();    // Clear the chat input
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Example: Function to dynamically update playlists (if applicable)
    function loadPlaylists() {
        fetch('/get_playlists')  // Assuming you have an endpoint to get updated playlists
            .then(response => response.json())
            .then(playlists => {
                const playlistContent = document.getElementById('playlistContent');
                playlistContent.innerHTML = '';
                playlists.forEach(playlist => {
                    const playlistItem = document.createElement('div');
                    playlistItem.className = 'playlist-item';
                    playlistItem.innerHTML = `
                        <img src="${playlist.image_url}" alt="Playlist Image">
                        <a href="${playlist.spotify_url}" target="_blank">${playlist.name}</a>
                    `;
                    playlistContent.appendChild(playlistItem);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    // Load playlists initially
    loadPlaylists();
});
