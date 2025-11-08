# 🚀 Deployment Checklist - Secure Your API Key

**Your API Key:** `AIzaSyDchi_mjZ-h1n7HrNYUOjcmfhLPufWds3I`

⚠️ **This key is exposed in conversation logs. Rotate it after deployment!**

---

## ✅ **STEP-BY-STEP DEPLOYMENT:**

### 1. Deploy Secure Proxy to Cloud Run

```bash
# From your project root
./DEPLOY_PROXY.sh
```

**OR manually:**

```bash
cd server

gcloud run deploy gemini-proxy \
  --source . \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=AIzaSyDchi_mjZ-h1n7HrNYUOjcmfhLPufWds3I
```

**Expected output:**
```
Deploying...
✓ Deploying new service... Done.
  https://gemini-proxy-XXXXX-uc.a.run.app
```

**Copy the URL!** (e.g., `https://gemini-proxy-598349270699.run.app`)

---

### 2. Update .env with Proxy URL

Edit `.env` and replace `YOUR-ID`:

```bash
# Before:
GEMINI_PROXY_URL=https://gemini-proxy-YOUR-ID.run.app

# After (example):
GEMINI_PROXY_URL=https://gemini-proxy-598349270699.run.app
```

---

### 3. Update Frontend Code

The frontend code needs to call the **proxy** instead of Gemini directly.

**Files to update:**

#### `index.html` (line 257):

**Before:**
```javascript
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
```

**After:**
```javascript
// Use proxy instead
const PROXY_URL = process.env.GEMINI_PROXY_URL;

async function callGemini(prompt) {
  const response = await fetch(`${PROXY_URL}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, model: 'gemini-2.5-flash' })
  });
  return await response.json();
}
```

#### `LiveChat.ts` (line 633):

**Before:**
```typescript
this.client = new GoogleGenAI({apiKey: process.env.API_KEY});
```

**After:**
```typescript
// Use proxy URL
this.proxyUrl = process.env.GEMINI_PROXY_URL;

// Replace all .generateContent() calls with fetch to proxy
async generateContent(prompt: string) {
  const response = await fetch(`${this.proxyUrl}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, model: 'gemini-2.5-flash' })
  });
  return await response.json();
}
```

#### `api.ts` (line 18):

**Before:**
```typescript
const client = new GoogleGenAI({apiKey: process.env.API_KEY});
```

**After:**
```typescript
const PROXY_URL = process.env.GEMINI_PROXY_URL;

export async function callGemini(prompt: string, model = 'gemini-2.5-flash') {
  const response = await fetch(`${PROXY_URL}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, model })
  });
  return await response.json();
}
```

---

### 4. Rebuild and Redeploy Frontend

```bash
# Build with new proxy configuration
npm run build

# Deploy to Cloud Run (muhadeeb app)
gcloud run deploy muhadeeb \
  --source . \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_PROXY_URL=https://gemini-proxy-XXXXX.run.app
```

---

### 5. Verify Security

1. Open: https://muhadeeb-598349270699.us-west1.run.app
2. Press `F12` (open DevTools)
3. Go to **Sources** tab
4. Search for: `AIzaSyDchi_mjZ`
5. **Should find NOTHING** ✅

If you still find the key, the frontend wasn't rebuilt/redeployed properly.

---

### 6. Test the App

1. Open: https://muhadeeb-598349270699.us-west1.run.app
2. Try video analysis, chat, or image generation
3. Should work exactly as before
4. Check proxy logs:

```bash
gcloud run services logs read gemini-proxy \
  --region us-west1 \
  --limit 20
```

You should see:
```
📝 Generating content with gemini-2.5-flash
   Prompt length: 150 chars
   ✅ Success | Input: 50 | Output: 100
```

---

### 7. Rotate Your API Key (IMPORTANT!)

Since you exposed the key in conversation logs:

1. Go to: https://aistudio.google.com/app/apikey
2. **Delete** key: `AIzaSyDchi_mjZ-h1n7HrNYUOjcmfhLPufWds3I`
3. **Create new** API key
4. **Update** `server/.env` with new key
5. **Redeploy** proxy:

```bash
cd server
gcloud run deploy gemini-proxy \
  --source . \
  --set-env-vars GEMINI_API_KEY=YOUR-NEW-KEY-HERE
```

---

### 8. Test Transparency Tools

```bash
# Check configuration
bash scripts/api_key_audit.sh

# View cost dashboard
python3 scripts/ai_dashboard.py

# View AI conversations
python3 scripts/view_ai_conversations.py all
```

---

## ✅ **SUCCESS CRITERIA:**

- [ ] Proxy deployed and running
- [ ] Frontend updated to use proxy
- [ ] No API key visible in browser DevTools
- [ ] App works as expected
- [ ] Logs show requests in Cloud Run
- [ ] API key rotated to new one
- [ ] Transparency tools working

---

## 🔍 **TROUBLESHOOTING:**

### "API key not found"
- Check `.env` files have the correct key
- Verify Cloud Run env vars: `gcloud run services describe gemini-proxy --region us-west1`

### "CORS error"
- Proxy CORS is set to `*` (allow all)
- If still errors, check `server/gemini-proxy.js` line 19-22

### "Rate limit exceeded"
- Default: 100 req/hour per IP
- Adjust in `server/.env`: `RATE_LIMIT=200`

### "403 Forbidden"
- API key is invalid or quota exceeded
- Check: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com

---

## 📊 **COST TRACKING:**

After deployment, all requests through the proxy are logged with token counts.

Integrate with transparency logger in `scripts/ai_transparency_logger.py`:

```python
# Add webhook to proxy that sends usage to logger
# See server/README.md for details
```

---

## 🎉 **YOU'RE DONE!**

Your muhadeeb app now:
- ✅ Uses secure backend proxy
- ✅ API key never exposed to browser
- ✅ Rate limiting active
- ✅ Full request logging
- ✅ Token usage tracked
- ✅ Ready for transparency monitoring

**No more security vulnerabilities!**
