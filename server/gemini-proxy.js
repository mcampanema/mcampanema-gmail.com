/**
 * Secure Gemini API Proxy
 * Keeps API key server-side, prevents client exposure
 */

import express from 'express';
import cors from 'cors';
import { GoogleGenAI } from '@google/genai';

const app = express();
const PORT = process.env.PORT || 3001;

// CRITICAL: API key stays on server only
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

if (!GEMINI_API_KEY) {
  console.error('❌ GEMINI_API_KEY not set in environment!');
  process.exit(1);
}

const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });

// Middleware
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
  credentials: true
}));
app.use(express.json({ limit: '10mb' }));

// Request logging for transparency
const logRequest = (req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
};
app.use(logRequest);

// Rate limiting (basic - upgrade for production)
const requestCounts = new Map();
const RATE_LIMIT = 100; // requests per hour per IP
const rateLimit = (req, res, next) => {
  const ip = req.ip || req.connection.remoteAddress;
  const now = Date.now();
  const hour = 60 * 60 * 1000;

  if (!requestCounts.has(ip)) {
    requestCounts.set(ip, []);
  }

  const requests = requestCounts.get(ip);
  const recentRequests = requests.filter(time => now - time < hour);

  if (recentRequests.length >= RATE_LIMIT) {
    return res.status(429).json({
      error: 'Rate limit exceeded',
      message: `Maximum ${RATE_LIMIT} requests per hour`
    });
  }

  recentRequests.push(now);
  requestCounts.set(ip, recentRequests);
  next();
};
app.use(rateLimit);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Generate content
app.post('/api/generate', async (req, res) => {
  try {
    const { model = 'gemini-2.5-flash', prompt, config } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt required' });
    }

    console.log(`📝 Generating content with ${model}`);
    console.log(`   Prompt length: ${prompt.length} chars`);

    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: config || {}
    });

    const result = {
      text: response.text,
      usage: response.usageMetadata || null,
      model: model
    };

    // Log usage for transparency
    if (result.usage) {
      console.log(`   ✅ Success | Input: ${result.usage.promptTokenCount} | Output: ${result.usage.candidatesTokenCount}`);
    }

    res.json(result);

  } catch (error) {
    console.error('❌ Generation error:', error.message);
    res.status(500).json({
      error: 'Generation failed',
      message: error.message
    });
  }
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { model = 'gemini-2.5-flash', messages, config } = req.body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: 'Messages array required' });
    }

    console.log(`💬 Chat request with ${model} (${messages.length} messages)`);

    const chat = ai.chats.create({
      model,
      config: config || {}
    });

    // Send all messages
    let lastResponse;
    for (const msg of messages) {
      lastResponse = await chat.sendMessage(msg);
    }

    const result = {
      text: lastResponse.text,
      usage: lastResponse.usageMetadata || null,
      model: model
    };

    if (result.usage) {
      console.log(`   ✅ Chat success | Tokens: ${result.usage.totalTokenCount}`);
    }

    res.json(result);

  } catch (error) {
    console.error('❌ Chat error:', error.message);
    res.status(500).json({
      error: 'Chat failed',
      message: error.message
    });
  }
});

// Video analysis endpoint
app.post('/api/analyze-video', async (req, res) => {
  try {
    const { videoUrl, prompt, model = 'gemini-2.5-flash' } = req.body;

    if (!videoUrl || !prompt) {
      return res.status(400).json({ error: 'videoUrl and prompt required' });
    }

    console.log(`🎥 Analyzing video: ${videoUrl}`);

    const response = await ai.models.generateContent({
      model,
      contents: `Video: ${videoUrl}\n\n${prompt}`
    });

    const result = {
      text: response.text,
      usage: response.usageMetadata || null
    };

    if (result.usage) {
      console.log(`   ✅ Video analysis complete | Tokens: ${result.usage.totalTokenCount}`);
    }

    res.json(result);

  } catch (error) {
    console.error('❌ Video analysis error:', error.message);
    res.status(500).json({
      error: 'Video analysis failed',
      message: error.message
    });
  }
});

// Cost tracking endpoint
app.get('/api/usage-stats', (req, res) => {
  // TODO: Integrate with transparency logger
  res.json({
    message: 'Usage stats coming soon',
    hint: 'Integrate with scripts/ai_transparency_logger.py'
  });
});

// Start server
app.listen(PORT, () => {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  🔒 SECURE GEMINI API PROXY');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`  Port: ${PORT}`);
  console.log(`  API Key: ${GEMINI_API_KEY ? '✅ Configured' : '❌ Missing'}`);
  console.log(`  Rate Limit: ${RATE_LIMIT} req/hour per IP`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
});

export default app;
