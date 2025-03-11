class ChatInterface {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.processingIndicator = document.getElementById('processing');
        
        this.initializeEventListeners();
        this.setupQuickActions();
    }

    initializeEventListeners() {
        this.sendBtn.addEventListener('click', () => this.handleUserMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleUserMessage();
        });
        
        document.querySelector('.new-chat').addEventListener('click', () => {
            this.resetChat();
        });
    }

    setupQuickActions() {
        document.querySelectorAll('.quick-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                this.userInput.value = e.target.dataset.action;
                this.handleUserMessage();
            });
        });
    }

    async handleUserMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
    
        this.addMessage('user', message);
        this.userInput.value = '';
        this.showProcessing(true);
    
        try {
            const response = await this.sendToBackend(message);
            if (response.error) {
                throw new Error(response.error); // Handle backend errors
            }
            this.addMessage('bot', response.response);
            this.handleSystemPrompts(response);
        } catch (error) {
            console.error("Chat error:", error); // Log error in browser console
            this.addMessage('bot', `Error: ${error.message}`);
        } finally {
            this.showProcessing(false);
        }
    }
    

    async sendToBackend(message) {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error('Server response was not OK');
        }
        return response.json();
    }

    addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const iconClass = sender === 'bot' ? 'fa-robot' : 'fa-user';
        messageDiv.innerHTML = `
            <div class="message-content">
                <i class="fas ${iconClass} message-icon"></i>
                <div class="text">${text}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showProcessing(show) {
        this.processingIndicator.style.display = show ? 'flex' : 'none';
    }

    resetChat() {
        this.chatMessages.innerHTML = `
            <div class="message bot">
                <div class="message-content">
                    <i class="fas fa-robot message-icon"></i>
                    <div class="text">
                        Welcome to MedAI Assistant! How can I help you today?
                        <div class="quick-actions">
                            <button class="quick-btn" data-action="book">Book Appointment</button>
                            <button class="quick-btn" data-action="reschedule">Reschedule</button>
                            <button class="quick-btn" data-action="cancel">Cancel Appointment</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        this.setupQuickActions();
    }

    handleSystemPrompts(response) {
        if (response.actions) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'quick-actions';
            response.actions.forEach(action => {
                const button = document.createElement('button');
                button.className = 'quick-btn';
                button.textContent = action.label;
                button.dataset.action = action.value;
                button.addEventListener('click', () => {
                    this.userInput.value = action.value;
                    this.handleUserMessage();
                });
                actionsDiv.appendChild(button);
            });
            
            const lastMessage = this.chatMessages.lastElementChild;
            lastMessage.querySelector('.text').appendChild(actionsDiv);
        }
    }
}

// Initialize chat when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});