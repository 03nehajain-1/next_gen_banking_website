# Next Gen Banking - Frontend

## Frontend Files

This directory contains all the frontend files for the Next Gen Indian Banking website.

### Files:
- `index.html` - Main HTML file with banking portal UI
- `styles.css` - All styling and CSS variables
- `app.js` - JavaScript for API calls and frontend logic
- `translations.js` - Multilingual translations (English, Hindi, Gujarati)

## Running the Frontend

### Option 1: Using Python HTTP Server
```bash
cd /Users/n0j01j4/hackathon/templates/next_gen_banking_website/frontend
python3 -m http.server 3000
```

Then open: http://localhost:3000

### Option 2: Using Node.js
```bash
npx http-server -p 3000
```

### Option 3: Open Directly
Simply open `index.html` in your browser. Make sure backend is running on port 8000.

## Features

- **Multilingual Support**: English, Hindi (हिंदी), Gujarati (ગુજરાતી)
- **Voice Assistant**: Click microphone to interact with AI banking assistant
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean, professional banking interface

## User Accounts

### Neha Sharma
- Username: `neha`
- Password: `neha123`

### Niyati Patel
- Username: `niyati`
- Password: `niyati456`

## Configuration

The frontend connects to the backend API at:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

Change this in `app.js` if your backend runs on a different port.
