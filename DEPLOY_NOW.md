# 🚀 DEPLOY PROXY - QUICK START

**Run this on your LOCAL MACHINE** (not Claude Code Web)

---

## ⚡ **ONE-COMMAND DEPLOYMENT:**

```bash
./deploy.sh
```

This script will:
- ✅ Check prerequisites (gcloud, npm)
- ✅ Verify API key configuration
- ✅ Deploy to Cloud Run
- ✅ Get your proxy URL
- ✅ Auto-update .env file
- ✅ Show next steps

---

## 📋 **MANUAL DEPLOYMENT (if script doesn't work):**

### Step 1: Prerequisites

```bash
# Install Google Cloud SDK (if needed)
# https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Set your project (replace YOUR-PROJECT-ID)
gcloud config set project YOUR-PROJECT-ID

# Enable Cloud Run API
gcloud services enable run.googleapis.com
```

### Step 2: Deploy

```bash
cd server

gcloud run deploy gemini-proxy \
  --source . \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=AIzaSyDchi_mjZ-h1n7HrNYUOjcmfhLPufWds3I
```

### Step 3: Get URL

The deployment will output a URL like:
```
Service [gemini-proxy] revision [gemini-proxy-00001-abc] has been deployed
and is serving 100 percent of traffic.
Service URL: https://gemini-proxy-598349270699-uc.a.run.app
```

### Step 4: Update .env

Copy the URL and update `.env`:

```bash
# Replace YOUR-ID with actual ID from deployment
GEMINI_PROXY_URL=https://gemini-proxy-598349270699-uc.a.run.app
```

### Step 5: Test

```bash
# Health check
curl https://gemini-proxy-598349270699-uc.a.run.app/health

# Should return:
# {"status":"ok","timestamp":"2025-11-08T..."}

# Test generation
curl -X POST https://gemini-proxy-598349270699-uc.a.run.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Say hello","model":"gemini-2.5-flash"}'
```

---

## 🔧 **TROUBLESHOOTING:**

### "gcloud: command not found"
Install Google Cloud SDK:
https://cloud.google.com/sdk/docs/install

### "You do not currently have an active account"
```bash
gcloud auth login
```

### "Failed to find attribute [project]"
```bash
gcloud config set project YOUR-PROJECT-ID
```

### "API [run.googleapis.com] not enabled"
```bash
gcloud services enable run.googleapis.com
```

### "Permission denied"
Your account needs Cloud Run Admin role:
- Go to: https://console.cloud.google.com/iam-admin/iam
- Add role: Cloud Run Admin

---

## 📊 **VERIFY DEPLOYMENT:**

```bash
# List Cloud Run services
gcloud run services list --region us-west1

# View service details
gcloud run services describe gemini-proxy --region us-west1

# View logs
gcloud run services logs read gemini-proxy --region us-west1 --limit 20
```

---

## ⏭️ **AFTER DEPLOYMENT:**

1. ✅ Copy the proxy URL
2. ✅ Update `.env` file with proxy URL
3. ✅ Test proxy endpoint
4. ✅ Update frontend code (see `DEPLOYMENT_CHECKLIST.md`)
5. ✅ Redeploy muhadeeb app
6. ✅ Rotate API key

---

## 🔗 **WHAT YOU JUST DEPLOYED:**

- **Service:** `gemini-proxy`
- **Region:** `us-west1`
- **Memory:** 512Mi
- **CPU:** 1
- **Min instances:** 0 (scales to zero)
- **Max instances:** 10
- **Timeout:** 60 seconds
- **Access:** Public (unauthenticated)

**Your muhadeeb app will call this proxy instead of Gemini directly.**

---

## 🎯 **NEXT STEPS:**

See `DEPLOYMENT_CHECKLIST.md` for complete frontend migration guide.

---

**Need help?** Check the logs:
```bash
gcloud run services logs tail gemini-proxy --region us-west1
```
