# app/utils/advanced_summarizer.py

import re
import nltk
from collections import defaultdict
from transformers import pipeline

def create_professional_summary(transcript, video_info):
    """Create a professional, detailed summary similar to the fishing example."""
    
    # Extract the main topic and key elements
    main_topic = extract_main_topic(transcript, video_info['title'])
    
    # Get structured content
    key_items = extract_structured_items(transcript)
    
    # Generate the opening line
    emoji = get_topic_emoji(video_info['title'] + " " + transcript[:500])
    opening = f'{emoji} The video "{video_info["title"]}" by {video_info["channel"]} '
    
    # Create context-aware description
    if 'tool' in video_info['title'].lower() or 'app' in video_info['title'].lower():
        opening += f"explores the most effective {main_topic} for enhancing productivity and workflow. "
    elif 'tip' in video_info['title'].lower() or 'guide' in video_info['title'].lower():
        opening += f"provides comprehensive guidance on {main_topic}. "
    else:
        opening += f"dives into {main_topic}. "
    
    # Add context from transcript analysis
    context = analyze_content_context(transcript)
    opening += context + "\n\n"
    
    # Add structured breakdown
    if key_items:
        opening += "Here's a quick breakdown of the featured items:\n\n"
        for item in key_items[:8]:
            opening += f"{item}\n\n"
    
    # Add concluding insight
    conclusion = generate_conclusion(transcript, video_info)
    opening += conclusion
    
    return opening

def extract_main_topic(transcript, title):
    """Extract the main topic from title and transcript."""
    # Clean the title to get the core topic
    title_lower = title.lower()
    transcript_lower = transcript.lower()

    # Fishing and outdoor content
    if any(word in title_lower for word in ['fishing', 'bass', 'lure', 'bait', 'tackle', 'rod', 'reel']):
        if 'challenge' in title_lower or 'vs' in title_lower:
            return "fishing challenges and gear comparisons"
        elif 'budget' in title_lower:
            return "budget fishing gear and strategies"
        else:
            return "fishing techniques and equipment"

    # Technology and tools
    elif 'tool' in title_lower:
        return "tools and applications"
    elif 'tip' in title_lower:
        return "tips and techniques"
    elif 'guide' in title_lower or 'how to' in title_lower:
        return "methods and strategies"
    elif 'review' in title_lower:
        return "product reviews and recommendations"
    else:
        # Extract from transcript with better categorization
        if any(word in transcript_lower for word in ['fish', 'fishing', 'bass', 'lure', 'bait', 'tackle']):
            return "fishing strategies and related concepts"
        elif any(word in transcript_lower for word in ['technique', 'method', 'strategy', 'approach']):
            return "strategies and related concepts"  # Fixed typo
        elif any(word in transcript_lower for word in ['tool', 'app', 'software']):
            return "tools and related concepts"
        else:
            return "key concepts and insights"

def extract_structured_items(transcript):
    """Extract structured items like tools, tips, or techniques."""
    sentences = nltk.sent_tokenize(transcript)
    items = []
    seen_concepts = set()

    # Look for patterns that indicate structured content
    for sentence in sentences:
        sentence_clean = sentence.strip()
        sentence_lower = sentence_clean.lower()

        # Skip very short or very long sentences
        if len(sentence_clean) < 30 or len(sentence_clean) > 150:
            continue

        # Skip sentences that are too repetitive or fragmented
        if sentence_clean.count(' ') < 4:  # Too few words
            continue

        # Look for meaningful content patterns
        meaningful_patterns = [
            # Fishing-specific patterns
            'lure', 'bait', 'tackle', 'rod', 'reel', 'hook', 'line',
            'cast', 'catch', 'fish', 'bass', 'weight', 'jig',
            # General item patterns
            'is called', 'tool called', 'app called', 'feature called',
            'first', 'second', 'third', 'next',
            'allows you to', 'helps you', 'enables you to',
            'perfect for', 'great for', 'ideal for', 'best for',
            'you can use', 'you can do', 'it can',
            'main feature', 'key feature', 'important feature',
            'recommend', 'suggest', 'works well'
        ]

        if any(pattern in sentence_lower for pattern in meaningful_patterns):
            # Extract the key concept
            concept = extract_concept_from_sentence(sentence_clean)
            if concept and len(concept) > 15:
                # Check for duplicates or very similar concepts
                concept_key = concept.lower()[:30]  # Use first 30 chars for similarity check
                if concept_key not in seen_concepts and concept.strip():
                    # Additional quality check - ensure concept is meaningful
                    if (len(concept.split()) >= 4 and
                        not concept.lower().startswith(('and', 'or', 'but', 'so'))):
                        seen_concepts.add(concept_key)
                        items.append(f"• {concept}")

    # Return top unique items
    return items[:6]  # Reduced to 6 for better quality

def extract_concept_from_sentence(sentence):
    """Extract the main concept from a sentence."""
    # Remove common starting phrases
    pattern = r'^(so|and|but|the|this|that|it|you can|this is|this tool|the tool)\s+'
    sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE)

    # Remove repetitive phrases that appear in fishing transcripts
    repetitive_patterns = [
        r'\b(can throw it|throw it|it can|it\'s|that\'s)\b',
        r'\b(perfect for|great for)\s+\w+\s+and\s+(perfect for|great for)',
        r'\b(weightless|weight)\s+\w*\s*(weightless|weight)',
        r'\b(we can|we)\s+(throw it|use it|do it)\b',
        r'\b(and|or)\s+(we can|it can|they can)\b',
    ]

    for pattern in repetitive_patterns:
        sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE)

    # Clean up extra spaces and incomplete sentences
    sentence = re.sub(r'\s+', ' ', sentence).strip()

    # Skip if sentence is too fragmented after cleaning
    if len(sentence.split()) < 5:
        return ""

    # Look for tool names or key concepts
    # If sentence mentions a specific name, extract it
    if ':' in sentence:
        parts = sentence.split(':')
        if len(parts) >= 2:
            name = parts[0].strip()
            description = parts[1].strip()
            return f"{name}: {description[:60]}..."

    # Otherwise, take the first meaningful part
    words = sentence.split()
    if len(words) > 12:
        return ' '.join(words[:12]) + "..."
    else:
        return sentence

def analyze_content_context(transcript):
    """Analyze the transcript to provide context."""
    transcript_lower = transcript.lower()

    # Count mentions of different themes
    themes = {
        'fishing': [
            'fish', 'fishing', 'bass', 'lure', 'bait', 'tackle',
            'rod', 'reel', 'catch', 'angler'
        ],
        'outdoor': [
            'outdoor', 'nature', 'hunting', 'camping',
            'wilderness', 'adventure'
        ],
        'productivity': [
            'productive', 'efficiency', 'workflow', 'organize', 'manage'
        ],
        'learning': [
            'learn', 'study', 'education', 'knowledge', 'understand'
        ],
        'technology': [
            'ai', 'artificial intelligence', 'software', 'digital', 'tech'
        ],
        'business': [
            'business', 'entrepreneur', 'money', 'income', 'profit'
        ],
        'creative': [
            'creative', 'design', 'content', 'video', 'create'
        ]
    }

    theme_scores = {}
    for theme, keywords in themes.items():
        score = sum(transcript_lower.count(keyword) for keyword in keywords)
        theme_scores[theme] = score

    # Get the dominant theme
    dominant_theme = max(theme_scores, key=theme_scores.get)

    # Generate context based on dominant theme
    if dominant_theme == 'fishing':
        if ('budget' in transcript_lower or 'cheap' in transcript_lower or
            'walmart' in transcript_lower):
            return ("Comparing budget-friendly fishing gear options, the presenter "
                   "tests affordable equipment to help anglers make informed "
                   "purchasing decisions.")
        elif 'challenge' in transcript_lower or 'vs' in transcript_lower:
            return ("Through hands-on testing and comparison, the presenter "
                   "evaluates different fishing approaches and equipment to "
                   "determine what works best.")
        else:
            return ("Sharing practical fishing knowledge and gear insights, "
                   "the presenter helps anglers improve their techniques and "
                   "equipment choices.")
    elif dominant_theme == 'outdoor':
        return ("Exploring outdoor activities and gear, the presenter shares "
               "practical advice for outdoor enthusiasts.")
    elif dominant_theme == 'productivity':
        return ("As productivity becomes increasingly important, the presenter "
               "highlights tools that can streamline workflows and boost efficiency.")
    elif dominant_theme == 'learning':
        return ("With the growing need for continuous learning, these "
               "recommendations focus on tools that enhance knowledge "
               "acquisition and retention.")
    elif dominant_theme == 'technology':
        return ("In today's digital landscape, the presenter showcases "
               "cutting-edge technologies that are reshaping how we work and create.")
    elif dominant_theme == 'business':
        return ("For entrepreneurs and business professionals, these tools "
               "offer practical solutions for growth and success.")
    else:
        return ("The presenter shares valuable insights and practical "
               "recommendations for viewers looking to improve their approach.")

def generate_conclusion(transcript, video_info):
    """Generate a contextual conclusion."""
    transcript_lower = transcript.lower()
    title_lower = video_info['title'].lower()

    # Fishing-specific conclusions
    if any(word in title_lower for word in ['fishing', 'bass', 'lure', 'bait', 'tackle']):
        if 'budget' in title_lower or 'walmart' in title_lower:
            return ("The video provides practical insights for budget-conscious "
                   "anglers, demonstrating that effective fishing doesn't require "
                   "expensive gear.")
        elif 'challenge' in title_lower or 'vs' in title_lower:
            return ("The video offers valuable comparisons to help anglers make "
                   "informed decisions about their fishing gear and techniques.")
        else:
            return ("The video provides comprehensive insights and practical "
                   "guidance for anglers looking to improve their fishing success.")

    # Technology/tool conclusions
    elif 'tool' in title_lower or 'app' in title_lower:
        if 'beginner' in transcript_lower or 'start' in transcript_lower:
            return ("The video emphasizes choosing the right tools based on your "
                   "experience level and specific needs, making it accessible for "
                   "both beginners and advanced users.")
        else:
            return ("The video emphasizes adapting your tool choice to your "
                   "specific workflow and requirements, ensuring maximum "
                   "productivity and effectiveness.")
    elif 'tip' in title_lower or 'technique' in title_lower:
        return ("The video emphasizes practical application and provides "
               "actionable advice that viewers can implement immediately.")
    else:
        return ("The video provides comprehensive insights and practical "
               "guidance for viewers interested in the topic.")

def get_topic_emoji(text):
    """Get an appropriate emoji based on the content."""
    text_lower = text.lower()

    # Fishing/outdoor content (check first for specificity)
    if any(word in text_lower for word in ['fish', 'fishing', 'bass', 'bait', 'lure']):
        return '🎣'

    # Technology/AI content
    elif any(word in text_lower for word in [
        'ai', 'artificial intelligence', 'tool', 'app', 'software'
    ]):
        return '🤖'

    # Productivity content
    elif any(word in text_lower for word in [
        'productivity', 'workflow', 'organize', 'efficiency'
    ]):
        return '⚡'

    # Learning/Education content
    elif any(word in text_lower for word in [
        'learn', 'study', 'education', 'tutorial', 'guide'
    ]):
        return '📚'

    # Business content
    elif any(word in text_lower for word in [
        'business', 'entrepreneur', 'money', 'income'
    ]):
        return '💼'

    # Creative content
    elif any(word in text_lower for word in [
        'creative', 'design', 'content', 'video'
    ]):
        return '🎨'

    # Default
    else:
        return '🎥'
