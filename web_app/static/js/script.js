// static/js/script.js

// --- Global State (for chat page) ---
let currentSessionId = null;

// --- Helper Functions ---
function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// --- Home Page Logic ---
async function loadAgents() {
    const agentListDiv = document.getElementById('agent-list');
    if (!agentListDiv) return;

    try {
        const response = await fetch('/list-apps');
        const agents = await response.json();
        
        agentListDiv.innerHTML = ''; // Clear loader

        agents.forEach(agent => {
            const card = document.createElement('a');
            card.href = `/chat/${agent}`;
            card.className = 'agent-card';
            
            // Get agent info from the global AGENT_INFO if available
            const agentInfo = typeof AGENT_INFO !== 'undefined' && AGENT_INFO[agent] ? AGENT_INFO[agent] : {};
            
            // Use custom image if provided, otherwise fall back to agent name or placeholder
            const imgPath = agentInfo.image 
                ? `/static/images/${agentInfo.image}` 
                : `/static/images/${agent}.png`;
            
            // Use custom description if provided, otherwise use default
            const description = agentInfo.description 
                ? agentInfo.description 
                : "Chat with this helpful agent about various topics.";
            
            card.innerHTML = `
                <img src="${imgPath}" alt="${agent}" onerror="this.src='/static/images/placeholder.png'">
                <h3>${agent.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
                <p>${description}</p>
            `;
            agentListDiv.appendChild(card);
        });
    } catch (error) {
        console.error('Failed to load agents:', error);
        agentListDiv.innerHTML = '<p>Error loading agents. Please try again later.</p>';
    }
}


// --- Chat Page Logic ---

function initChatPage() {
    document.getElementById('new-chat-btn').addEventListener('click', startNewChat);
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    document.getElementById('message-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    loadSessions();
}

async function loadSessions() {
    const sessionListDiv = document.getElementById('session-list');
    sessionListDiv.innerHTML = '<div class="loader"></div>';
    
    try {
        const response = await fetch(`/apps/${AGENT_NAME}/users/${USER_ID}/sessions`);
        const sessions = await response.json();
        
        sessionListDiv.innerHTML = '';
        if (sessions.length === 0) {
            sessionListDiv.innerHTML = '<p>No past sessions found.</p>';
        } else {
            sessions.forEach(session => {
                const sessionEl = document.createElement('div');
                sessionEl.className = 'session-list-item';
                sessionEl.dataset.sessionId = session.id;
                
                const date = new Date(session.lastUpdateTime * 1000).toLocaleString();

                sessionEl.innerHTML = `
                    <div class="session-preview">Session from:</div>
                    <div class="session-date">${date}</div>
                `;
                sessionEl.addEventListener('click', () => loadChatHistory(session.id));
                sessionListDiv.appendChild(sessionEl);
            });
        }
    } catch (error) {
        console.error('Failed to load sessions:', error);
        sessionListDiv.innerHTML = '<p>Error loading sessions.</p>';
    }
}

function startNewChat() {
    currentSessionId = uuidv4();
    document.getElementById('chat-window').innerHTML = ''; // Clear window
    document.getElementById('chat-input-area').style.display = 'flex';
    document.getElementById('message-input').focus();
    updateActiveSessionUI(null); // No session is active yet until first message
    console.log(`Started new chat with session ID: ${currentSessionId}`);
}

async function loadChatHistory(sessionId) {
    currentSessionId = sessionId;
    const chatWindow = document.getElementById('chat-window');
    chatWindow.innerHTML = '<div class="loader"></div>';
    document.getElementById('chat-input-area').style.display = 'flex';

    updateActiveSessionUI(sessionId);
    
    try {
        const response = await fetch(`/apps/${AGENT_NAME}/users/${USER_ID}/sessions/${sessionId}`);
        const sessionData = await response.json();
        
        chatWindow.innerHTML = '';
        if (sessionData.events && sessionData.events.length > 0) {
            sessionData.events.forEach(event => {
                appendMessage(event.content.parts[0].text, event.content.role, event.author);
            });
        }
    } catch (error) {
        console.error('Failed to load chat history:', error);
        chatWindow.innerHTML = '<p>Error loading chat history.</p>';
    }
}

async function sendMessage() {
    const input = document.getElementById('message-input');
    const messageText = input.value.trim();
    if (!messageText) return;
    if (!currentSessionId) {
        alert("Please start a new chat or select a previous session first.");
        return;
    }

    // Display user message immediately
    appendMessage(messageText, 'user');
    input.value = '';

    const payload = {
        app_name: AGENT_NAME,
        session_id: currentSessionId,
        new_message: {
            role: 'user',
            parts: [{ text: messageText }]
        },
        streaming: false
    };

    try {
        const response = await fetch('/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const responseEvents = await response.json();
        responseEvents.forEach(event => {
            if (event.content && event.content.parts && event.content.parts[0].text) {
                 appendMessage(event.content.parts[0].text, event.content.role, event.author);
            }
        });
        
        // If this was the first message of a new chat, reload session list
        if (document.querySelector(`.session-list-item[data-session-id="${currentSessionId}"]`) === null) {
            loadSessions();
        }

    } catch (error) {
        console.error('Error sending message:', error);
        appendMessage("Sorry, there was an error communicating with the agent.", "model", "System");
    }
}

function appendMessage(text, role, author = 'user') {
    const chatWindow = document.getElementById('chat-window');
    const messageDiv = document.createElement('div');
    
    messageDiv.classList.add('chat-message');
    messageDiv.classList.add(role === 'user' ? 'user-message' : 'model-message');
    
    // Sanitize text to prevent HTML injection
    const textNode = document.createTextNode(text);
    
    if (role === 'model') {
        const authorSpan = document.createElement('div');
        authorSpan.className = 'author';
        authorSpan.textContent = author.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        messageDiv.appendChild(authorSpan);
    }
    
    messageDiv.appendChild(textNode);
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll
}

function updateActiveSessionUI(sessionId) {
    document.querySelectorAll('.session-list-item').forEach(el => {
        el.classList.remove('active');
        if (el.dataset.sessionId === sessionId) {
            el.classList.add('active');
        }
    });
}