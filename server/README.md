# 🔒 Secure Gemini API Proxy

**CRITICAL SECURITY FIX** for exposed API keys in client-side code.

---

## 🚨 THE PROBLEM

Your current deployment (`muhadeeb-598349270699.us-west1.run.app`) has a **CRITICAL SECURITY ISSUE**:

```typescript
// vite.config.ts (INSECURE)
define: {
  'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),  // ❌ EXPOSED IN BROWSER
}
```

**This means:**
- ❌ API key is embedded in JavaScript bundle
- ❌ ANYONE can view it in browser DevTools
- ❌ ANYONE can steal and use your key
- ❌ Unlimited costs from stolen keys

---

## ✅ THE SOLUTION

This backend proxy keeps API keys SERVER-SIDE only:

```
┌─────────┐          ┌──────────┐          ┌─────────┐
│ Browser │  HTTPS   │  Proxy   │  Secure  │ Gemini  │
│ (public)├─────────►│ (server) ├─────────►│   API   │
└─────────┘          └──────────┘          └─────────┘
                      API key stays
                      on server only
```

**Benefits:**
- ✅ API key never sent to browser
- ✅ Rate limiting per IP
- ✅ Request logging for transparency
- ✅ Cost control via server-side limits
- ✅ Can add authentication later

---

## 🚀 DEPLOYMENT TO GOOGLE CLOUD RUN

### 1. Install Dependencies

```bash
cd server
npm install
```

### 2. Test Locally

```bash
# Set API key
export GEMINI_API_KEY="your-actual-key-here"

# Start server
npm start
```

Server runs on http://localhost:3001

### 3. Test the Proxy

```bash
# Health check
curl http://localhost:3001/health

# Test generation
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello", "model": "gemini-2.5-flash"}'
```

### 4. Deploy to Cloud Run

```bash
# Ensure you're in /server directory
cd server

# Deploy (will prompt for project/region)
gcloud run deploy gemini-proxy \
  --source . \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="your-actual-key-here"

# OR use secret manager (recommended)
gcloud run deploy gemini-proxy \
  --source . \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest
```

You'll get a URL like: `https://gemini-proxy-xxxxx-uc.a.run.app`

---

## 🔧 UPDATE FRONTEND TO USE PROXY

### Before (INSECURE):

```typescript
// Direct API call with exposed key
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });  // ❌ BAD
const response = await ai.models.generateContent({
  model: 'gemini-2.5-flash',
  contents: prompt
});
```

### After (SECURE):

```typescript
// Call your proxy instead
const PROXY_URL = 'https://gemini-proxy-xxxxx-uc.a.run.app';  // ✅ SECURE

const response = await fetch(`${PROXY_URL}/api/generate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'gemini-2.5-flash',
    prompt: 'Your prompt here'
  })
});

const result = await response.json();
console.log(result.text);
console.log('Tokens used:', result.usage);
```

---

## 📡 API ENDPOINTS

### `GET /health`
Health check

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-08T10:00:00.000Z"
}
```

### `POST /api/generate`
Generate content

**Request:**
```json
{
  "model": "gemini-2.5-flash",
  "prompt": "Your prompt here",
  "config": {}  // Optional Gemini config
}
```

**Response:**
```json
{
  "text": "Generated response...",
  "usage": {
    "promptTokenCount": 150,
    "candidatesTokenCount": 200,
    "totalTokenCount": 350
  },
  "model": "gemini-2.5-flash"
}
```

### `POST /api/chat`
Multi-turn chat

**Request:**
```json
{
  "model": "gemini-2.5-flash",
  "messages": [
    "Hello",
    "How are you?"
  ],
  "config": {}
}
```

**Response:** Same as `/api/generate`

### `POST /api/analyze-video`
Analyze video content

**Request:**
```json
{
  "videoUrl": "https://youtube.com/watch?v=...",
  "prompt": "What's happening in this video?",
  "model": "gemini-2.5-flash"
}
```

**Response:** Same as `/api/generate`

### `GET /api/usage-stats`
Usage statistics (coming soon)

---

## 🛡️ SECURITY FEATURES

### Rate Limiting
- Default: 100 requests/hour per IP
- Prevents abuse
- Returns 429 on limit exceeded

### Request Logging
All requests logged to console:
```
[2025-11-08T10:00:00.000Z] POST /api/generate
📝 Generating content with gemini-2.5-flash
   Prompt length: 150 chars
   ✅ Success | Input: 50 | Output: 100
```

### Environment-Based Config
```bash
# Required
GEMINI_API_KEY=your-key-here

# Optional
PORT=3001                           # Default: 3001
ALLOWED_ORIGINS=https://your-app.com  # Default: * (all)
RATE_LIMIT=100                      # Requests per hour per IP
```

---

## 📊 COST TRACKING

The proxy logs token usage for every request. Integrate with transparency logger:

```python
# After each request, log to transparency system
from scripts.ai_transparency_logger import log_ai_call

log_ai_call(
    model="gemini-2.5-flash",
    provider="google",
    prompt=prompt,
    response=response_text,
    input_tokens=usage.promptTokenCount,
    output_tokens=usage.candidatesTokenCount
)
```

---

## 🔄 MIGRATION PLAN

### Step 1: Deploy Proxy
```bash
cd server
gcloud run deploy gemini-proxy --source .
```

### Step 2: Update Frontend
Replace all `GoogleGenAI({ apiKey: ... })` with fetch calls to proxy.

### Step 3: Remove Client-Side Key
Delete from `vite.config.ts`:
```typescript
define: {
  // DELETE THESE LINES
  // 'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
  // 'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
}
```

### Step 4: Redeploy Frontend
```bash
# Build without API key
npm run build

# Deploy to Cloud Run
gcloud run deploy muhadeeb \
  --source . \
  --set-env-vars PROXY_URL=https://gemini-proxy-xxxxx-uc.a.run.app
```

### Step 5: Verify Security
1. Open https://muhadeeb-598349270699.us-west1.run.app
2. Press F12 (DevTools)
3. Search for "apiKey" or your actual key
4. Should find NOTHING

---

## 🚦 TESTING

### Local Testing
```bash
# Terminal 1: Start proxy
cd server
npm start

# Terminal 2: Test
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "model": "gemini-2.5-flash"}'
```

### Production Testing
```bash
curl -X POST https://gemini-proxy-xxxxx-uc.a.run.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "model": "gemini-2.5-flash"}'
```

---

## 📈 MONITORING

### View Logs (Cloud Run)
```bash
gcloud run services logs read gemini-proxy \
  --region us-west1 \
  --limit 50
```

### Stream Live Logs
```bash
gcloud run services logs tail gemini-proxy --region us-west1
```

### Cost Tracking
See `TRANSPARENCY_GUIDE.md` for full cost tracking setup.

---

## ⚠️ IMPORTANT NOTES

1. **DO NOT** commit API keys to git
2. **DO NOT** use `--allow-unauthenticated` for production (add auth)
3. **DO** use Google Secret Manager for keys
4. **DO** set up proper CORS for production
5. **DO** monitor logs regularly

---

## 🔐 ADDING AUTHENTICATION (Production)

```javascript
// Simple API key auth
app.use((req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  const validKeys = process.env.VALID_API_KEYS?.split(',') || [];

  if (!validKeys.includes(apiKey)) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  next();
});
```

Then in frontend:
```typescript
fetch(`${PROXY_URL}/api/generate`, {
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-frontend-api-key'  // Different from Gemini key
  },
  ...
})
```

---

## 📞 SUPPORT

Questions? Check:
1. `TRANSPARENCY_GUIDE.md` for cost tracking
2. Server logs: `gcloud run services logs read gemini-proxy`
3. Health endpoint: `https://your-proxy.run.app/health`

---

**Remember: NEVER expose API keys in client-side code!**
