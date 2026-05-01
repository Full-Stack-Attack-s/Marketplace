// ============================================
// FRIENDS.JS — управление списком друзей
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    window.removeFriend = function(friendId) {
        if (!confirm('Вы уверены, что хотите удалить этого пользователя из друзей?')) return;
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

        fetch(`/friends/toggle/${friendId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'removed') {
                const card = document.getElementById(`friend-${friendId}`);
                if (card) card.remove();
                
                // Если друзей не осталось, перезагружаем для показа empty-state
                if (document.querySelectorAll('.friend-card').length === 0) {
                    location.reload();
                }
            }
        })
        .catch(err => console.error('Ошибка удаления друга:', err));
    };
});
