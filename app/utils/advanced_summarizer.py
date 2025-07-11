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
    
    if 'tool' in title_lower:
        return "tools and applications"
    elif 'tip' in title_lower:
        return "tips and techniques"
    elif 'guide' in title_lower or 'how to' in title_lower:
        return "methods and strategies"
    elif 'review' in title_lower:
        return "product reviews and recommendations"
    else:
        # Extract from transcript
        common_topics = ['technique', 'method', 'strategy', 'approach', 'tool', 'tip']
        for topic in common_topics:
            if topic in transcript.lower():
                return f"{topic}s and related concepts"
        return "key concepts and insights"

def extract_structured_items(transcript):
    """Extract structured items like tools, tips, or techniques."""
    sentences = nltk.sent_tokenize(transcript)
    items = []
    
    # Look for patterns that indicate structured content
    for sentence in sentences:
        sentence_clean = sentence.strip()
        sentence_lower = sentence_clean.lower()
        
        # Skip very short or very long sentences
        if len(sentence_clean) < 20 or len(sentence_clean) > 200:
            continue
            
        # Look for tool names, features, or specific items
        if any(pattern in sentence_lower for pattern in [
            'is called', 'tool called', 'app called', 'feature called',
            'first tool', 'second tool', 'third tool', 'next tool',
            'allows you to', 'helps you', 'enables you to',
            'perfect for', 'great for', 'ideal for', 'best for',
            'you can use', 'you can do', 'it can',
            'main feature', 'key feature', 'important feature'
        ]):
            # Extract the key concept
            concept = extract_concept_from_sentence(sentence_clean)
            if concept and len(concept) > 10:
                items.append(f"• {concept}")
    
    # Remove duplicates and return top items
    unique_items = list(dict.fromkeys(items))
    return unique_items[:8]

def extract_concept_from_sentence(sentence):
    """Extract the main concept from a sentence."""
    # Remove common starting phrases
    sentence = re.sub(r'^(so|and|but|the|this|that|it|you can|this is|this tool|the tool)\s+', '', sentence, flags=re.IGNORECASE)
    
    # Look for tool names or key concepts
    # If sentence mentions a specific name, extract it
    if ':' in sentence:
        parts = sentence.split(':')
        if len(parts) >= 2:
            name = parts[0].strip()
            description = parts[1].strip()
            return f"{name}: {description[:80]}..."
    
    # Otherwise, take the first meaningful part
    words = sentence.split()
    if len(words) > 15:
        return ' '.join(words[:15]) + "..."
    else:
        return sentence

def analyze_content_context(transcript):
    """Analyze the transcript to provide context."""
    transcript_lower = transcript.lower()
    
    # Count mentions of different themes
    themes = {
        'productivity': ['productive', 'efficiency', 'workflow', 'organize', 'manage'],
        'learning': ['learn', 'study', 'education', 'knowledge', 'understand'],
        'technology': ['ai', 'artificial intelligence', 'software', 'digital', 'tech'],
        'business': ['business', 'entrepreneur', 'money', 'income', 'profit'],
        'creative': ['creative', 'design', 'content', 'video', 'create']
    }
    
    theme_scores = {}
    for theme, keywords in themes.items():
        score = sum(transcript_lower.count(keyword) for keyword in keywords)
        theme_scores[theme] = score
    
    # Get the dominant theme
    dominant_theme = max(theme_scores, key=theme_scores.get)
    
    # Generate context based on dominant theme
    if dominant_theme == 'productivity':
        return "As productivity becomes increasingly important, the presenter highlights tools that can streamline workflows and boost efficiency."
    elif dominant_theme == 'learning':
        return "With the growing need for continuous learning, these recommendations focus on tools that enhance knowledge acquisition and retention."
    elif dominant_theme == 'technology':
        return "In today's digital landscape, the presenter showcases cutting-edge technologies that are reshaping how we work and create."
    elif dominant_theme == 'business':
        return "For entrepreneurs and business professionals, these tools offer practical solutions for growth and success."
    else:
        return "The presenter shares valuable insights and practical recommendations for viewers looking to improve their approach."

def generate_conclusion(transcript, video_info):
    """Generate a contextual conclusion."""
    transcript_lower = transcript.lower()
    title_lower = video_info['title'].lower()
    
    if 'tool' in title_lower or 'app' in title_lower:
        if 'beginner' in transcript_lower or 'start' in transcript_lower:
            return "The video emphasizes choosing the right tools based on your experience level and specific needs, making it accessible for both beginners and advanced users."
        else:
            return "The video emphasizes adapting your tool choice to your specific workflow and requirements, ensuring maximum productivity and effectiveness."
    elif 'tip' in title_lower or 'technique' in title_lower:
        return "The video emphasizes practical application and provides actionable advice that viewers can implement immediately."
    else:
        return "The video provides comprehensive insights and practical guidance for viewers interested in the topic."

def get_topic_emoji(text):
    """Get an appropriate emoji based on the content."""
    text_lower = text.lower()
    
    # Technology/AI content
    if any(word in text_lower for word in ['ai', 'artificial intelligence', 'tool', 'app', 'software']):
        return '🤖'
    
    # Productivity content
    elif any(word in text_lower for word in ['productivity', 'workflow', 'organize', 'efficiency']):
        return '⚡'
    
    # Learning/Education content
    elif any(word in text_lower for word in ['learn', 'study', 'education', 'tutorial', 'guide']):
        return '📚'
    
    # Business content
    elif any(word in text_lower for word in ['business', 'entrepreneur', 'money', 'income']):
        return '💼'
    
    # Creative content
    elif any(word in text_lower for word in ['creative', 'design', 'content', 'video']):
        return '🎨'
    
    # Fishing/outdoor content
    elif any(word in text_lower for word in ['fish', 'fishing', 'bass', 'bait', 'lure']):
        return '🎣'
    
    # Default
    else:
        return '🎥'
