document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/friends')
        .then(response => response.json())
        .then(data => {
            const friendsContent = document.getElementById('friendsContent');
            if (data.error) {
                friendsContent.innerHTML = `<p>${data.error}</p>`;
            } else if (data.length === 0) {
                friendsContent.innerHTML = '<p>You don\'t have any friends yet.</p>';
            } else {
                const friendList = document.createElement('ul');
                data.forEach(friend => {
                    const listItem = document.createElement('li');
                    listItem.textContent = friend;
                    friendList.appendChild(listItem);
                });
                friendsContent.appendChild(friendList);
            }
        })
        .catch(error => {
            console.error('Error fetching friends:', error);
            document.getElementById('friendsContent').innerHTML = '<p>Error loading friends. Please try again later.</p>';
        });
});

