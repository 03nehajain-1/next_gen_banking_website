# Next Gen Indian Banking Website with Voice Assistant Integration

This project integrates a LangGraph-powered AI voice assistant into a Next Gen banking website.

## 🏗️ Project Structure

```
next_gen_banking_website/
├── index.html              # Main website HTML
├── styles.css              # Website styling
├── app.js                  # Frontend JavaScript (voice bot integration)
├── backend_server.py       # Flask backend server
├── banking_assistant_backend.py  # LangGraph assistant integration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## ✨ Features

### Frontend Features
- **Modern Banking Interface**: Clean, professional SBI-themed design
- **Voice Assistant Widget**: Floating chat widget with voice recording
- **Dashboard**: Account summary, balance, transactions, quick actions
- **Authentication**: Login modal with voice authentication option
- **Real-time Voice Recognition**: Uses Web Speech API
- **Text-to-Speech**: AI responses are spoken back to users
- **Responsive Design**: Works on desktop and mobile devices

### Backend Features
- **LangGraph Integration**: Connects to the multi-agent banking assistant
- **RESTful API**: Clean API endpoints for voice queries
- **Session Management**: Maintains conversation context
- **Security**: Authentication and compliance checks
- **Mock Mode**: Works standalone without LangGraph for testing

## 🚀 Setup Instructions

### 1. Install Python Dependencies

```bash
cd sbi_banking_website
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file with your Azure OpenAI credentials:

```env
AZURE_ENDPOINT=your_azure_endpoint
PRIVATE_KEY_PATH=path_to_your_key.pem
CONSUMER_ID=your_consumer_id
API_VERSION=2024-02-15-preview
WM_SVC_ENV=prod
LLM_MODEL=gpt-4
```

### 3. Start the Backend Server

```bash
python backend_server.py
```

The server will start on `http://localhost:8000`

### 4. Open the Website

Open `index.html` in a web browser or use a local server:

```bash
# Using Python's built-in server
python -m http.server 8080
```

Then navigate to `http://localhost:8080`

## 🎯 How to Use

### Voice Assistant

1. **Click the "Voice Assistant" button** in the header or hero section
2. **Click the microphone icon** to start voice recording
3. **Speak your query** (e.g., "What's my account balance?")
4. **Listen to the AI response** (text and speech)

### Supported Voice Commands

- **Balance Inquiry**: "What's my account balance?"
- **Transaction History**: "Show me my recent transactions"
- **Fund Transfer**: "I want to transfer ₹500"
- **Loan Information**: "Tell me about my home loan"
- **Credit Card**: "What's my credit card limit?"

### Dashboard Features

After logging in, you can:
- View account balance
- See recent transactions
- Use quick action buttons to trigger voice queries
- Access various banking services

## 🔧 Configuration

### Connect to LangGraph Backend

To connect the website to your LangGraph banking assistant:

1. **Convert the notebook to Python module**:
   
   ```python
   # Save this as banking_assistant_backend.py
   # Copy all the agent functions and graph building code from the notebook
   ```

2. **Update the import** in `backend_server.py`:
   
   ```python
   from banking_assistant_backend import banking_assistant, BankingState
   ```

3. **Restart the backend server**

### Customize API Endpoint

In `app.js`, update the API base URL:

```javascript
const API_BASE_URL = 'http://localhost:8000'; // Your backend URL
```

## 🏦 API Endpoints

### POST `/api/voice-banking`

Process voice banking queries

**Request:**
```json
{
  "user_input": "What's my balance?",
  "user_id": "user_001",
  "thread_id": "session_12345"
}
```

**Response:**
```json
{
  "response": "Your account balance is ₹15,750.50",
  "intent": "check_balance",
  "confidence": 0.95,
  "account_balance": 15750.50,
  "transaction_history": null,
  "compliance_passed": true
}
```

### POST `/api/authenticate`

Authenticate user

**Request:**
```json
{
  "username": "user123",
  "password": "password"
}
```

### GET `/api/health`

Health check endpoint

## 🎨 Customization

### Branding

Update colors in `styles.css`:

```css
:root {
    --sbi-blue: #22409A;
    --sbi-orange: #FF6B35;
    /* Add more custom colors */
}
```

### Mock Data

Update user data in `backend_server.py`:

```python
users_db = {
    "user_001": {
        "name": "Your Name",
        "balance": 15750.50,
        "account_number": "ACC123456789"
    }
}
```

## 🔒 Security Considerations

For production deployment:

1. **Enable HTTPS**: Use SSL/TLS certificates
2. **Implement JWT**: Use proper token-based authentication
3. **Add Rate Limiting**: Prevent API abuse
4. **Validate Input**: Sanitize all user inputs
5. **Use Environment Variables**: Never hardcode credentials
6. **Enable CORS properly**: Restrict allowed origins
7. **Add Session Management**: Use Redis or database
8. **Implement Logging**: Track all transactions and queries
9. **Add MFA**: Multi-factor authentication
10. **Compliance**: Ensure PCI DSS and GDPR compliance

## 📱 Browser Compatibility

### Voice Recognition Support:
- ✅ Chrome (desktop & mobile)
- ✅ Edge
- ✅ Safari (limited)
- ❌ Firefox (not supported)

### Fallback:
If voice recognition is not supported, users can type their queries.

## 🐛 Troubleshooting

### Voice recognition not working
- Check browser compatibility
- Ensure microphone permissions are granted
- Try Chrome or Edge browsers

### Backend connection failed
- Verify Flask server is running on port 8000
- Check CORS settings
- Update API_BASE_URL in app.js

### LangGraph import error
- Ensure all notebook code is converted to Python module
- Check Python path configuration
- Install all required dependencies

## 🚀 Production Deployment

### Option 1: Docker

```dockerfile
# Dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "backend_server.py"]
```

### Option 2: Cloud Deployment

- **Frontend**: Deploy to Netlify, Vercel, or GitHub Pages
- **Backend**: Deploy to AWS EC2, Azure App Service, or Google Cloud Run

## 📊 Performance Optimization

1. **Caching**: Implement Redis for session data
2. **CDN**: Use CDN for static assets
3. **Compression**: Enable gzip compression
4. **Lazy Loading**: Load resources on demand
5. **Database**: Use PostgreSQL for production data

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes.

## 🔗 Related Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/services/cognitive-services/openai-service/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

## 📧 Support

For issues or questions:
- Create an issue in the repository
- Contact: support@example.com

---

**Built with ❤️ using LangGraph, Flask, and modern web technologies**
