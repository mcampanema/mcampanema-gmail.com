#!/bin/bash
# Quick Deploy Script for Secure Gemini Proxy
# Run this from your LOCAL machine (not Claude Code Web)

set -e  # Exit on error

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 DEPLOYING SECURE GEMINI API PROXY TO CLOUD RUN"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found!"
    echo "   Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found!"
    echo "   Install Node.js from: https://nodejs.org/"
    exit 1
fi

echo "✅ gcloud found: $(gcloud --version | head -1)"
echo "✅ npm found: $(npm --version)"
echo

# Check if in correct directory
if [ ! -f "server/gemini-proxy.js" ]; then
    echo "❌ Error: Must run from project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected file: server/gemini-proxy.js"
    exit 1
fi

echo "✅ In correct directory"
echo

# Check API key
if [ ! -f "server/.env" ]; then
    echo "❌ Error: server/.env not found"
    echo "   Create it with:"
    echo "   GEMINI_API_KEY=your-key-here"
    exit 1
fi

source server/.env

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not set in server/.env"
    exit 1
fi

echo "✅ API key configured: ${GEMINI_API_KEY:0:10}...${GEMINI_API_KEY: -4}"
echo

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ -z "$CURRENT_PROJECT" ]; then
    echo "❌ No Google Cloud project configured"
    echo "   Run: gcloud config set project YOUR-PROJECT-ID"
    exit 1
fi

echo "📦 Using Google Cloud Project: $CURRENT_PROJECT"
echo

# Confirm deployment
read -p "🔹 Deploy to Cloud Run? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo
echo "🚀 Deploying to Cloud Run..."
echo

# Deploy
cd server

gcloud run deploy gemini-proxy \
  --source . \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY" \
  --min-instances 0 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --quiet

if [ $? -eq 0 ]; then
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ✅ DEPLOYMENT SUCCESSFUL!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe gemini-proxy --region us-west1 --format='value(status.url)')

    echo "🔗 Proxy URL: $SERVICE_URL"
    echo
    echo "📝 Next steps:"
    echo "   1. Update .env file with this URL:"
    echo "      GEMINI_PROXY_URL=$SERVICE_URL"
    echo
    echo "   2. Test the proxy:"
    echo "      curl $SERVICE_URL/health"
    echo
    echo "   3. Update frontend to use proxy"
    echo "   4. Redeploy muhadeeb app"
    echo "   5. Rotate API key at: https://aistudio.google.com/app/apikey"
    echo

    # Offer to update .env automatically
    cd ..
    read -p "🔹 Update .env file automatically? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f ".env" ]; then
            # Update or add GEMINI_PROXY_URL
            if grep -q "GEMINI_PROXY_URL=" .env; then
                # Replace existing
                sed -i.bak "s|GEMINI_PROXY_URL=.*|GEMINI_PROXY_URL=$SERVICE_URL|" .env
                echo "✅ Updated GEMINI_PROXY_URL in .env"
            else
                # Add new
                echo "" >> .env
                echo "# Auto-updated by deployment script" >> .env
                echo "GEMINI_PROXY_URL=$SERVICE_URL" >> .env
                echo "✅ Added GEMINI_PROXY_URL to .env"
            fi

            echo
            echo "📄 Current .env configuration:"
            grep -E "^(GEMINI_API_KEY|GEMINI_PROXY_URL)=" .env | sed 's/\(.\{20\}\).*/\1.../'
        else
            echo "❌ .env file not found in project root"
        fi
    fi

    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🎉 READY TO SECURE YOUR APP!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

else
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  ❌ DEPLOYMENT FAILED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    echo "Common issues:"
    echo "  • Not authenticated: gcloud auth login"
    echo "  • Wrong project: gcloud config set project YOUR-PROJECT"
    echo "  • APIs not enabled: gcloud services enable run.googleapis.com"
    echo
    exit 1
fi
