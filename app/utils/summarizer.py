# app/utils/summarizer.py

import os
import re
import tempfile
import yt_dlp
import nltk
from collections import defaultdict
from transformers import pipeline
from .advanced_summarizer import create_professional_summary

def download_nltk_data():
    """Checks for and downloads NLTK data if missing."""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)

def get_transcript(youtube_url):
    """Fetches a transcript using yt-dlp and returns it."""
    ydl_opts = {
        'writesubtitles': True, 'writeautomaticsub': True,
        'subtitleslangs': ['en'], 'skip_download': True,
        'quiet': True, 'no_warnings': True,
    }
    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_opts['outtmpl'] = os.path.join(temp_dir, 'subtitle')
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if not info.get('subtitles') and not info.get('automatic_captions'):
                raise Exception("No English captions found.")
            
            ydl.download([youtube_url])
            subtitle_file = None
            for file in os.listdir(temp_dir):
                if file.endswith(('.en.vtt', '.en.srt')):
                    subtitle_file = os.path.join(temp_dir, file)
                    break
            
            if not subtitle_file:
                raise Exception("Could not find downloaded subtitle file.")
            
            with open(subtitle_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return parse_subtitle_content(content)

def parse_subtitle_content(content):
    """Parses subtitle content to clean text."""
    lines = content.split('\n')
    text_lines = []
    for line in lines:
        line = line.strip()
        if line and '-->' not in line and not line.isdigit() and not line.startswith('WEBVTT'):
            clean_line = re.sub(r'<[^>]+>', '', line)
            text_lines.append(clean_line)
    return ' '.join(text_lines)

def extract_video_info(youtube_url):
    """Extract video title and channel name from YouTube URL."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if info:
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'channel': info.get('uploader', 'Unknown Channel'),
                    'description': info.get('description', '')
                }
            else:
                return {'title': 'Unknown Title', 'channel': 'Unknown Channel', 'description': ''}
    except Exception as e:
        print(f"Error extracting video info: {e}")
        return {'title': 'Unknown Title', 'channel': 'Unknown Channel', 'description': ''}

def create_enhanced_summary(transcript, video_info):
    """Create a detailed, formatted summary similar to the example provided."""

    # Use T5 model for simplicity and reliability
    try:
        summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base", framework="pt")

        # Truncate transcript if too long
        max_length = 1000
        truncated_transcript = transcript[:max_length] if len(transcript) > max_length else transcript

        # Generate summary
        result = summarizer('summarize: ' + truncated_transcript, max_length=200, min_length=50, do_sample=False)

        # Extract summary text safely
        if isinstance(result, list) and len(result) > 0:
            summary_dict = result[0]
            if isinstance(summary_dict, dict) and 'summary_text' in summary_dict:
                combined_summary = summary_dict['summary_text']
            else:
                combined_summary = "Summary not available."
        else:
            combined_summary = "Summary not available."

    except Exception as e:
        print(f"Error in summarization: {e}")
        combined_summary = "Summary not available."

    # Extract key points and topics
    key_points = extract_key_points(transcript)

    # Format the enhanced summary
    formatted_summary = format_summary(video_info, combined_summary, key_points)

    return formatted_summary

def extract_key_points(transcript):
    """Extract key points, tips, or items mentioned in the transcript."""
    # Look for numbered lists, bullet points, or repeated patterns
    sentences = nltk.sent_tokenize(transcript)

    key_points = []

    # Look for sentences that might contain key information
    for sentence in sentences:
        sentence_lower = sentence.lower()

        # Look for tool names, specific items, or actionable content
        if any(keyword in sentence_lower for keyword in [
            'tool', 'app', 'software', 'platform', 'service',
            'first', 'second', 'third', 'fourth', 'fifth',
            'number one', 'number two', 'number three',
            'tip', 'technique', 'method', 'way to',
            'best', 'top', 'recommended', 'effective',
            'important', 'key', 'main', 'feature',
            'allows you', 'helps you', 'enables you',
            'perfect for', 'great for', 'ideal for'
        ]):
            # Clean and add the sentence
            clean_sentence = sentence.strip()
            # Filter for meaningful sentences
            if (len(clean_sentence) > 30 and len(clean_sentence) < 150 and
                not clean_sentence.startswith('so ') and
                not clean_sentence.startswith('and ') and
                '.' in clean_sentence):
                key_points.append(clean_sentence)

    # Remove duplicates while preserving order
    seen = set()
    unique_points = []
    for point in key_points:
        if point not in seen:
            seen.add(point)
            unique_points.append(point)

    return unique_points[:8]  # Limit to top 8 points

def format_summary(video_info, summary, key_points):
    """Format the summary in the style of the example provided."""

    # Determine appropriate emoji based on content
    emoji = get_content_emoji(summary + " " + " ".join(key_points))

    # Create the formatted summary
    formatted = f'{emoji} The video "{video_info["title"]}" by {video_info["channel"]} '

    # Add the main summary with better formatting
    formatted += f"explores {summary.lower()}\n\n"

    # Add key points if available
    if key_points and len(key_points) > 0:
        formatted += "Here's a quick breakdown of the key points:\n\n"

        for point in key_points[:6]:  # Limit to 6 points for better readability
            # Extract the main concept from each point
            main_concept = extract_main_concept(point)
            if main_concept and len(main_concept.strip()) > 5:  # Only add meaningful points
                formatted += f"• {main_concept}\n\n"

    # Add a concluding statement based on content
    if 'tool' in summary.lower() or 'app' in summary.lower():
        formatted += "The video provides practical recommendations for tools and applications that can enhance productivity and workflow."
    elif 'tutorial' in summary.lower() or 'how to' in summary.lower():
        formatted += "The video offers step-by-step guidance and practical tips for viewers to implement."
    else:
        formatted += "The video emphasizes practical application and provides valuable insights for viewers interested in the topic."

    return formatted

def get_content_emoji(text):
    """Determine appropriate emoji based on content."""
    text_lower = text.lower()

    # Fishing/outdoor content
    if any(word in text_lower for word in ['fish', 'fishing', 'bass', 'bait', 'lure', 'rod', 'reel']):
        return '🎣'

    # Cooking/food content
    elif any(word in text_lower for word in ['cook', 'recipe', 'food', 'kitchen', 'meal']):
        return '👨‍🍳'

    # Technology content
    elif any(word in text_lower for word in ['tech', 'software', 'app', 'computer', 'digital']):
        return '💻'

    # Education/tutorial content
    elif any(word in text_lower for word in ['learn', 'tutorial', 'guide', 'how to', 'teach']):
        return '📚'

    # Business/finance content
    elif any(word in text_lower for word in ['business', 'money', 'invest', 'finance', 'market']):
        return '💼'

    # Fitness/health content
    elif any(word in text_lower for word in ['workout', 'fitness', 'health', 'exercise', 'gym']):
        return '💪'

    # Travel content
    elif any(word in text_lower for word in ['travel', 'trip', 'vacation', 'destination']):
        return '✈️'

    # Default
    else:
        return '🎥'

def extract_main_concept(sentence):
    """Extract the main concept or action from a sentence."""
    # Simple extraction - look for key nouns and verbs
    words = sentence.split()

    # Remove common starting words
    while words and words[0].lower() in ['the', 'a', 'an', 'this', 'that', 'these', 'those', 'and', 'but', 'or']:
        words.pop(0)

    # Take first meaningful part of the sentence
    if len(words) > 8:
        return " ".join(words[:8]) + "..."
    else:
        return " ".join(words)

def run_summarization(transcript, video_info=None):
    """Takes a transcript and returns an enhanced summary and keywords."""
    try:
        # Use provided video_info or create a default one
        if video_info is None:
            video_info = {
                'title': 'Video Summary',
                'channel': 'Content Creator',
                'description': ''
            }

        # Create enhanced summary using the advanced summarizer
        enhanced_summary = create_professional_summary(transcript, video_info)

        # Extract keywords (keep the existing logic)
        stop_words = set(nltk.corpus.stopwords.words('english'))
        words = nltk.tokenize.word_tokenize(transcript.lower())
        filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
        freq = defaultdict(int)
        for word in filtered_words:
            freq[word] += 1
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, _ in sorted_keywords[:10]]

        return enhanced_summary, ", ".join(keywords)

    except Exception as e:
        print(f"Error in enhanced summarization: {e}")
        # Fallback to simple summarization
        try:
            summarizer = pipeline("summarization", model="t5-base", tokenizer="t5-base", framework="pt")
            result = summarizer('summarize: ' + transcript[:1000], max_length=150, min_length=30, do_sample=False)

            # Extract summary text safely
            if isinstance(result, list) and len(result) > 0:
                summary_dict = result[0]
                if isinstance(summary_dict, dict) and 'summary_text' in summary_dict:
                    summary = summary_dict['summary_text']
                else:
                    summary = "Summary not available."
            else:
                summary = "Summary not available."
        except Exception as e2:
            print(f"Error in fallback summarization: {e2}")
            summary = "Summary not available."

        # Keyword Extraction
        stop_words = set(nltk.corpus.stopwords.words('english'))
        words = nltk.tokenize.word_tokenize(transcript.lower())
        filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
        freq = defaultdict(int)
        for word in filtered_words:
            freq[word] += 1
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, _ in sorted_keywords[:10]]

        return summary, ", ".join(keywords)

# Ensure NLTK data is ready when the app starts
download_nltk_data()