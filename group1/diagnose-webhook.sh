#!/bin/bash

echo "🔍 Startup Evaluator - Webhook Diagnostic Tool"
echo "==============================================="
echo ""

# Check environment files
echo "📁 Environment Files:"
echo "--------------------"

if [ -f .env ]; then
    echo "✅ .env exists"
    echo "   REACT_APP_N8N_WEBHOOK_URL=$(grep REACT_APP_N8N_WEBHOOK_URL .env | cut -d'=' -f2)"
    echo "   REACT_APP_DEMO_MODE=$(grep REACT_APP_DEMO_MODE .env | cut -d'=' -f2)"
else
    echo "❌ .env not found"
fi

if [ -f .env.local ]; then
    echo "✅ .env.local exists"
    echo "   REACT_APP_N8N_WEBHOOK_URL=$(grep REACT_APP_N8N_WEBHOOK_URL .env.local | cut -d'=' -f2)"
    echo "   REACT_APP_DEMO_MODE=$(grep REACT_APP_DEMO_MODE .env.local | cut -d'=' -f2)"
else
    echo "❌ .env.local not found"
fi

echo ""

# Check for placeholder URLs
echo "🔍 Checking for placeholder URLs:"
echo "---------------------------------"

if grep -q "your-n8n-instance.com" .env* 2>/dev/null; then
    echo "⚠️  Found placeholder URL 'your-n8n-instance.com' in environment files"
fi

if grep -q "your-actual-n8n-webhook-url.com" .env* 2>/dev/null; then
    echo "⚠️  Found placeholder URL 'your-actual-n8n-webhook-url.com' in environment files"
fi

echo ""

# Check demo mode logic
echo "🎯 Demo Mode Analysis:"
echo "---------------------"

DEMO_MODE_ENV=$(grep REACT_APP_DEMO_MODE .env.local 2>/dev/null | cut -d'=' -f2)
WEBHOOK_URL_ENV=$(grep REACT_APP_N8N_WEBHOOK_URL .env.local 2>/dev/null | cut -d'=' -f2)

if [ "$DEMO_MODE_ENV" = "true" ]; then
    echo "🎯 DEMO_MODE is explicitly set to TRUE"
    echo "   → App will use demo analysis (not webhook)"
elif [ "$DEMO_MODE_ENV" = "false" ]; then
    echo "✅ DEMO_MODE is set to FALSE"
    echo "   → App will attempt to use webhook"
else
    echo "⚠️  DEMO_MODE not set or invalid value: '$DEMO_MODE_ENV'"
    echo "   → App behavior depends on default value"
fi

echo ""

# Check webhook URL
echo "🌐 Webhook URL Analysis:"
echo "-----------------------"

if [ -z "$WEBHOOK_URL_ENV" ]; then
    echo "❌ No webhook URL found in .env.local"
elif [[ "$WEBHOOK_URL_ENV" == *"your-n8n-instance.com"* ]] || [[ "$WEBHOOK_URL_ENV" == *"your-actual-n8n-webhook-url.com"* ]]; then
    echo "❌ Webhook URL is still a placeholder: $WEBHOOK_URL_ENV"
    echo "   → This will trigger 'Webhook URL not configured' error"
elif [[ "$WEBHOOK_URL_ENV" == http* ]]; then
    echo "✅ Valid-looking webhook URL: $WEBHOOK_URL_ENV"
else
    echo "⚠️  Unusual webhook URL format: $WEBHOOK_URL_ENV"
fi

echo ""

# Provide recommendations
echo "💡 Recommendations:"
echo "------------------"

if [ "$DEMO_MODE_ENV" = "true" ]; then
    echo "1. Change REACT_APP_DEMO_MODE=false in .env.local to use webhook"
fi

if [[ "$WEBHOOK_URL_ENV" == *"your-"* ]]; then
    echo "2. Replace placeholder webhook URL with your actual n8n webhook URL"
    echo "   Example: https://your-n8n-instance.app.n8n.cloud/webhook/startup-analysis"
fi

echo "3. After making changes, restart the dev server: npm start"
echo "4. Open browser console to see debug logs when analyzing an idea"
echo "5. Use './test-webhook.js' to test your webhook directly"

echo ""

# Test instructions
echo "🧪 Testing Steps:"
echo "----------------"
echo "1. Fix the webhook URL in .env.local"
echo "2. Set REACT_APP_DEMO_MODE=false"
echo "3. Run: npm start"
echo "4. Open browser console (F12)"
echo "5. Try analyzing a startup idea"
echo "6. Look for these debug messages:"
echo "   - '🚀 Starting analysis...'"
echo "   - '🔗 Using WEBHOOK MODE' (not demo mode)"
echo "   - '📤 Making request to: [your-url]'"
echo "   - '📥 Response status: [status-code]'"

echo ""
echo "🆘 If you need help:"
echo "1. Check browser console for error messages"
echo "2. Verify your n8n workflow is active and working"
echo "3. Test webhook with: node test-webhook.js"