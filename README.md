Smart Email Generator
A Flask-based web application that uses AI to generate and improve professional emails. Built with Mistral API for intelligent email composition and enhancement.
-> Features
Email Generation: Create emails from simple descriptions
Email Improvement: Enhance existing email drafts
Tone Control: Choose between professional and friendly tones
Length Options: Short, medium, or long email formats
Email History: Track and view previously generated emails
Modern UI: Responsive design with Bootstrap and custom styling
Copy to Clipboard: Easy copying of generated emails

Prerequisites
Python 
Mistral API key 

Installation
Install dependencies
bashpip install -r requirements.txt

Set up environment variables
Create a .env file in the root directory
echo "MISTRAL_API_KEY=your-mistral-api-key-here" > .env

Run the application
python app.py

Open your browser
Navigate to http://localhost:5000

Usage
Generating New Emails

Select "Generate New Email" mode
Describe what you want to communicate
Choose tone (Professional/Friendly)
Select length (Short/Medium/Long)
Click "Generate Email"

Improving Email Drafts

Select "Improve Email Draft" mode
Paste your existing email draft
Choose desired tone and length
Click "Improve Email"

Example Descriptions

"Follow up with client about project timeline"
"Thank team for completing the quarterly report"
"Request vacation time for next month"
"Introduce new team member to the department"