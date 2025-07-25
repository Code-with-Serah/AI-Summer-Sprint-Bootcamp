from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

from utils.email_generator import EmailGenerator, generate_email, improve_email
from models.database import save_email, get_all_emails

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
# Initialize email generator once
try:
    email_generator = EmailGenerator()
except ValueError as e:
    print(f"Warning: {e}")
    email_generator = None

@app.route('/', methods=['GET'])
def index():
    """Main page with email history"""
    try:
        email_history = get_all_emails()
        return render_template('index.html', emails=email_history)
    except Exception as e:
        flash(f"Error loading emails: {str(e)}", 'error')
        return render_template('index.html', emails=[])

@app.route('/generate', methods=['POST'])
def generate():
    """Generate a new email from description"""
    try:
        # Get form data
        idea = request.form.get('idea', '').strip()
        tone = request.form.get('tone', 'professional')
        length = request.form.get('length', 'medium')
        
        # Validate input
        if not idea:
            flash('Please provide an email description', 'error')
            return redirect('/')
        
        # Generate email
        if email_generator:
            generated = email_generator.generate_email(idea, tone, length)
        else:
            generated = generate_email(idea, tone, length)
        
        # Check for errors in generation
        if generated.startswith('❌ Error'):
            flash(generated, 'error')
            return redirect('/')
        
        # Save to database
        save_email(
            idea=idea,
            tone=tone,
            generated=generated,
            improved=""
        )
        
        flash('Email generated successfully!', 'success')
        
        # Load updated email history
        emails = get_all_emails()
        return render_template('index.html', result=generated, emails=emails)
        
    except Exception as e:
        flash(f'Error generating email: {str(e)}', 'error')
        return redirect('/')

@app.route('/improve', methods=['POST'])
def improve():
    """Improve an existing email draft"""
    try:
        # Get form data
        original_email = request.form.get('original_email', '').strip()
        tone = request.form.get('tone', 'professional')
        length = request.form.get('length', 'medium')
        idea = request.form.get('idea', 'Email improvement')
        
        # Validate input
        if not original_email:
            flash('Please provide an email to improve', 'error')
            return redirect('/')
        
        # Improve email
        if email_generator:
            improved = email_generator.improve_email(original_email, tone, length)
        else:
            improved = improve_email(original_email, tone, length)
        
        # Check for errors in improvement
        if improved.startswith('❌ Error'):
            flash(improved, 'error')
            return redirect('/')
        
        # Save to database
        save_email(
            idea=f'Improved: {idea}',
            tone=tone,
            generated=original_email,
            improved=improved
        )
        
        flash('Email improved successfully!', 'success')
        
        # Load updated email history
        email_history = get_all_emails()
        return render_template('index.html', 
                             emails=email_history, 
                             improved=improved, 
                             original=original_email)
        
    except Exception as e:
        flash(f'Error improving email: {str(e)}', 'error')
        return redirect('/')

@app.route('/history')
def history():
    """View email history"""
    try:
        emails = get_all_emails()
        return render_template('history.html', emails=emails)
    except Exception as e:
        flash(f'Error loading email history: {str(e)}', 'error')
        return redirect('/')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Check if API key is configured
    if not os.getenv('MISTRAL_API_KEY'):
        print("Warning: MISTRAL_API_KEY not found in environment variables")
    
    # Run app
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', 5000))
    )