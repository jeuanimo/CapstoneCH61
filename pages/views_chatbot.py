"""
PUBLIC INFORMATION CHATBOT VIEWS
Secure keyword-matching chatbot for public Q&A about the fraternity.

Security Features:
- POST only endpoint
- CSRF protection (Django default)
- Rate limiting (5 requests per minute)
- Input length limit (400 chars)
- Input sanitization (remove dangerous chars)
- No external APIs
- No user history storage
- Safe fallback messages
- Keyword-based scoring (no ML, no fabrication)
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
import re
import logging

from pages.models_chatbot import PublicAnswer

logger = logging.getLogger(__name__)

# Constants
MAX_QUERY_LENGTH = 400
MIN_QUERY_LENGTH = 3
CONFIDENCE_THRESHOLD_DEFAULT = 30
MAX_SUGGESTIONS = 5
RATE_LIMIT = '5/m'  # 5 requests per minute per IP

# Greeting words to detect casual conversation
GREETING_WORDS = {
    'hello', 'hi', 'hey', 'greetings', 'howdy', 'hola', 'sup', 'yo',
    'good morning', 'good afternoon', 'good evening', 'whats up', "what's up",
    'how are you', 'how do you do', 'nice to meet you'
}

# Sanitization: Remove dangerous characters but keep spaces, letters, numbers, basic punctuation
SANITIZE_PATTERN = re.compile(r'[^a-zA-Z0-9\s\?\.\,\-\']')
WHITESPACE_PATTERN = re.compile(r'\s+')


def _sanitize_input(text):
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Raw user input
        
    Returns:
        Sanitized string safe for processing
    """
    # Remove dangerous characters (keep alphanumeric, spaces, basic punctuation)
    sanitized = SANITIZE_PATTERN.sub('', text)
    
    # Collapse multiple spaces into single space
    sanitized = WHITESPACE_PATTERN.sub(' ', sanitized)
    
    # Strip leading/trailing whitespace
    return sanitized.strip()


def _validate_query(query):
    """
    Validate user query.
    
    Args:
        query: User input string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not isinstance(query, str):
        return False, "Query must be a non-empty string."
    
    if len(query) > MAX_QUERY_LENGTH:
        return False, f"Query too long. Maximum {MAX_QUERY_LENGTH} characters."
    
    if len(query) < MIN_QUERY_LENGTH:
        return False, f"Query too short. Minimum {MIN_QUERY_LENGTH} characters."
    
    return True, None


def _is_greeting(query):
    """
    Check if the query is a casual greeting.
    
    Args:
        query: Sanitized user query
        
    Returns:
        Boolean indicating if query is a greeting
    """
    query_lower = query.lower().strip()
    
    # Check exact match or close match with greetings
    if query_lower in GREETING_WORDS:
        return True
    
    # Check if query starts with a greeting word (e.g., "hello there")
    for greeting in GREETING_WORDS:
        if query_lower.startswith(greeting):
            return True
    
    return False


def _build_greeting_response():
    """
    Build a friendly greeting response with helpful prompts.
    
    Returns:
        Dictionary with greeting response data
    """
    return {
        'success': True,
        'type': 'greeting',
        'message': "Hello! I'm the Phi Beta Sigma assistant. How can I help you today?",
        'prompts': [
            'What is Phi Beta Sigma?',
            'How can I join the fraternity?',
            'What events do you have coming up?',
            'Tell me about your community programs'
        ],
        'source': 'greeting_handler',
    }


def _calculate_keyword_score(query, keywords_list):
    """
    Calculate match score using simple keyword matching.
    
    Scoring algorithm:
    - Exact phrase match: 100 points
    - All query words in keywords: 80 points
    - Partial word matches: points per match
    - Case-insensitive matching
    
    Args:
        query: User query (sanitized)
        keywords_list: List of keywords from PublicAnswer
        
    Returns:
        Integer score (0-100)
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())
    keyword_words = set(' '.join(keywords_list).lower().split())
    
    # Exact phrase match in keywords (highest priority)
    for keyword in keywords_list:
        if query_lower == keyword.lower():
            return 100
    
    # Check if all query words exist in keywords
    matching_words = query_words & keyword_words
    
    if not matching_words:
        return 0
    
    # Calculate percentage of query words that matched
    match_percentage = (len(matching_words) / len(query_words)) * 100
    
    # Additional boost if multiple words matched
    if len(matching_words) > 1:
        match_percentage = min(100, match_percentage + (len(matching_words) * 5))
    
    return int(match_percentage)


def _find_best_matches(query):
    """
    Find best matching answers for a query using keyword scoring.
    
    Args:
        query: Sanitized user query
        
    Returns:
        List of tuples (PublicAnswer, score) sorted by score descending
    """
    answers = PublicAnswer.objects.filter(is_active=True)
    matches = []
    
    for answer in answers:
        keyword_list = answer.get_keywords_list()
        score = _calculate_keyword_score(query, keyword_list)
        
        # Only include if score meets answer's confidence threshold
        if score >= answer.confidence_threshold:
            matches.append((answer, score))
    
    # Sort by score descending, then by recency
    matches.sort(key=lambda x: (-x[1], -x[0].created_at.timestamp()))
    
    return matches


def _get_fallback_suggestions():
    """
    Get recent public answers to suggest when no match is found.
    
    Returns:
        List of top MAX_SUGGESTIONS most recent PublicAnswers
    """
    return list(
        PublicAnswer.objects.filter(is_active=True)
        .order_by('-created_at')[:MAX_SUGGESTIONS]
    )


def _build_response(best_match=None, matches=None, suggestions=None):
    """
    Build JSON response for chatbot query.
    
    Args:
        best_match: Tuple of (PublicAnswer, score) or None
        matches: List of matching (PublicAnswer, score) tuples
        suggestions: List of suggested answers
        
    Returns:
        Dictionary with response data
    """
    if best_match:
        answer, score = best_match
        return {
            'success': True,
            'type': 'answer',
            'answer': answer.answer,
            'question': answer.question,
            'category': answer.get_category_display(),
            'confidence': min(100, max(0, score)),  # Clamp 0-100
            'source': 'public_knowledge_base',
        }
    
    elif suggestions:
        suggestion_list = [
            {
                'question': s.question,
                'category': s.get_category_display(),
                'id': s.id,
            }
            for s in suggestions
        ]
        return {
            'success': True,
            'type': 'suggestions',
            'message': 'I didn\'t find an exact match, but here are some related topics:',
            'suggestions': suggestion_list,
            'source': 'public_suggestions',
        }
    
    else:
        return {
            'success': True,
            'type': 'no_match',
            'message': 'I couldn\'t find an answer to your question. Please contact us directly or visit our website for more information.',
            'source': 'fallback',
        }


@require_http_methods(['POST'])
@csrf_protect
@ratelimit(key='ip', rate=RATE_LIMIT, method='POST')
def chatbot_query(request):
    """
    Handle public chatbot queries.
    
    Security:
    - POST only
    - CSRF protected
    - Rate limited (5 req/min per IP)
    - Input validated and sanitized
    - Never stores user data
    - Only returns public info
    
    Request JSON:
    {
        "query": "What is your fraternity about?"
    }
    
    Response JSON (success):
    {
        "success": true,
        "type": "answer|suggestions|no_match",
        "answer": "...",
        "message": "...",
        "suggestions": [...],
        "confidence": 85,
        "source": "public_knowledge_base"
    }
    
    Response JSON (error):
    {
        "success": false,
        "error": "Error message"
    }
    """
    try:
        # Parse JSON request
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            logger.warning('Invalid JSON in chatbot query')
            return JsonResponse({
                'success': False,
                'error': 'Invalid request format.'
            }, status=400)
        
        # Extract and sanitize query
        raw_query = data.get('query', '').strip()
        
        # Validate input
        is_valid, error_msg = _validate_query(raw_query)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=400)
        
        # Sanitize input
        query = _sanitize_input(raw_query)
        
        # Log query (do NOT log sensitive data)
        logger.info(f'Chatbot query received: {len(query)} chars')
        
        # Check if it's a greeting first
        if _is_greeting(query):
            response = _build_greeting_response()
        else:
            # Find best matches
            matches = _find_best_matches(query)
            
            if matches:
                # Return best match
                best_match = matches[0]
                response = _build_response(best_match=best_match)
            else:
                # No match - return suggestions
                suggestions = _get_fallback_suggestions()
                if suggestions:
                    response = _build_response(suggestions=suggestions)
                else:
                    response = _build_response()
        
        return JsonResponse(response, status=200)
    
    except Exception as e:
        # Log error but don't expose details to user
        logger.exception('Error in chatbot_query')
        return JsonResponse({
            'success': False,
            'error': 'An error occurred processing your request.'
        }, status=500)


def chatbot_widget(request):
    """
    Render the chatbot widget page.
    
    GET request - returns HTML page with chatbot widget.
    """
    context = {
        'faq_categories': PublicAnswer.CATEGORY_CHOICES,
        'answer_count': PublicAnswer.objects.filter(is_active=True).count(),
    }
    return render(request, 'pages/chatbot_widget.html', context)
