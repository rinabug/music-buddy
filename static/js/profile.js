document.addEventListener('DOMContentLoaded', () => {
    loadFriends();
    loadBadges();
    setupSendFriendRequestButton();
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

function setupSendFriendRequestButton() {
    const sendRequestBtn = document.getElementById('send-request-btn');
    sendRequestBtn.addEventListener('click', () => {
        const friendUsername = document.getElementById('friend-username').value;
        if (friendUsername) {
            sendFriendRequest(friendUsername);
        }
    });
}

function sendFriendRequest(friendUsername) {
    fetch('/send_friend_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ receiver_username: friendUsername }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
            } else {
                alert('Failed to send friend request. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error sending friend request:', error);
            alert('An error occurred while sending the friend request.');
        });
}
