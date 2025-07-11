# app/routes.py

from flask import render_template, request, jsonify
from app import app
from app.utils.summarizer import get_transcript, run_summarization, extract_video_info

@app.route('/')
@app.route('/index')
def index():
    # This route just shows the main page
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    # This route handles the summarization request
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required.'}), 400

        # Extract video information
        video_info = extract_video_info(url)

        # Run the backend processing
        transcript = get_transcript(url)
        summary, keywords = run_summarization(transcript, video_info)

        # Return the results as JSON
        return jsonify({'summary': summary, 'keywords': keywords})

    except Exception as e:
        # Return any errors as JSON
        return jsonify({'error': str(e)}), 500