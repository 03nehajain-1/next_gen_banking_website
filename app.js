// Voice Bot Integration with LangGraph Banking Assistant
// This connects the frontend to the Python backend

let isRecording = false;
let isAuthenticated = false;
let currentUser = null;
let voiceBotVisible = false;

// API Configuration - Update this to match your backend endpoint
const API_BASE_URL = 'http://localhost:8000'; // Change to your Flask/FastAPI backend URL

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Next Gen Indian Banking Website Loaded');
    // Check if user is already logged in (from session storage)
    checkAuthStatus();
});

// Voice Bot Functions
function toggleVoiceBot() {
    const voiceBot = document.getElementById('voiceBot');
    voiceBotVisible = !voiceBotVisible;
    
    if (voiceBotVisible) {
        voiceBot.classList.remove('hidden');
        // If user is authenticated, greet them
        if (isAuthenticated && currentUser) {
            addBotMessage(`Hello ${currentUser.name}! How can I help you with your banking today?`);
        }
    } else {
        voiceBot.classList.add('hidden');
    }
}

function minimizeBot() {
    const voiceBot = document.getElementById('voiceBot');
    voiceBot.classList.toggle('minimized');
}

// Voice Recording Functions
async function toggleVoiceRecording() {
    const voiceBtn = document.getElementById('voiceBtn');
    const voiceIndicator = document.getElementById('voiceIndicator');
    const botStatus = document.getElementById('botStatus');
    
    if (!isRecording) {
        // Start recording
        isRecording = true;
        voiceBtn.classList.add('recording');
        voiceIndicator.classList.add('active');
        botStatus.textContent = 'Listening...';
        
        try {
            // Use Web Speech API for voice recognition
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                recognition.onstart = function() {
                    console.log('Voice recognition started');
                };
                
                recognition.onresult = async function(event) {
                    const transcript = event.results[0][0].transcript;
                    console.log('Transcript:', transcript);
                    
                    // Add user message to chat
                    addUserMessage(transcript);
                    
                    // Send to backend
                    await processVoiceQuery(transcript);
                };
                
                recognition.onerror = function(event) {
                    console.error('Speech recognition error:', event.error);
                    botStatus.textContent = 'Error: ' + event.error;
                    addBotMessage('Sorry, I couldn\'t understand that. Please try again.');
                };
                
                recognition.onend = function() {
                    isRecording = false;
                    voiceBtn.classList.remove('recording');
                    voiceIndicator.classList.remove('active');
                    botStatus.textContent = 'Ready to help';
                };
                
                recognition.start();
            } else {
                alert('Voice recognition is not supported in your browser. Please use Chrome or Edge.');
                isRecording = false;
                voiceBtn.classList.remove('recording');
                voiceIndicator.classList.remove('active');
                botStatus.textContent = 'Voice not supported';
            }
        } catch (error) {
            console.error('Error starting voice recognition:', error);
            isRecording = false;
            voiceBtn.classList.remove('recording');
            voiceIndicator.classList.remove('active');
            botStatus.textContent = 'Error';
        }
    } else {
        // Stop recording (handled by recognition.onend)
        isRecording = false;
    }
}

// Process voice query through backend
async function processVoiceQuery(query) {
    const botStatus = document.getElementById('botStatus');
    botStatus.textContent = 'Processing...';
    
    try {
        // Get current language
        const currentLang = typeof getCurrentLanguage === 'function' ? getCurrentLanguage() : 'en';
        
        // Call backend API
        const response = await fetch(`${API_BASE_URL}/api/voice-banking`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_input: query,
                user_id: isAuthenticated ? currentUser.user_id : null,
                thread_id: `session_${Date.now()}`,
                language: currentLang
            })
        });
        
        if (!response.ok) {
            throw new Error('Backend API error');
        }
        
        const result = await response.json();
        
        // Add bot response to chat
        if (result.response) {
            addBotMessage(result.response);
            
            // Update UI if balance or transaction data is returned
            if (result.account_balance) {
                updateAccountBalance(result.account_balance);
            }
            
            if (result.transaction_history) {
                updateTransactionHistory(result.transaction_history);
            }
            
            // Text-to-speech for response (use appropriate language)
            speakText(result.response, currentLang);
        }
        
        botStatus.textContent = 'Ready to help';
        
    } catch (error) {
        console.error('Error processing voice query:', error);
        
        // Fallback to mock response if backend is not available
        const mockResponse = getMockResponse(query);
        addBotMessage(mockResponse);
        speakText(mockResponse);
        
        botStatus.textContent = 'Ready to help';
    }
}

// Mock response generator (fallback when backend is unavailable)
function getMockResponse(query) {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('balance')) {
        updateAccountBalance(15750.50);
        return "Your current account balance is ₹15,750.50. Is there anything else I can help you with?";
    }
    
    if (lowerQuery.includes('transaction') || lowerQuery.includes('history')) {
        return "Here are your recent transactions: You spent ₹150 at a grocery store on Nov 20, received salary deposit of ₹3,000 on Nov 18, and spent ₹85.25 at a restaurant on Nov 15.";
    }
    
    if (lowerQuery.includes('transfer')) {
        return "To transfer funds, I'll need the recipient's account details and the amount. Please tell me the account number and amount you'd like to transfer.";
    }
    
    if (lowerQuery.includes('loan')) {
        return "Your current home loan balance is ₹1,20,000 at 3.5% interest rate. Your next EMI of ₹8,500 is due on December 5th.";
    }
    
    if (lowerQuery.includes('credit')) {
        return "Your credit card limit is ₹50,000 with ₹42,350 available credit. Would you like to know about recent transactions or payment due dates?";
    }
    
    return "I'm here to help you with balance inquiries, transactions, transfers, loans, and credit cards. What would you like to know?";
}

// Text-to-Speech function with multilingual support (Male Voice)
function speakText(text, lang = 'en') {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 0.9; // Slightly lower pitch for more masculine voice
        utterance.volume = 1.0;
        
        // Set language based on selected language
        switch(lang) {
            case 'hi':
                utterance.lang = 'hi-IN'; // Hindi (India)
                break;
            case 'gu':
                utterance.lang = 'gu-IN'; // Gujarati (India)
                break;
            default:
                utterance.lang = 'en-US'; // English (US)
        }
        
        // Get available voices and select a male voice
        const voices = window.speechSynthesis.getVoices();
        
        if (voices.length > 0) {
            // Try to find a male voice for the selected language
            let maleVoice = null;
            
            if (lang === 'hi') {
                // Find Hindi male voice
                maleVoice = voices.find(voice => 
                    voice.lang.includes('hi') && 
                    (voice.name.toLowerCase().includes('male') || 
                     voice.name.toLowerCase().includes('man') ||
                     voice.name.toLowerCase().includes('ravi') ||
                     voice.name.toLowerCase().includes('hemant'))
                );
                // Fallback to any Hindi voice
                if (!maleVoice) {
                    maleVoice = voices.find(voice => voice.lang.includes('hi'));
                }
            } else if (lang === 'gu') {
                // Find Gujarati male voice
                maleVoice = voices.find(voice => 
                    voice.lang.includes('gu') && 
                    (voice.name.toLowerCase().includes('male') || 
                     voice.name.toLowerCase().includes('man'))
                );
                // Fallback to any Gujarati voice
                if (!maleVoice) {
                    maleVoice = voices.find(voice => voice.lang.includes('gu'));
                }
            } else {
                // Find English male voice
                maleVoice = voices.find(voice => 
                    voice.lang.includes('en') && 
                    (voice.name.toLowerCase().includes('male') || 
                     voice.name.toLowerCase().includes('david') ||
                     voice.name.toLowerCase().includes('james') ||
                     voice.name.toLowerCase().includes('george') ||
                     voice.name.toLowerCase().includes('daniel'))
                );
                // Fallback to any English voice with male characteristics
                if (!maleVoice) {
                    maleVoice = voices.find(voice => 
                        voice.lang.includes('en-US') || voice.lang.includes('en-GB')
                    );
                }
            }
            
            if (maleVoice) {
                utterance.voice = maleVoice;
                console.log('🎙️ Using voice:', maleVoice.name);
            }
        }
        
        window.speechSynthesis.speak(utterance);
    }
}

// Load voices when they are ready (needed for some browsers)
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = function() {
        const voices = window.speechSynthesis.getVoices();
        console.log('🎙️ Available voices loaded:', voices.length);
        // Log male voices for debugging
        voices.filter(v => 
            v.name.toLowerCase().includes('male') || 
            v.name.toLowerCase().includes('david') ||
            v.name.toLowerCase().includes('james')
        ).forEach(v => console.log('Male voice:', v.name, v.lang));
    };
}

// Text input handling
function handleTextInput(event) {
    if (event.key === 'Enter') {
        sendTextMessage();
    }
}

async function sendTextMessage() {
    const input = document.getElementById('textInput');
    const message = input.value.trim();
    
    if (message) {
        addUserMessage(message);
        input.value = '';
        await processVoiceQuery(message);
    }
}

// Quick action from dashboard
function askVoiceBot(query) {
    // Show voice bot if hidden
    if (!voiceBotVisible) {
        toggleVoiceBot();
    }
    
    // Add query and process
    addUserMessage(query);
    processVoiceQuery(query);
}

// Chat UI Functions
function addUserMessage(message) {
    const chatContent = document.getElementById('chatContent');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'user-message';
    messageDiv.innerHTML = `
        <div class="message-bubble">
            <p>${message}</p>
        </div>
    `;
    chatContent.appendChild(messageDiv);
    chatContent.scrollTop = chatContent.scrollHeight;
}

function addBotMessage(message) {
    const chatContent = document.getElementById('chatContent');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'bot-message';
    messageDiv.innerHTML = `
        <i class="fas fa-robot"></i>
        <div class="message-bubble">
            <p>${message}</p>
        </div>
    `;
    chatContent.appendChild(messageDiv);
    chatContent.scrollTop = chatContent.scrollHeight;
}

// Clear chat history
function clearChat() {
    const chatContent = document.getElementById('chatContent');
    if (chatContent) {
        chatContent.innerHTML = '';
    }
}

// Login/Logout Functions
function showLogin() {
    document.getElementById('loginModal').classList.remove('hidden');
}

function closeLogin() {
    document.getElementById('loginModal').classList.add('hidden');
}

async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Mock authentication - in production, call backend API
    if (username && password) {
        // Simulate successful login
        currentUser = {
            id: 'user_001',
            name: 'John Doe',
            account_number: 'ACC123456789',
            balance: 15750.50
        };
        
        isAuthenticated = true;
        
        // Save to session storage
        sessionStorage.setItem('isAuthenticated', 'true');
        sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        // Update UI
        document.getElementById('userName').textContent = currentUser.name;
        document.getElementById('accountBalance').textContent = `₹${currentUser.balance.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
        
        // Hide login modal and show dashboard
        closeLogin();
        document.querySelector('.hero').style.display = 'none';
        document.querySelector('.services').style.display = 'none';
        document.getElementById('dashboard').classList.remove('hidden');
        
        // Show welcome message in voice bot if open
        if (voiceBotVisible) {
            addBotMessage(`Welcome back, ${currentUser.name}! Your account balance is ₹${currentUser.balance.toLocaleString('en-IN')}. How can I assist you today?`);
        }
    }
}

function startVoiceAuth() {
    closeLogin();
    toggleVoiceBot();
    addBotMessage("Please say your name for voice authentication.");
    
    setTimeout(() => {
        toggleVoiceRecording();
    }, 500);
}

function logout() {
    isAuthenticated = false;
    currentUser = null;
    
    sessionStorage.removeItem('isAuthenticated');
    sessionStorage.removeItem('currentUser');
    
    document.getElementById('dashboard').classList.add('hidden');
    document.querySelector('.hero').style.display = 'block';
    document.querySelector('.services').style.display = 'block';
    
    if (voiceBotVisible) {
        toggleVoiceBot();
    }
    
    alert('You have been logged out successfully.');
}

function showDashboard() {
    if (!currentUser) return;
    
    // Update dashboard with user data
    document.getElementById('userName').textContent = currentUser.name;
    document.getElementById('accountBalance').textContent = `₹${currentUser.balance.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    
    // Update account number display
    const accountNumberElement = document.querySelector('.account-number');
    if (accountNumberElement && currentUser.account_number) {
        const lastFour = currentUser.account_number.slice(-4);
        accountNumberElement.textContent = `A/C: ****${lastFour}`;
    }
    
    // Hide hero and services sections
    document.querySelector('.hero').style.display = 'none';
    document.querySelector('.services').style.display = 'none';
    
    // Show dashboard
    document.getElementById('dashboard').classList.remove('hidden');
    
    // Load user transactions if available
    loadUserTransactions(currentUser.user_id);
}

function checkAuthStatus() {
    const authStatus = sessionStorage.getItem('isAuthenticated');
    const userData = sessionStorage.getItem('currentUser');
    
    if (authStatus === 'true' && userData) {
        isAuthenticated = true;
        currentUser = JSON.parse(userData);
        showDashboard();
    }
}

async function loadUserTransactions(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/transactions/${userId}`);
        const data = await response.json();
        
        if (data.success && data.transactions) {
            updateTransactionHistory(data.transactions.slice(0, 5)); // Show last 5 transactions
        }
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

// Update UI Functions
function updateAccountBalance(balance) {
    const balanceElement = document.getElementById('accountBalance');
    if (balanceElement) {
        balanceElement.textContent = `₹${balance.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    }
    
    if (currentUser) {
        currentUser.balance = balance;
        sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
    }
}

function updateTransactionHistory(transactions) {
    const transactionsList = document.getElementById('transactionsList');
    if (!transactionsList || !transactions || transactions.length === 0) return;
    
    transactionsList.innerHTML = '';
    
    transactions.forEach(txn => {
        const txnDiv = document.createElement('div');
        txnDiv.className = 'transaction-item';
        txnDiv.innerHTML = `
            <div class="transaction-icon ${txn.type}">
                <i class="fas fa-${txn.type === 'debit' ? 'shopping-cart' : 'arrow-down'}"></i>
            </div>
            <div class="transaction-details">
                <p class="transaction-desc">${txn.description}</p>
                <p class="transaction-date">${txn.date}</p>
            </div>
            <div class="transaction-amount ${txn.type}">
                ${txn.type === 'debit' ? '-' : '+'}₹${txn.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}
            </div>
        `;
        transactionsList.appendChild(txnDiv);
    });
}

// Login Modal Functions
function showLogin() {
    const modal = document.getElementById('loginModal');
    modal.classList.remove('hidden');
}

function closeLogin() {
    const modal = document.getElementById('loginModal');
    modal.classList.add('hidden');
    document.getElementById('loginForm').reset();
}

async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value.trim().toLowerCase();
    const password = document.getElementById('password').value;
    
    // Mock user database (in production, this would be handled by backend)
    const users = {
        'neha': {
            password: 'neha123',
            user_id: 'neha',
            name: 'Neha Sharma',
            account_number: 'NGB001234567890',
            balance: 125000.00,
            phone: '+91-9876543210',
            email: 'neha.sharma@email.com'
        },
        'niyati': {
            password: 'niyati123',
            user_id: 'niyati',
            name: 'Niyati Patel',
            account_number: 'NGB009876543210',
            balance: 87500.00,
            phone: '+91-9123456789',
            email: 'niyati.patel@email.com'
        }
    };
    
    // Validate credentials
    if (users[username] && users[username].password === password) {
        // Login successful
        const user = users[username];
        delete user.password; // Remove password from stored data
        
        currentUser = user;
        isAuthenticated = true;
        
        // Save to session storage
        sessionStorage.setItem('isAuthenticated', 'true');
        sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        // Clear chat history for new session
        clearChat();
        
        // Close modal
        closeLogin();
        
        // Show success message
        alert(`Welcome back, ${user.name}! 👋`);
        
        // Update dashboard
        showDashboard();
        
        // Greet user in voice bot if it's open
        if (voiceBotVisible) {
            addBotMessage(`Hello ${user.name}! I'm your AI banking assistant. How can I help you today?`);
        }
    } else {
        // Login failed
        alert('Invalid username or password. Please try again.\n\nDemo users:\n- Username: neha, Password: neha123\n- Username: niyati, Password: niyati123');
    }
}

// Logout Function
function logout() {
    isAuthenticated = false;
    currentUser = null;
    sessionStorage.removeItem('isAuthenticated');
    sessionStorage.removeItem('currentUser');
    
    // Clear chat history
    clearChat();
    
    // Hide dashboard, show hero
    document.getElementById('dashboard').classList.add('hidden');
    document.querySelector('.hero').style.display = 'block';
    document.querySelector('.services').style.display = 'block';
    
    // Close voice bot if open
    if (voiceBotVisible) {
        toggleVoiceBot();
    }
    
    alert('You have been logged out successfully.');
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('loginModal');
    if (event.target === modal) {
        closeLogin();
    }
}
