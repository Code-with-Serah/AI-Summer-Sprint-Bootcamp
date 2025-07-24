#!/usr/bin/env node

// Polyfill fetch for Node.js < 18
if (typeof fetch === 'undefined') {
  try {
    global.fetch = require('node-fetch');
  } catch (e) {
    console.log('❌ This script requires Node.js 18+ or you need to install node-fetch');
    console.log('Install with: npm install node-fetch');
    process.exit(1);
  }
}

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🔧 n8n Webhook Test Tool');
console.log('========================');

rl.question('Enter your n8n webhook URL: ', async (webhookUrl) => {
  console.log('🧪 Testing webhook...');
  
  const testPayload = {
    idea: "A simple test idea for the webhook",
    timestamp: new Date().toISOString()
  };

  console.log('📤 URL:', webhookUrl);
  console.log('📦 Payload:', JSON.stringify(testPayload, null, 2));

  try {
    const response = await fetch(webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testPayload)
    });

    console.log('📥 Response:');
    console.log('  Status:', response.status);
    console.log('  Status Text:', response.statusText);
    console.log('  Headers:', Object.fromEntries(response.headers.entries()));

    // Check if response has content before trying to parse JSON
    const contentLength = response.headers.get('content-length');
    
    if (contentLength === '0' || contentLength === null) {
      console.log('  Body: (empty response)');
      
      if (response.ok) {
        console.log('✅ Webhook test SUCCESSFUL! (Empty response is OK for some workflows)');
      } else {
        console.log('❌ Webhook test FAILED with status:', response.status);
      }
    } else {
      // Try to parse response as text first
      const responseText = await response.text();
      console.log('  Body (raw):', responseText);
      
      // Try to parse as JSON if it looks like JSON
      if (responseText.trim().startsWith('{') || responseText.trim().startsWith('[')) {
        try {
          const responseData = JSON.parse(responseText);
          console.log('  Body (parsed):', JSON.stringify(responseData, null, 2));
        } catch (parseError) {
          console.log('  Body (JSON parse failed):', parseError.message);
        }
      }
      
      if (response.ok) {
        console.log('✅ Webhook test SUCCESSFUL!');
      } else {
        console.log('❌ Webhook test FAILED with status:', response.status);
      }
    }

  } catch (error) {
    console.log('❌ Webhook test FAILED with error:');
    console.log('  Error:', error.message);
  }

  rl.close();
});