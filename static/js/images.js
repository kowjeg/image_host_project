document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'F5' || event.key === 'Escape') {
            event.preventDefault();
            window.location.href = './upload';
        }
    });

    const uploadRedirectButton = document.getElementById('upload-tab-btn');
    if (uploadRedirectButton) {
        uploadRedirectButton.addEventListener('click', () => {
            window.location.href = './upload';
        });
    }

    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const filename = button.dataset.filename;
            const response = await fetch('/images/' + filename, { method: 'DELETE' });
            if (response.ok) {
                window.location.reload();
            } else {
                const result = await response.json();
                alert('Ошибка: ' + result.error);
            }
        });
    });
});
