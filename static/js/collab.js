document.addEventListener('DOMContentLoaded', function() {
    // Function to dynamically load chat messages
    function loadChatMessages() {
        fetch('/get_friend_messages')  // Endpoint to get friend messages
            .then(response => response.json())
            .then(messages => {
                const chatContent = document.getElementById('chatContent');
                chatContent.innerHTML = '';
                messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.textContent = `${msg.sender}: ${msg.message}`;
                    chatContent.appendChild(messageDiv);
                });
            })
            .catch(error => console.error('Error loading messages:', error));
    }

    // Load chat messages initially
    loadChatMessages();

    // Function to handle sending chat messages
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(chatForm);
            fetch('/send_friend_message', {  // Endpoint to send friend message
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
            .catch(error => console.error('Error sending message:', error));
        });
    }
});

