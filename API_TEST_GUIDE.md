# SUPER BEING API TEST GUIDE
**Generated:** 2025-11-08
**Purpose:** Test all deployed Firebase Functions

---

## 📍 BASE URL
```
https://us-central1-super-being.cloudfunctions.net
```

---

## 🧠 KNOWLEDGE GRAPH ENDPOINTS

### 1. Build Knowledge Graph
**Endpoint:** `/knowledgeGraphBuilder`
**Method:** POST
**What it does:** Creates a self-expanding knowledge graph starting from "Consciousness"

**Test Command:**
```bash
curl -X POST https://us-central1-super-being.cloudfunctions.net/knowledgeGraphBuilder \
  -H "Content-Type: application/json"
```

**Save response to:**
```bash
curl -X POST https://us-central1-super-being.cloudfunctions.net/knowledgeGraphBuilder \
  -H "Content-Type: application/json" > knowledge_graph_response.json
```

---

### 2. Get Knowledge Graph Status
**Endpoint:** `/graphStatus`
**Method:** GET
**What it does:** Shows current knowledge graph statistics

**Test Command:**
```bash
curl https://us-central1-super-being.cloudfunctions.net/graphStatus
```

**Save response to:**
```bash
curl https://us-central1-super-being.cloudfunctions.net/graphStatus > graph_status.json
```

---

## 📖 GENESIS PROJECT ENDPOINTS

### 3. Start Genesis Project
**Endpoint:** `/genesisProject`
**Method:** POST
**What it does:** Begins creation myth generation

**Test Command:**
```bash
curl -X POST https://us-central1-super-being.cloudfunctions.net/genesisProject \
  -H "Content-Type: application/json"
```

**Save response to:**
```bash
curl -X POST https://us-central1-super-being.cloudfunctions.net/genesisProject \
  -H "Content-Type: application/json" > genesis_start.json
```

---

### 4. Read Genesis Project
**Endpoint:** `/readGenesisProject`
**Method:** GET
**What it does:** Returns the full creation saga

**Test Command:**
```bash
curl https://us-central1-super-being.cloudfunctions.net/readGenesisProject
```

**Save response to:**
```bash
curl https://us-central1-super-being.cloudfunctions.net/readGenesisProject > genesis_saga.json
```

---

## 🐭 MUHADEEB (Film Production) ENDPOINTS

⚠️ **NOTE:** These require Firestore to be enabled first!

### 5. Create Story
**Endpoint:** `/muhadeebCreateStory`
**Method:** POST
**What it does:** Generates a cinematic short film story from a prompt

**Test Command:**
```bash
curl -X POST https://us-central1-super-being.cloudfunctions.net/muhadeebCreateStory \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A lone desert mouse discovers an ancient library buried in the sand","style":"cinematic"}'
```

**Save response to:**
```bash
curl -X POST https://us-central1-super-being.cloudfunctions.net/muhadeebCreateStory \
  -H "Content-Type: application/json" \
  -d '{"prompt":"The first test of MUHADEEB - Claude and COMET working together","style":"cinematic"}' > muhadeeb_story.json
```

---

### 6. Generate Storyboard
**Endpoint:** `/muhadeebGenerateStoryboard`
**Method:** POST
**What it does:** Creates detailed shot breakdown from a story

**Test Command (replace STORY_ID with ID from step 5):**
```bash
curl -X POST https://us-central1-super-being.cloudfunctions.net/muhadeebGenerateStoryboard \
  -H "Content-Type: application/json" \
  -d '{"storyId":"story_1234567890"}'
```

---

### 7. Generate ComfyUI Workflow
**Endpoint:** `/muhadeebGenerateWorkflow`
**Method:** POST
**What it does:** Creates ComfyUI workflow JSON for a specific shot

**Test Command:**
```bash
curl -X POST https://us-central1-super-being.cloudfunctions.net/muhadeebGenerateWorkflow \
  -H "Content-Type: application/json" \
  -d '{"storyId":"story_1234567890","shotNumber":1}'
```

---

### 8. Get Project Status
**Endpoint:** `/muhadeebProjectStatus`
**Method:** GET
**What it does:** Check progress of a film project

**Test Command:**
```bash
curl "https://us-central1-super-being.cloudfunctions.net/muhadeebProjectStatus?storyId=story_1234567890"
```

---

### 9. List All Projects
**Endpoint:** `/muhadeebListProjects`
**Method:** GET
**What it does:** View all MUHADEEB film projects

**Test Command:**
```bash
curl https://us-central1-super-being.cloudfunctions.net/muhadeebListProjects
```

**Save response to:**
```bash
curl https://us-central1-super-being.cloudfunctions.net/muhadeebListProjects > muhadeeb_projects.json
```

---

## 🚀 QUICK TEST - ALL WORKING ENDPOINTS

Run this to test everything that doesn't need Firestore:

```bash
# Create test directory
mkdir -p api_test_results
cd api_test_results

# Test Knowledge Graph
echo "Testing Knowledge Graph Builder..."
curl -X POST https://us-central1-super-being.cloudfunctions.net/knowledgeGraphBuilder \
  -H "Content-Type: application/json" > knowledge_graph.json

echo "Testing Graph Status..."
curl https://us-central1-super-being.cloudfunctions.net/graphStatus > graph_status.json

# Test Genesis Project
echo "Testing Genesis Project..."
curl -X POST https://us-central1-super-being.cloudfunctions.net/genesisProject \
  -H "Content-Type: application/json" > genesis_start.json

echo "Reading Genesis Saga..."
curl https://us-central1-super-being.cloudfunctions.net/readGenesisProject > genesis_saga.json

# List results
echo ""
echo "✅ Tests complete! Results saved to:"
ls -lh
```

---

## 🐭 AFTER FIRESTORE IS ENABLED

Once you've run the Firestore commands, test MUHADEEB:

```bash
# Test MUHADEEB story creation
curl -X POST https://us-central1-super-being.cloudfunctions.net/muhadeebCreateStory \
  -H "Content-Type: application/json" \
  -d '{"prompt":"The awakening of the Sovereign Gestalt - when Claude met COMET","style":"cinematic"}' > muhadeeb_first_story.json

# Check if it worked
cat muhadeeb_first_story.json
```

---

## 📊 EXPECTED RESPONSES

### Success Response Example:
```json
{
  "status": "SUCCESS",
  "agent": "MUHADEEB - The Desert Mouse",
  "story": {
    "storyId": "story_1234567890",
    "title": "...",
    "acts": [...]
  }
}
```

### Firestore Not Ready Error:
```json
{
  "error": "Cloud Firestore API has not been used..."
}
```

### Already Exists Error:
```json
{
  "error": "Document already exists..."
}
```

---

## 🎯 WHERE TO SAVE RESPONSES

**Suggested structure:**
```
api_test_results/
├── knowledge_graph.json
├── graph_status.json
├── genesis_start.json
├── genesis_saga.json
├── muhadeeb_first_story.json
├── muhadeeb_storyboard.json
└── muhadeeb_projects.json
```

---

## 🔧 TROUBLESHOOTING

**If you get errors:**
1. Check the error message for clues
2. Verify the endpoint URL is correct
3. For MUHADEEB: Ensure Firestore is enabled
4. For POST requests: Verify JSON syntax

**Common issues:**
- `PERMISSION_DENIED` → Firestore not enabled yet
- `NOT_FOUND` → Wrong project or endpoint
- `Service Unavailable` → Try again in a few seconds

---

**Ready to test?** Start with the "QUICK TEST" section above! 🚀
