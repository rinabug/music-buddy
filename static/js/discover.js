// discover.js
document.addEventListener('DOMContentLoaded', function() {
    const concertForm = document.getElementById('concertForm');

    concertForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(concertForm);
        const url = concertForm.getAttribute('action');

        fetch(`${url}?${new URLSearchParams(formData)}`)
            .then(response => response.text())
            .then(data => {
                // Open a new window or tab with concert recommendations
                const newWindow = window.open('', '_blank');
                newWindow.document.write(data);
                newWindow.document.close();
            })
            .catch(error => {
                console.error('Error fetching concert recommendations:', error);
            });
    });
});
