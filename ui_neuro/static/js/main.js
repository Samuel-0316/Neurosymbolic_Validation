let currentUser = '';
const messageHistory = [];
let accuracyScores = {
    total: 0,
    correct: 0
};

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const chatContainer = document.getElementById('chat-container');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const messagesDiv = document.getElementById('messages');
    const accuracyDisplay = document.getElementById('accuracy-score');
    const logsContainer = document.getElementById('logs');

    // Login Handler
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        try {
            const response = await fetch('http://localhost:5000/api/users/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username })
            });
            const data = await response.json();
            if (response.ok) {
                currentUser = username;
                document.getElementById('login-section').classList.add('hidden');
                chatContainer.classList.remove('hidden');
                updateLogs(`User ${username} logged in successfully`);
            }
        } catch (error) {
            console.error('Login error:', error);
            updateLogs(`Login error: ${error.message}`);
        }
    });

    // Message Handler
    messageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;

        try {
            const response = await fetch('http://localhost:5000/api/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user: currentUser,
                    message
                })
            });
            const data = await response.json();
            if (response.ok) {
                addMessage(data);
                messageInput.value = '';
                updateLogs(`Message sent: ${message}`);
                
                // Simulate LLM response and validation
                setTimeout(() => {
                    const llmResponse = simulateLLMResponse(message);
                    addMessage({
                        user: 'AI',
                        message: llmResponse,
                        timestamp: new Date().toISOString()
                    });
                    updateAccuracyScore(Math.random() > 0.3);
                }, 1000);
            }
        } catch (error) {
            console.error('Message error:', error);
            updateLogs(`Error sending message: ${error.message}`);
        }
    });

    // Helper Functions
    function addMessage(messageData) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message fade-in p-4 mb-4 rounded-lg ${
            messageData.user === currentUser ? 'bg-blue-100 ml-12' : 'bg-gray-100 mr-12'
        }`;
        messageDiv.innerHTML = `
            <div class="flex items-center mb-2">
                <span class="font-bold ${messageData.user === 'AI' ? 'text-purple-600' : 'text-blue-600'}">${messageData.user}</span>
                <span class="text-xs text-gray-500 ml-2">${new Date(messageData.timestamp).toLocaleTimeString()}</span>
            </div>
            <p class="text-gray-800">${messageData.message}</p>
        `;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        messageHistory.push(messageData);
    }

    function updateAccuracyScore(correct) {
        accuracyScores.total++;
        if (correct) accuracyScores.correct++;
        const score = (accuracyScores.correct / accuracyScores.total) * 100;
        accuracyDisplay.textContent = `${score.toFixed(1)}%`;
        document.getElementById('accuracy-bar').style.width = `${score}%`;
    }

    function updateLogs(message) {
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry fade-in text-sm text-gray-600 mb-2';
        logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logsContainer.appendChild(logEntry);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    function simulateLLMResponse(message) {
        const responses = [
            "That's an interesting point! Let me think about it...",
            "Based on my analysis, I would suggest...",
            "I understand your question. Here's what I think...",
            "Let me provide a detailed explanation...",
            "According to my training data..."
        ];
        return responses[Math.floor(Math.random() * responses.length)] + 
               " [Simulated AI response to: " + message + "]";
    }

    // Initial load of messages
    fetch('http://localhost:5000/api/messages')
        .then(response => response.json())
        .then(messages => {
            messages.forEach(addMessage);
            updateLogs('Loaded message history');
        })
        .catch(error => {
            console.error('Error loading messages:', error);
            updateLogs('Error loading message history');
        });
});
