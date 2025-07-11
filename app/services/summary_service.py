# app/services/summary_service.py

from typing import Dict, Tuple, List, Optional
from app.utils.summarizer import run_summarization
from app.utils.keyword_extractor import extract_keywords
from app.utils.advanced_summarizer import create_professional_summary
import nltk
from collections import defaultdict


class SummaryService:
    """Service for handling summary generation and processing."""
    
    @staticmethod
    def generate_summary(transcript: str, video_info: Dict[str, str]) -> Tuple[str, str]:
        """
        Generate a comprehensive summary and keywords from transcript.
        
        Args:
            transcript (str): Video transcript
            video_info (Dict[str, str]): Video metadata
            
        Returns:
            Tuple[str, str]: Enhanced summary and keywords string
            
        Raises:
            Exception: If summary generation fails
        """
        if not transcript or len(transcript.strip()) == 0:
            raise Exception("Cannot generate summary from empty transcript")
        
        try:
            # Use the existing summarization logic
            summary, keywords = run_summarization(transcript, video_info)
            
            if not summary or summary == "Summary not available.":
                # Fallback to basic summary
                summary = SummaryService._generate_basic_summary(transcript, video_info)
            
            if not keywords:
                # Fallback to basic keyword extraction
                keywords = SummaryService._extract_basic_keywords(transcript)
            
            return summary, keywords
            
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    @staticmethod
    def _generate_basic_summary(transcript: str, video_info: Dict[str, str]) -> str:
        """
        Generate a basic summary as fallback.
        
        Args:
            transcript (str): Video transcript
            video_info (Dict[str, str]): Video metadata
            
        Returns:
            str: Basic summary
        """
        try:
            # Get first few sentences as a basic summary
            sentences = transcript.split('.')[:5]
            basic_summary = '. '.join(sentence.strip() for sentence in sentences if sentence.strip())
            
            if len(basic_summary) > 500:
                basic_summary = basic_summary[:500] + "..."
            
            return f"📺 Summary of \"{video_info.get('title', 'Video')}\" by {video_info.get('channel', 'Unknown Channel')}:\n\n{basic_summary}"
            
        except Exception:
            return f"📺 This video \"{video_info.get('title', 'Video')}\" by {video_info.get('channel', 'Unknown Channel')} contains content that has been transcribed but could not be automatically summarized."
    
    @staticmethod
    def _extract_basic_keywords(transcript: str, max_keywords: int = 10) -> str:
        """
        Extract basic keywords as fallback.
        
        Args:
            transcript (str): Video transcript
            max_keywords (int): Maximum number of keywords to extract
            
        Returns:
            str: Comma-separated keywords
        """
        try:
            # Download NLTK data if needed
            try:
                nltk.data.find('tokenizers/punkt')
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
            
            # Basic keyword extraction
            stop_words = set(nltk.corpus.stopwords.words('english'))
            words = nltk.tokenize.word_tokenize(transcript.lower())
            filtered_words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
            
            freq = defaultdict(int)
            for word in filtered_words:
                freq[word] += 1
            
            sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, _ in sorted_keywords[:max_keywords]]
            
            return ", ".join(keywords) if keywords else "video, content, information"
            
        except Exception:
            return "video, content, information"
    
    @staticmethod
    def analyze_content_type(transcript: str, video_info: Dict[str, str]) -> str:
        """
        Analyze the type of content based on transcript and metadata.
        
        Args:
            transcript (str): Video transcript
            video_info (Dict[str, str]): Video metadata
            
        Returns:
            str: Content type (e.g., "tutorial", "review", "educational", etc.)
        """
        title = video_info.get('title', '').lower()
        transcript_lower = transcript.lower()
        
        # Define content type indicators
        content_indicators = {
            'tutorial': ['how to', 'tutorial', 'guide', 'step by step', 'learn', 'teach'],
            'review': ['review', 'opinion', 'rating', 'recommend', 'pros and cons'],
            'educational': ['explain', 'education', 'science', 'history', 'facts'],
            'entertainment': ['funny', 'comedy', 'entertainment', 'fun', 'laugh'],
            'news': ['news', 'breaking', 'report', 'update', 'current'],
            'gaming': ['game', 'gaming', 'play', 'level', 'boss', 'strategy'],
            'cooking': ['recipe', 'cook', 'ingredient', 'kitchen', 'food'],
            'fitness': ['workout', 'exercise', 'fitness', 'training', 'muscle'],
            'technology': ['tech', 'software', 'app', 'device', 'computer'],
            'music': ['song', 'music', 'album', 'artist', 'lyrics']
        }
        
        # Count indicators in title and transcript
        scores = {}
        for content_type, indicators in content_indicators.items():
            score = 0
            for indicator in indicators:
                score += title.count(indicator) * 2  # Title has more weight
                score += transcript_lower.count(indicator)
            scores[content_type] = score
        
        # Return the type with highest score, or 'general' if no clear type
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'general'
    
    @staticmethod
    def extract_key_timestamps(transcript: str) -> List[str]:
        """
        Extract potential key moments or topics from transcript.
        
        Args:
            transcript (str): Video transcript
            
        Returns:
            List[str]: List of key points or topics
        """
        try:
            sentences = transcript.split('.')
            key_points = []
            
            # Look for sentences that might indicate important points
            importance_indicators = [
                'important', 'key', 'main', 'first', 'second', 'third',
                'remember', 'note', 'tip', 'trick', 'secret', 'best',
                'worst', 'never', 'always', 'must', 'should', 'need'
            ]
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and len(sentence) < 200:  # Reasonable length
                    sentence_lower = sentence.lower()
                    if any(indicator in sentence_lower for indicator in importance_indicators):
                        key_points.append(sentence)
                        if len(key_points) >= 5:  # Limit to 5 key points
                            break
            
            return key_points
            
        except Exception:
            return []
    
    @staticmethod
    def get_summary_statistics(transcript: str, summary: str) -> Dict[str, any]:
        """
        Get statistics about the summary and original content.
        
        Args:
            transcript (str): Original transcript
            summary (str): Generated summary
            
        Returns:
            Dict[str, any]: Statistics dictionary
        """
        try:
            transcript_words = len(transcript.split())
            summary_words = len(summary.split())
            compression_ratio = round((1 - summary_words / transcript_words) * 100, 1) if transcript_words > 0 else 0
            
            return {
                'original_word_count': transcript_words,
                'summary_word_count': summary_words,
                'compression_ratio': compression_ratio,
                'estimated_reading_time': max(1, summary_words // 200),  # Assuming 200 WPM
                'original_estimated_time': max(1, transcript_words // 150)  # Assuming 150 WPM for original
            }
        except Exception:
            return {
                'original_word_count': 0,
                'summary_word_count': 0,
                'compression_ratio': 0,
                'estimated_reading_time': 1,
                'original_estimated_time': 1
            }
