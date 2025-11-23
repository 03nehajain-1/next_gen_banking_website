# Next Gen Banking Voice Assistant - Demo Walkthrough (English)

## 🎬 Recording Script for English Demo

### Pre-Recording Setup Checklist
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] Browser opened to http://localhost:3000
- [ ] Microphone permissions granted
- [ ] Audio levels tested
- [ ] Screen recording software ready

---

## 🎭 Demo Flow

### Scene 1: Introduction (30 seconds)
**Narrator Script:**
> "Welcome to the Next Gen Indian Banking Voice Assistant - a revolutionary multilingual banking platform powered by AI. This intelligent system supports English, Hindi, and Gujarati, making banking accessible to millions of Indians in their preferred language. Let's see it in action."

**Visual:** 
- Show login page with clean interface
- Highlight language selector (English/Hindi/Gujarati)
- Pan across the modern UI

---

### Scene 2: Login - Neha's Account (15 seconds)
**Action:**
1. Click on login page
2. Enter credentials:
   - **Username:** neha
   - **Password:** neha123
3. Click "Login"

**Narrator Script:**
> "Let's start by logging in as Neha, one of our customers. The system provides secure authentication while maintaining a simple, user-friendly interface."

**Visual:**
- Show login form
- Type credentials (you can blur password)
- Smooth transition to chat interface

---

### Scene 3: Check Balance (30 seconds)
**Action:**
1. Click microphone button
2. **Say:** "What is my account balance?"
3. Wait for response

**Expected Response:**
> "Hello Neha, your current account balance is ₹1,25,000.00. Account number: NGB001234567890. Is there anything else I can help you with?"

**Narrator Script:**
> "Neha asks about her account balance. The AI assistant, powered by LangGraph and Azure OpenAI, processes her request and provides accurate, real-time information in natural language."

**Visual:**
- Highlight voice input animation
- Show transcription appearing
- Display AI response with proper rupee formatting
- Text-to-speech voice reads the response

---

### Scene 4: View Recent Transactions (40 seconds)
**Action:**
1. Click microphone button
2. **Say:** "Show me my recent transactions"
3. Wait for response

**Expected Response:**
> "Hello Neha, here are your recent transactions:
> 1. 2024-01-15 - CREDIT ₹50,000.00 - Salary credit
> 2. 2024-01-14 - DEBIT ₹5,000.00 - Online shopping
> 3. 2024-01-13 - DEBIT ₹2,500.00 - Restaurant
> Would you like more details?"

**Narrator Script:**
> "Next, Neha wants to review her recent transactions. The assistant retrieves her transaction history and presents it in an easy-to-read format, showing dates, amounts, and descriptions."

**Visual:**
- Show transaction list appearing
- Highlight the structured format
- Point out rupee amounts and transaction types

---

### Scene 5: Loan Inquiry (30 seconds)
**Action:**
1. Click microphone button
2. **Say:** "What is my loan balance?"
3. Wait for response

**Expected Response:**
> "Hello Neha, your loan balance is ₹1,80,000.00 with an interest rate of 7.5% per annum. Is there anything else I can help you with?"

**Narrator Script:**
> "The assistant can also handle complex queries about loans, providing detailed information about loan balances and interest rates."

**Visual:**
- Show loan information display
- Highlight interest rate details

---

### Scene 6: Credit Card Inquiry (30 seconds)
**Action:**
1. Click microphone button
2. **Say:** "What is my credit limit?"
3. Wait for response

**Expected Response:**
> "Hello Neha, your credit limit is ₹2,00,000.00. Is there anything else I can help you with?"

**Narrator Script:**
> "Credit card information is instantly accessible through simple voice commands."

**Visual:**
- Display credit limit information
- Show smooth interaction flow

---

### Scene 7: Fund Transfer Demo (45 seconds)
**Action:**
1. Click microphone button
2. **Say:** "Transfer 10000 rupees to Niyati"
3. Wait for response

**Expected Response:**
> "✅ Success! Neha, ₹10,000.00 has been transferred to Niyati. Your new balance: ₹1,15,000.00. Recipient account: NGB987654321098."

**Narrator Script:**
> "Now let's demonstrate the fund transfer capability. Neha wants to send money to her friend Niyati. The system processes the transfer securely, validates the recipient, checks the balance, and completes the transaction - all through natural voice commands."

**Visual:**
- Show transfer confirmation
- Highlight the updated balance
- Display recipient details
- Show transaction success indicator (✅)

---

### Scene 8: Verify Transfer (30 seconds)
**Action:**
1. Click microphone button
2. **Say:** "Show my recent transactions"
3. Wait for response

**Expected Response:**
> "Hello Neha, here are your recent transactions:
> 1. 2025-11-23 21:45:30 - DEBIT ₹10,000.00 - Transfer to Niyati
> 2. 2024-01-15 - CREDIT ₹50,000.00 - Salary credit
> 3. 2024-01-14 - DEBIT ₹5,000.00 - Online shopping
> Would you like more details?"

**Narrator Script:**
> "Let's verify the transfer by checking the transaction history again. Notice the new transaction at the top showing the transfer to Niyati."

**Visual:**
- Show updated transaction list
- Highlight the new transfer entry
- Point out the updated balance

---

### Scene 9: Logout and Login as Niyati (20 seconds)
**Action:**
1. Click logout button
2. Login with:
   - **Username:** niyati
   - **Password:** niyati123
3. Click "Login"

**Narrator Script:**
> "Now let's log in as Niyati to verify she received the funds."

**Visual:**
- Smooth logout transition
- Quick login as second user

---

### Scene 10: Verify Received Funds (30 seconds)
**Action:**
1. Click microphone button
2. **Say:** "What is my account balance?"
3. Wait for response

**Expected Response:**
> "Hello Niyati, your current account balance is ₹97,500.00. Account number: NGB987654321098. Is there anything else I can help you with?"

**Narrator Script:**
> "Niyati checks her balance and confirms she received the ₹10,000 from Neha. Her balance has increased from ₹87,500 to ₹97,500."

**Visual:**
- Show Niyati's updated balance
- Highlight the increased amount

---

### Scene 11: Check Niyati's Transactions (30 seconds)
**Action:**
1. Click microphone button
2. **Say:** "Show my recent transactions"
3. Wait for response

**Expected Response:**
> "Hello Niyati, here are your recent transactions:
> 1. 2025-11-23 21:45:30 - CREDIT ₹10,000.00 - Transfer from Neha
> 2. 2024-01-10 - DEBIT ₹15,000.00 - EMI payment
> 3. 2024-01-09 - CREDIT ₹40,000.00 - Freelance income
> Would you like more details?"

**Narrator Script:**
> "Her transaction history shows the incoming transfer from Neha, completing the end-to-end fund transfer demonstration."

**Visual:**
- Display Niyati's transaction history
- Highlight the credit entry from Neha

---

### Scene 12: Technical Architecture Overview (30 seconds)
**Narrator Script:**
> "Behind the scenes, this powerful system uses cutting-edge technology: LangGraph for multi-agent workflow orchestration, Azure OpenAI for natural language understanding, Whisper AI for speech recognition, and a Flask backend with React-like frontend. The system features real-time intent detection with fallback mechanisms, multilingual support, and secure transaction processing."

**Visual:**
- Show a diagram or overlay with tech stack:
  - LangGraph (Multi-Agent Workflow)
  - Azure OpenAI (LLM)
  - Whisper AI (Speech-to-Text)
  - Web Speech API (Text-to-Speech)
  - Flask Backend
  - JavaScript Frontend
  - Male Voice TTS (David/James/Ravi)

---

### Scene 13: Key Features Summary (25 seconds)
**Narrator Script:**
> "Key features include: Voice-activated banking with male voice responses, real-time balance and transaction queries, secure fund transfers with validation, multilingual support for English, Hindi, and Gujarati, intelligent intent detection with keyword fallback, and comprehensive error handling with user-friendly messages."

**Visual:**
- Bullet points appearing on screen:
  - ✅ Voice-Activated Banking
  - ✅ Real-Time Account Information
  - ✅ Secure Fund Transfers
  - ✅ Multilingual Support (En/Hi/Gu)
  - ✅ Intelligent Intent Detection
  - ✅ Male Voice TTS
  - ✅ Rupee Currency (₹)
  - ✅ Error Handling & Validation

---

### Scene 14: Closing (15 seconds)
**Narrator Script:**
> "This Next Gen Indian Banking Voice Assistant represents the future of accessible, multilingual banking in India. Thank you for watching!"

**Visual:**
- Fade to project title screen
- Show GitHub/Contact information
- Credits roll

---

## 📝 Recording Tips

### Voice Recording
1. **Environment:** Record in a quiet room with minimal echo
2. **Microphone:** Use a good quality microphone positioned 6-8 inches away
3. **Tone:** Professional, enthusiastic, clear enunciation
4. **Pace:** Moderate speed - not too fast, not too slow
5. **Practice:** Rehearse the script 2-3 times before recording

### Screen Recording
1. **Resolution:** 1920x1080 (Full HD) minimum
2. **Frame Rate:** 60 FPS for smooth animations
3. **Cursor:** Use cursor highlighting/spotlight effect
4. **Browser:** Use Chrome in full-screen mode (F11)
5. **Zoom:** Zoom in on important elements when needed

### User Interactions
1. **Typing Speed:** Type at natural speed (not too fast)
2. **Waiting:** Allow 2-3 seconds for responses to fully appear
3. **Voice Commands:** Speak clearly and naturally
4. **Transitions:** Smooth transitions between scenes

### Post-Production
1. **Add Background Music:** Soft, professional music (royalty-free)
2. **Add Captions:** For accessibility
3. **Color Correction:** Ensure consistent brightness
4. **Audio Levels:** Normalize audio, reduce background noise
5. **Transitions:** Add subtle fade effects between scenes
6. **Annotations:** Add arrows/highlights to draw attention

---

## 🎯 Demo Scenarios

### Quick Demo (2 minutes)
- Login as Neha
- Check balance
- View transactions
- Logout

### Standard Demo (4-5 minutes)
- Login as Neha
- Check balance
- View transactions
- Loan inquiry
- Transfer funds to Niyati
- Login as Niyati
- Verify received funds

### Full Demo (6-7 minutes)
- All standard demo steps
- Credit inquiry
- Technical overview
- Features summary
- Error handling demonstration

---

## 🚨 Troubleshooting During Recording

### If Voice Recognition Fails
- **Fallback:** Type the query manually (the system accepts text input too)
- **Retry:** Click microphone again and speak more clearly

### If Response is Slow
- **Wait:** AI processing can take 2-3 seconds
- **Edit:** Can be sped up in post-production

### If Amount Shows Dollars
- **Restart Backend:** Ensure latest code is running
- **Verify:** Check that fallback intent detection is working

### If Transfer Fails
- **Check Balance:** Ensure sufficient funds
- **Check Recipient:** Verify recipient name is correct (Niyati/Neha)
- **Retry:** Try the command again with clear enunciation

---

## 📊 Test Data Reference

### Neha's Account
- **Username:** neha
- **Password:** neha123
- **Initial Balance:** ₹1,25,000.00
- **Account Number:** NGB001234567890
- **Loan Balance:** ₹1,80,000.00
- **Interest Rate:** 7.5% per annum
- **Credit Limit:** ₹2,00,000.00

### Niyati's Account
- **Username:** niyati
- **Password:** niyati123
- **Initial Balance:** ₹87,500.00
- **Account Number:** NGB987654321098
- **Loan Balance:** ₹41,20,000.00
- **Interest Rate:** 7.5% per annum
- **Credit Limit:** ₹1,50,000.00

---

## 🎬 Sample Voice Commands

### Balance Queries
- "What is my account balance?"
- "Show me my balance"
- "How much money do I have?"
- "Check my account balance"

### Transaction Queries
- "Show my recent transactions"
- "What are my recent transactions?"
- "Show me my transaction history"
- "Display my last few transactions"

### Loan Queries
- "What is my loan balance?"
- "How much loan do I have?"
- "Tell me about my loan"
- "Show my loan details"

### Credit Queries
- "What is my credit limit?"
- "How much credit do I have?"
- "Tell me about my credit card"

### Transfer Commands
- "Transfer 10000 rupees to Niyati"
- "Send 5000 to Neha"
- "I want to transfer money to Niyati"
- "Transfer ₹10000 to Niyati"

---

## 🎥 Video Editing Checklist

- [ ] Trim unnecessary pauses
- [ ] Add intro title screen (5 seconds)
- [ ] Add background music (subtle, professional)
- [ ] Add captions/subtitles
- [ ] Highlight important elements (arrows, circles)
- [ ] Add transition effects between scenes
- [ ] Color grade for consistency
- [ ] Normalize audio levels
- [ ] Add outro with contact info (5 seconds)
- [ ] Export in 1080p or 4K
- [ ] Add thumbnail image

---

## 📱 Social Media Versions

### YouTube (Full Version)
- **Length:** 6-7 minutes
- **Aspect Ratio:** 16:9
- **Include:** Full walkthrough with technical details

### LinkedIn (Professional)
- **Length:** 2-3 minutes
- **Aspect Ratio:** 16:9 or 1:1
- **Focus:** Business value, technical architecture

### Instagram/TikTok (Short)
- **Length:** 30-60 seconds
- **Aspect Ratio:** 9:16 (vertical)
- **Focus:** Most impressive feature (fund transfer)

### Twitter/X (Teaser)
- **Length:** 30 seconds
- **Aspect Ratio:** 16:9
- **Focus:** Quick demo with call-to-action

---

## 🎯 Call-to-Action Options

1. "Try the demo yourself at [GitHub link]"
2. "Star the project on GitHub"
3. "Share your feedback in the comments"
4. "Follow for more AI banking innovations"
5. "Contact us for enterprise solutions"

---

## ✅ Pre-Recording Final Checklist

Before starting the recording:

1. [ ] Backend server running (verify with health check)
2. [ ] Frontend server running (http://localhost:3000)
3. [ ] Browser cleared of other tabs
4. [ ] Desktop clean (professional background)
5. [ ] Notifications disabled (Do Not Disturb mode)
6. [ ] Screen recording software ready
7. [ ] Microphone tested
8. [ ] Audio levels checked
9. [ ] Script rehearsed
10. [ ] Test run completed successfully
11. [ ] Water nearby (for voice clarity)
12. [ ] Timer/stopwatch ready

---

Good luck with your recording! 🎬🎤✨
