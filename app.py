import os
from flask import Flask, render_template, request
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Configure logging
if not app.debug:
    file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('App startup')

@app.route('/')
def home():
    app.logger.info('Home page accessed')
    return render_template('index.html')

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error('404 error occurred')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error('500 error occurred', exc_info=True)
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
