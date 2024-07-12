document.addEventListener('DOMContentLoaded', function() {
    const concertForm = document.getElementById('concertForm');

    concertForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(concertForm);
        const url = concertForm.getAttribute('action');

        fetch(`${url}?${new URLSearchParams(formData)}`)
            .then(response => response.text())
            .then(data => {
                // Instead of opening a new window, set the HTML content to the session and redirect to the new page
                fetch('/chat_recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ data: data })
                }).then(() => {
                    window.location.href = '/chat_recommendations';
                });
            })
            .catch(error => {
                console.error('Error fetching concert recommendations:', error);
            });
    });
});
