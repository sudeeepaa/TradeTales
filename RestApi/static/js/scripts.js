// filepath: TradeTales/src/static/js/scripts.js
document.addEventListener("DOMContentLoaded", function() {
    // Handle review submission
    const reviewForms = document.querySelectorAll('.review-form');
    reviewForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(form);
            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Review submitted successfully!');
                    location.reload(); // Reload the page to show the new review
                } else {
                    alert('Error submitting review: ' + data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Handle search functionality
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const searchParams = new URLSearchParams(new FormData(searchForm)).toString();
            fetch(`/search?${searchParams}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById('search-results').innerHTML = html;
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // Handle delete book functionality
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const bookId = this.dataset.bookId;
            if (confirm('Are you sure you want to delete this book?')) {
                fetch(`/admin/delete-book/${bookId}`, {
                    method: 'POST'
                })
                .then(response => {
                    if (response.ok) {
                        alert('Book deleted successfully!');
                        location.reload(); // Reload the page to reflect changes
                    } else {
                        alert('Error deleting book.');
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });
});