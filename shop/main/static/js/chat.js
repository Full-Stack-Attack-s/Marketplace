// ============================================
// CHAT.JS — логика чата (детализация)
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const msgContent = document.getElementById('msgContent');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';
    
    // Получаем ID из data-атрибутов (будут добавлены в шаблон)
    const chatConfig = document.getElementById('chat-config');
    const currentUserId = chatConfig ? chatConfig.dataset.currentUserId : null;
    const otherUserId = chatConfig ? chatConfig.dataset.otherUserId : null;
    const chatUrl = chatConfig ? chatConfig.dataset.chatUrl : '';
    const newMessagesUrl = chatConfig ? chatConfig.dataset.newMessagesUrl : '';
    
    function scrollToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    scrollToBottom();
    
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const content = msgContent.value.trim();
            if (!content || !chatUrl) return;
            
            const formData = new FormData();
            formData.append('content', content);
            
            fetch(chatUrl, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    appendMessage(data);
                    msgContent.value = '';
                    scrollToBottom();
                }
            })
            .catch(err => console.error('Ошибка отправки сообщения:', err));
        });
    }
    
    function appendMessage(msg) {
        if (!chatMessages || document.querySelector(`.message[data-id="${msg.id}"]`)) return;
        
        const div = document.createElement('div');
        div.className = `message ${msg.sender_id == currentUserId ? 'msg-mine' : 'msg-theirs'}`;
        div.dataset.id = msg.id;
        
        div.innerHTML = `
            <div>${escapeHtml(msg.content)}</div>
            <div class="msg-time">${msg.created_at}</div>
        `;
        
        chatMessages.appendChild(div);
        scrollToBottom();
    }
    
    function fetchNewMessages() {
        if (!chatMessages || !newMessagesUrl) return;
        
        const messages = document.querySelectorAll('.message');
        let lastMsgId = 0;
        if (messages.length > 0) {
            lastMsgId = messages[messages.length - 1].dataset.id;
        }
        
        fetch(`${newMessagesUrl}?last_message_id=${lastMsgId}`)
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                let needsScroll = (chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages.scrollHeight - 50);
                
                data.messages.forEach(msg => appendMessage(msg));
                
                if (needsScroll) {
                    scrollToBottom();
                }
            }
        })
        .catch(err => console.error('Ошибка получения сообщений:', err));
    }
    
    if (newMessagesUrl) {
        setInterval(fetchNewMessages, 3000);
    }
    
    // Вспомогательная функция для безопасности
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});

// Функция добавления в друзья (глобальная)
window.toggleFriend = function(userId, btn) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';
    
    fetch(`/friends/toggle/${userId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'added') {
            btn.textContent = '✓ В друзьях';
            btn.style.background = 'var(--nav-active, #007bff)';
            btn.style.color = 'white';
        } else if (data.status === 'removed') {
            btn.textContent = 'Добавить в друзья';
            btn.style.background = 'none';
            btn.style.color = 'var(--nav-active, #007bff)';
        } else {
            alert(data.message || 'Ошибка');
        }
    })
    .catch(err => console.error('Ошибка добавления в друзья:', err));
};
