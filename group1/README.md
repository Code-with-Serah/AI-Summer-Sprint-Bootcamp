
# Startup Evaluator

A modern, responsive web app for validating startup ideas with instant AI-powered insights. Built for founders, students, and innovators who want fast, actionable feedback.

## Features
- **Landing Page**: Marketing-focused, explains the product, shows sample analysis, and encourages users to try the app.
- **Web App**: Lets users input their startup idea and receive a detailed analysis (market potential, risks, suggestions, validation strategy, and verdict).
- **Navigation**: Simple navigation between the landing page and the analysis app.
- **Responsive Design**: Mobile-first, works beautifully on all devices.

## Project Structure
- `src/` — Standard React app entry (index.js, index.css, etc.)
- `startup_evaluator.tsx` — Main app logic, contains both the landing page and the analyzer app components.
- `public/` — Static assets.
- `tailwind.config.js` — Tailwind CSS configuration for utility-first styling.

## How It Works
- **Landing Page**: 
  - Hero section with call-to-action.
  - "How It Works" steps.
  - Sample analysis (accordion style for details).
  - Social proof and testimonials.
  - Final call-to-action.
- **Analyzer App**:
  - Users describe their idea in a text area.
  - Click "Get AI Analysis" to receive instant feedback (demo logic, can be connected to real AI backend).
  - Results are shown in a clear, sectioned report.
  - Users can analyze another idea or return to the landing page.

## Code Overview
- **startup_evaluator.tsx**
  - `LandingPage` component: Handles all landing/marketing content and navigation to the app.
  - `AnalyzerApp` component: Handles idea input, analysis logic, and displaying results.
  - `App` component: Controls which view is shown (landing or app) using React state.
- **Styling**: Uses Tailwind CSS for all layout and responsive design. Utility classes ensure mobile, tablet, and desktop support.

## How to Run/Modify
1. Install dependencies: `npm install`
2. Start the app: `npm start` (runs on http://localhost:3000)
3. To modify the landing page or app, edit `startup_evaluator.tsx`.
4. For global styles, use `src/index.css` and Tailwind utilities.

## Customization
- To connect to a real AI backend, replace the demo analysis logic in `AnalyzerApp` with an API call.
- To change the landing page content, edit the relevant sections in `LandingPage`.
- To adjust styling, use Tailwind classes or update the Tailwind config.

## Responsive Design
- The layout uses Tailwind's responsive utilities (`md:`, `lg:`, etc.) to ensure all sections adapt to different screen sizes.
- Test on mobile and desktop for best results.

## License
MIT. Use and modify freely for your own startup projects!
=======
# Startup Evaluator 🚀

A responsive React web application that helps entrepreneurs validate their startup ideas using AI-powered analysis.

![Startup Evaluator](https://img.shields.io/badge/React-18.2.0-blue)
![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4.17-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- **🤖 AI-Powered Analysis**: Real AI analysis via n8n webhooks (OpenAI, Anthropic, etc.)
- **📱 Fully Responsive**: Works seamlessly on mobile, tablet, and desktop devices
- **🎨 Modern UI**: Clean, professional design with smooth animations
- **🚀 Fast & Lightweight**: Built with React and optimized for performance
- **🔧 Configurable**: Easy webhook setup with environment variables
- **🎯 Demo Mode**: Fallback demo mode for testing and development

## 🎬 Live Demo

The app includes:
- **Landing Page**: Professional marketing page with features overview
- **Analyzer Tool**: Interactive startup idea evaluation interface
- **Detailed Analysis**: Comprehensive reports with actionable insights

## 🛠️ Quick Start

```bash
# Install dependencies
npm install

# Configure environment (copy and edit .env file)
cp .env .env.local
# Edit .env.local with your n8n webhook URL

# Start development server
npm start

# Build for production
npm run build
```

The app will be available at `http://localhost:3000`

### 🔧 Configuration

1. **Set up n8n webhook** - Follow [`N8N_SETUP_GUIDE.md`](./N8N_SETUP_GUIDE.md)
2. **Configure environment variables** in `.env.local`:
   ```env
   REACT_APP_N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/startup-analysis
   REACT_APP_DEMO_MODE=false
   ```

## 📋 What You Get

### Analysis Categories
1. **📈 Market Potential** - Growth opportunities and competition analysis
2. **⚠️ Key Risks** - Potential challenges and obstacles
3. **💡 Improvement Suggestions** - Actionable recommendations
4. **🎯 Validation Strategy** - Steps to validate your business idea
5. **✅ Final Verdict** - Color-coded overall assessment

### Responsive Design
- **Mobile First**: Optimized for smartphones and tablets
- **Desktop Enhanced**: Full-featured experience on larger screens
- **Touch Friendly**: Intuitive gestures and interactions

## 🏗️ Tech Stack

- **Frontend**: React 18+ with functional components and hooks
- **Styling**: Tailwind CSS for responsive design
- **Icons**: Lucide React icon library
- **Build Tool**: Create React App
- **State Management**: React useState hooks

## 📚 Documentation

For detailed documentation including:
- Complete feature breakdown
- Architecture overview
- Customization guide
- Deployment instructions

See: [`DOCUMENTATION.md`](./DOCUMENTATION.md)

## 🚀 Deployment

Ready to deploy to:
- Netlify
- Vercel
- AWS S3/CloudFront
- GitHub Pages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple devices
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🌟 Key Highlights

- **Zero Dependencies**: No complex backend required
- **SEO Friendly**: Semantic HTML structure
- **Accessibility**: WCAG compliant design
- **Performance**: Optimized for fast loading
- **Scalable**: Easy to extend and customize

---

**Getting Started**: Run `npm start` and visit the landing page to explore all features!

