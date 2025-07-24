#!/bin/bash

echo "🚀 Startup Evaluator - Webhook Configuration"
echo "============================================"
echo ""

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "Creating .env.local file..."
    cp .env .env.local
fi

echo "Please enter your n8n webhook URL:"
echo "Example: https://your-n8n-instance.com/webhook/startup-analysis"
read -p "Webhook URL: " webhook_url

if [ -z "$webhook_url" ]; then
    echo "❌ No URL provided. Using demo mode."
    cat > .env.local << EOF
# Local Environment Configuration
REACT_APP_N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/startup-analysis
REACT_APP_DEMO_MODE=true
EOF
else
    echo "✅ Configuring webhook URL: $webhook_url"
    cat > .env.local << EOF
# Local Environment Configuration
REACT_APP_N8N_WEBHOOK_URL=$webhook_url
REACT_APP_DEMO_MODE=false
EOF
fi

echo ""
echo "✅ Configuration complete!"
echo "📝 Configuration saved to .env.local"
echo ""
echo "Next steps:"
echo "1. Restart your development server: npm start"
echo "2. Test with a startup idea"
echo "3. Check browser console for any errors"
echo ""
echo "🔧 To change configuration later, edit .env.local file"