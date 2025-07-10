from flask import current_app, render_template, request, jsonify
from app.utils.transcript_fetcher import get_video_id, get_transcript
from app.utils.summarizer import summarize_text
from app.utils.keyword_extractor import extract_keywords
from app.utils.youtube_api import get_video_details
from app.utils.web_scraper import scrape_video_description # <-- New import

app = current_app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    video_url = request.form.get('youtube_url')
    video_id = get_video_id(video_url)

    if not video_id:
        return jsonify({'error': "Invalid YouTube URL provided."})

    details = get_video_details(video_id, app.config['YOUTUBE_API_KEY'])
    video_title = details['title'] if details else "Video"
    
    # --- Fallback Logic ---
    text_to_summarize = get_transcript(video_id)
    source = "Transcript"

    if not text_to_summarize:
        print(f"Transcript failed for '{video_title}'. Falling back to description.")
        text_to_summarize = scrape_video_description(video_url)
        source = "Video Description"

    if not text_to_summarize:
        return jsonify({'error': f"Could not retrieve a transcript or description for '{video_title}'."})
    # --- End Fallback Logic ---

    try:
        summary = summarize_text(text_to_summarize)
        keywords = extract_keywords(text_to_summarize)
        
        return jsonify({
            'video_title': f"{video_title} (from {source})", # Clarify the source
            'summary': summary,
            'keywords': keywords
        })
    except Exception as e:
        print(f"Error during processing: {e}")
        return jsonify({'error': "An error occurred while processing the video."})