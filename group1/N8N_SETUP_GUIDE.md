# n8n Webhook Setup Guide for Startup Evaluator

This guide will help you set up an n8n workflow to handle startup idea analysis requests from the Startup Evaluator app.

## Prerequisites

- n8n instance (cloud or self-hosted)
- AI service access (OpenAI, Anthropic, or similar)
- Basic knowledge of n8n workflows

## Workflow Setup

### Step 1: Create Webhook Trigger

1. Create a new workflow in n8n
2. Add a **Webhook** node as the trigger
3. Configure the webhook:
   - **HTTP Method**: POST
   - **Path**: `/startup-analysis` (or your preferred path)
   - **Response Mode**: Respond to Webhook
   - **Response Code**: 200

### Step 2: Expected Input Format

The webhook will receive a JSON payload with this structure:
```json
{
  "idea": "Your startup idea description here...",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Step 3: AI Analysis Node

Add an AI node (e.g., **OpenAI** or **Anthropic**) with the following prompt:

```
Analyze the following startup idea and provide a comprehensive evaluation:

Startup Idea: {{ $json.idea }}

Please provide your analysis in the following JSON format:

{
  "summary": "A brief 2-3 sentence summary of the startup idea and its core value proposition",
  "market_potential": "Detailed analysis of market size, target audience, competition, and growth opportunities (3-4 sentences)",
  "key_risks": "Main challenges, obstacles, and risks the startup might face (3-4 sentences)",
  "suggestions": "Specific actionable recommendations for improving the idea and execution (3-4 sentences)",
  "final_verdict": "Overall assessment - choose one: 'Promising idea with high potential', 'Promising idea with potential - Needs validation and refinement', 'Needs significant work and validation', or 'High risk - consider pivoting'",
  "validation_strategy": "Specific steps to validate this business idea in the market (3-4 sentences)"
}

Ensure the response is valid JSON and includes all required fields.
```

### Step 4: Response Processing

Add a **Code** node to clean and validate the AI response:

```javascript
// Get the AI response
const aiResponse = $input.first().json.message || $input.first().json.text || $input.first().json.choices[0].message.content;

try {
  // Parse the JSON response from AI
  let analysisData;
  
  // Handle different AI response formats
  if (typeof aiResponse === 'string') {
    // Extract JSON from markdown code blocks if present
    const jsonMatch = aiResponse.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
    const jsonString = jsonMatch ? jsonMatch[1] : aiResponse;
    analysisData = JSON.parse(jsonString);
  } else {
    analysisData = aiResponse;
  }

  // Validate required fields
  const requiredFields = ['summary', 'market_potential', 'key_risks', 'suggestions', 'final_verdict', 'validation_strategy'];
  const missingFields = requiredFields.filter(field => !analysisData[field]);
  
  if (missingFields.length > 0) {
    throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
  }

  // Clean and truncate text fields if necessary
  Object.keys(analysisData).forEach(key => {
    if (typeof analysisData[key] === 'string') {
      analysisData[key] = analysisData[key].trim();
      // Limit text length to prevent overly long responses
      if (key !== 'final_verdict' && analysisData[key].length > 1000) {
        analysisData[key] = analysisData[key].substring(0, 997) + '...';
      }
    }
  });

  return [{
    json: {
      ...analysisData,
      timestamp: new Date().toISOString(),
      status: 'success'
    }
  }];

} catch (error) {
  // Return error response
  return [{
    json: {
      error: 'Failed to process analysis',
      message: error.message,
      timestamp: new Date().toISOString(),
      status: 'error'
    }
  }];
}
```

### Step 5: Error Handling

Add a **Respond to Webhook** node with:

```javascript
// Check if there's an error in the previous response
const data = $input.first().json;

if (data.status === 'error') {
  $respondWith.status(500).json({
    error: data.error,
    message: data.message,
    timestamp: data.timestamp
  });
} else {
  // Remove internal fields before sending response
  const { status, timestamp, ...cleanResponse } = data;
  $respondWith.status(200).json(cleanResponse);
}
```

## Configuration Steps

### 1. Update Environment Variables

In your React app's `.env` file:

```env
# Replace with your actual n8n webhook URL
REACT_APP_N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/startup-analysis

# Set to false to use real webhook (not demo mode)
REACT_APP_DEMO_MODE=false
```

### 2. Test the Webhook

Before connecting the app, test your webhook:

```bash
curl -X POST https://ireinstark.app.n8n.cloud/webhook-test/startup-evaluator \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "An AI-powered app that helps people find the perfect pet based on their lifestyle",
    "timestamp": "2024-01-15T10:30:00.000Z"
  }'
```

Expected response format:
```json
{
  "summary": "...",
  "market_potential": "...",
  "key_risks": "...",
  "suggestions": "...",
  "final_verdict": "Promising idea with potential - Needs validation and refinement",
  "validation_strategy": "..."
}
```

## Security Considerations

### 1. Rate Limiting
Add rate limiting to prevent abuse:
- Use n8n's built-in rate limiting
- Implement IP-based restrictions if needed

### 2. Input Validation
Add validation to prevent malicious inputs:
- Limit idea text length (e.g., max 5000 characters)
- Sanitize input text
- Validate timestamp format

### 3. API Key Security
- Store AI service API keys securely in n8n credentials
- Use environment variables for sensitive data
- Rotate API keys regularly

## Troubleshooting

### Common Issues

1. **Webhook not responding**
   - Check n8n workflow is active
   - Verify webhook URL is correct
   - Check n8n logs for errors

2. **Invalid JSON response**
   - Review AI prompt for JSON format requirements
   - Add better error handling in Code node
   - Check AI service response format

3. **Missing fields in response**
   - Update AI prompt to be more specific
   - Add field validation in Code node
   - Provide fallback values for missing fields

4. **Timeout errors**
   - Increase webhook timeout settings
   - Optimize AI prompt for faster responses
   - Add retry logic if needed

### Debugging Tips

- Enable n8n workflow logging
- Test each node individually
- Use n8n's manual execution for debugging
- Check browser network tab for request/response details

## Production Deployment

### 1. Performance Optimization
- Use webhook queues for high traffic
- Implement caching for common requests
- Monitor response times

### 2. Monitoring
- Set up n8n workflow monitoring
- Track success/error rates
- Monitor AI service usage and costs

### 3. Backup
- Export n8n workflow regularly
- Document any custom modifications
- Keep track of AI prompt versions

## Sample Workflow JSON

For a complete working example, you can import this basic workflow structure into n8n:

```json
{
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "startup-analysis",
        "responseMode": "responseNode"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "parameters": {
        "model": "gpt-4",
        "messages": {
          "messages": [
            {
              "role": "user",
              "message": "=Analyze this startup idea and return JSON: {{ $json.idea }}"
            }
          ]
        }
      },
      "name": "OpenAI",
      "type": "@n8n/n8n-nodes-langchain.openAi"
    },
    {
      "parameters": {
        "jsCode": "// Process and validate AI response (see code above)"
      },
      "name": "Process Response",
      "type": "n8n-nodes-base.code"
    },
    {
      "parameters": {
        "respondWith": "={{ $json }}"
      },
      "name": "Respond to Webhook",
      "type": "n8n-nodes-base.respondToWebhook"
    }
  ]
}
```

## Support

If you encounter issues:
1. Check the n8n documentation
2. Review the app's error messages in browser console
3. Test the webhook endpoint directly
4. Verify all required fields are returned

Happy analyzing! 🚀