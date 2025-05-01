# Libraries

# Standard logging module
import logging

# Flask modules for handling web requests and rendering HTML
from flask import Flask, render_template, request, redirect, url_for

# Logging handler that rotates log files when they reach a certain size
from logging.handlers import RotatingFileHandler

# Logging Format

# Define a simple format for log entries with timestamps
logging_format = logging.Formatter('%(asctime)s %(message)s')

# HTTP Logger

# Create a logger named 'HTTP Logger'
funnel_logger = logging.getLogger('HTTP Logger')
funnel_logger.setLevel(logging.INFO)  # Set logging level to INFO

# Set up a rotating file handler to store logs in 'http_audits.log'
funnel_handler = RotatingFileHandler('http_audits.log', maxBytes=2000, backupCount=5)
funnel_handler.setFormatter(logging_format)  # Apply the logging format
funnel_logger.addHandler(funnel_handler)  # Attach the handler to the logger

# Baseline honeypot function that returns a Flask app

def web_honeypot(input_username="admin", input_password="password"):
    # Create a Flask application instance
    app = Flask(__name__)

    # Define the root route
    @app.route('/')
    def index():
        # Serve the wp-admin.html login page (should be in your templates folder)
        return render_template('wp-admin.html')
    
    # Define the login form handler route
    @app.route('/wp-admin-login', methods=['POST'])
    def login():
        # Extract form input values from the POST request
        username = request.form['username']
        password = request.form['password']

        # Get the client's IP address from the request
        ip_address = request.remote_addr

        # Log the credentials and IP to the funnel logger
        funnel_logger.info(f'Client with IP Address: {ip_address} entered\n Username: {username}, Password: {password}')

        # Basic validation check
        if username == input_username and password == input_password:
            return 'Good Job!'  # Return success message
        else:
            return "Invalid username or password. Please try again."  # Return failure message

    # Return the Flask app object to be run externally
    return app

# Function to run the honeypot web server

def run_web_honeypot(port=5000, input_username="admin", input_password="password"):
    # Generate the web app instance with provided credentials
    run_web_honeypot_app = web_honeypot(input_username, input_password)

    # Start the Flask development server
    run_web_honeypot_app.run(debug=True, port=port, host="0.0.0.0")  # Host "0.0.0.0" binds to all network interfaces

    # Return the app instance (optional, mostly for testing or embedding)
    return run_web_honeypot_app