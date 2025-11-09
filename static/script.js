document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Kullanıcı mesajını sohbet kutusuna ekler
    function appendUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `<p>${text}</p>`;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Bot mesajını sohbet kutusuna ekler
    function appendBotMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `<p>${text}</p>`;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Sorgu gönderme işlevi
    async function sendMessage() {
        const query = userInput.value.trim();
        if (query === "") return;

        // 1. Kullanıcı mesajını göster
        appendUserMessage(query);
        userInput.value = '';
        sendButton.disabled = true; // Gönder tuşunu devre dışı bırak
        appendBotMessage("🤖 Estü Bot düşünüyor..."); // Yükleme mesajı

        try {
            // 2. FastAPI API'sine sorguyu gönder
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            // 3. Cevabı al ve göster
            const data = await response.json();
            
            // Son yükleme mesajını kaldır
            const loadingMessage = chatBox.querySelector('.bot-message:last-child');
            if (loadingMessage && loadingMessage.textContent.includes('düşünüyor')) {
                loadingMessage.remove();
            }

            if (response.ok) {
                appendBotMessage(data.response);
            } else {
                appendBotMessage(`⚠️ Hata oluştu: ${data.detail || 'Bilinmeyen Hata'}`);
            }

        } catch (error) {
            console.error('API Hatası:', error);
            appendBotMessage("❌ Sunucuya bağlanırken bir sorun oluştu.");
        } finally {
            sendButton.disabled = false; // Gönder tuşunu tekrar etkinleştir
        }
    }

    // Olay Dinleyicileri
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});