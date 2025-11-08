#!/bin/bash
# Deploy Secure Gemini API Proxy to Cloud Run

echo "🚀 Deploying Secure Gemini API Proxy..."
echo ""

# Change to server directory
cd server

# Deploy to Cloud Run
gcloud run deploy gemini-proxy \
  --source . \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=AIzaSyDchi_mjZ-h1n7HrNYUOjcmfhLPufWds3I \
  --min-instances 0 \
  --max-instances 10 \
  --memory 256Mi \
  --cpu 1 \
  --timeout 60

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔗 Your proxy URL will be shown above (e.g., https://gemini-proxy-xxxxx-uc.a.run.app)"
echo ""
echo "⚠️  IMPORTANT: After deployment, rotate your API key at:"
echo "   https://aistudio.google.com/app/apikey"
echo ""
echo "📝 Next steps:"
echo "   1. Copy the proxy URL from above"
echo "   2. Update your frontend to use the proxy URL"
echo "   3. Remove API key from vite.config.ts"
echo "   4. Redeploy frontend"
echo ""
