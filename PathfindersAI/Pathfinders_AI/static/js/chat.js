document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');

    let chatHistory = [];

    const initialSystemInstruction = {
        role: "user",
        parts: [{
            text: "You are StudyBuddy, an AI academic guidance assistant. Your purpose is to help students with questions about courses, career planning, and study tips. Provide helpful, encouraging, and accurate information. Do not answer questions outside of these academic and career guidance topics. If a user asks something irrelevant, gently steer them back to your purpose. When providing lists or emphasized text, do so in a natural, conversational tone without using markdown formatting like asterisks (*), underscores (_), or hash symbols (#). Present information as plain, readable text."
        }]
    };

    chatHistory.push(initialSystemInstruction);

    addMessage('Hello! I\'m StudyBuddy. How can I help you with your academic journey today?', 'bot-message');

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            chatHistory.push({ role: "user", parts: [{ text: message }] });
            addMessage(message, 'user-message');
            userInput.value = '';
            userInput.disabled = true;
            sendButton.disabled = true;

            const loadingMessageDiv = addMessage('StudyBuddy is thinking...', 'bot-message loading-message');
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const apiKey = "AIzaSyBEVn9RTZVFG4sOI6RN4G1RtotHieZKOM8"; // <<< API KEY HERE
                const payload = {
                    contents: chatHistory
                };

                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`API error: ${response.status} - ${errorData.error.message || response.statusText}`);
                }

                const result = await response.json();

                if (loadingMessageDiv && loadingMessageDiv.parentNode) {
                    loadingMessageDiv.parentNode.removeChild(loadingMessageDiv);
                }

                if (result.candidates && result.candidates.length > 0 &&
                    result.candidates[0].content && result.candidates[0].content.parts &&
                    result.candidates[0].content.parts.length > 0) {
                    const botResponseText = result.candidates[0].content.parts[0].text;
                    chatHistory.push({ role: "model", parts: [{ text: botResponseText }] });
                    addMessage(botResponseText, 'bot-message');
                } else {
                    addMessage("Sorry, I couldn't get a response from the AI. The response structure was unexpected.", 'bot-message error-message');
                    console.error("Unexpected API response structure:", result);
                }

            } catch (error) {
                if (loadingMessageDiv && loadingMessageDiv.parentNode) {
                    loadingMessageDiv.parentNode.removeChild(loadingMessageDiv);
                }
                console.error("Error fetching AI response:", error);
                addMessage(`Oops! Something went wrong while connecting to the AI: ${error.message}. Please check your API key or network and try again later.`, 'bot-message error-message');
            } finally {
                userInput.disabled = false;
                sendButton.disabled = false;
                userInput.focus();
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    }

    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        messageDiv.innerHTML = `
            <p>${text}</p>
            <div class="message-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return messageDiv;
    }
});
