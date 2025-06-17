from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from typing import List, Dict, Any
import logging
import time
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryExpansionParser(BaseOutputParser):
    """Custom parser for query expansion output."""
    
    def parse(self, text: str) -> List[str]:
        """Parse the LLM output into a list of expanded queries."""
        try:
            # Split by newlines and clean up
            queries = [q.strip() for q in text.split('\n') if q.strip()]
            # Remove numbering and bullet points
            cleaned_queries = []
            for query in queries:
                query = query.strip('- •*')
                if query.startswith(('1.', '2.', '3.', '4.', '5.')):
                    query = query[2:].strip()
                if query and len(query) > 5:  # Filter out very short queries
                    cleaned_queries.append(query)
            return cleaned_queries[:5]  # Limit to 5 expanded queries
        except Exception as e:
            logger.error(f"Failed to parse query expansion: {e}")
            return []

class ContentSummaryParser(BaseOutputParser):
    """Custom parser for content summarization."""
    
    def parse(self, text: str) -> str:
        """Parse and clean the summarized content."""
        return text.strip()

class LangChainProcessor:
    """LangChain integration for query processing and content enhancement using Gemini."""
    
    def __init__(self):
        self.llm = None
        self.query_expansion_chain = None
        self.summarization_chain = None
        self.last_llm_call = 0
        self.llm_call_count = 0
        self.initialize_chains()
    
    def _rate_limit_llm_calls(self):
        """Rate limit LLM API calls to respect Google's free tier limits."""
        current_time = time.time()
        
        # Reset counter if a minute has passed
        if current_time - self.last_llm_call > 60:
            self.llm_call_count = 0
            self.last_llm_call = current_time
        
        # If we've hit the rate limit, wait
        if self.llm_call_count >= settings.llm_rate_limit:
            sleep_time = 60 - (current_time - self.last_llm_call)
            if sleep_time > 0:
                logger.info(f"LLM rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                self.llm_call_count = 0
                self.last_llm_call = time.time()
        
        self.llm_call_count += 1
    
    def initialize_chains(self):
        """Initialize LangChain components with Gemini."""
        try:
            if not settings.google_api_key:
                logger.warning("Google API key not provided. LangChain features will be limited.")
                return
            
            # Initialize Gemini LLM
            self.llm = ChatGoogleGenerativeAI(
                model=settings.llm_model,
                google_api_key=settings.google_api_key,
                temperature=settings.llm_temperature,
                max_output_tokens=500
            )
            
            # Query expansion chain
            query_expansion_prompt = PromptTemplate(
                input_variables=["query"],
                template="""
                Given the search query: "{query}"
                
                Generate 3-5 alternative search queries that would help find similar or related content.
                The queries should capture different aspects, synonyms, and related concepts.
                
                Original query: {query}
                
                Alternative queries:
                """
            )
            
            self.query_expansion_chain = LLMChain(
                llm=self.llm,
                prompt=query_expansion_prompt,
                output_parser=QueryExpansionParser()
            )
            
            # Content summarization chain
            summarization_prompt = PromptTemplate(
                input_variables=["content", "max_words"],
                template="""
                Summarize the following content in approximately {max_words} words.
                Focus on the key points and main ideas while maintaining clarity and readability.
                
                Content: {content}
                
                Summary:
                """
            )
            
            self.summarization_chain = LLMChain(
                llm=self.llm,
                prompt=summarization_prompt,
                output_parser=ContentSummaryParser()
            )
            
            logger.info("LangChain processors initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain: {e}")
    
    def expand_query(self, query: str) -> List[str]:
        """Expand a search query into multiple related queries."""
        if not self.query_expansion_chain:
            return [query]  # Return original query if LangChain not available
        
        try:
            # Rate limit API calls
            self._rate_limit_llm_calls()
            
            expanded_queries = self.query_expansion_chain.run(query=query)
            logger.info(f"Query expansion completed successfully")
            
            # Always include the original query
            all_queries = [query] + expanded_queries
            return list(set(all_queries))  # Remove duplicates
                
        except Exception as e:
            logger.error(f"Query expansion failed: {e}")
            return [query]
    
    def summarize_content(self, content: str, max_words: int = 50) -> str:
        """Summarize long content."""
        if not self.summarization_chain:
            # Fallback: return first few sentences
            sentences = content.split('. ')
            summary = '. '.join(sentences[:2])
            return summary + '.' if not summary.endswith('.') else summary
        
        try:
            # Only summarize if content is long enough
            if len(content.split()) <= max_words:
                return content
            
            # Rate limit API calls
            self._rate_limit_llm_calls()
            
            summary = self.summarization_chain.run(
                content=content,
                max_words=max_words
            )
            logger.info(f"Summarization completed successfully")
            return summary
                
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            # Fallback to truncation
            words = content.split()
            if len(words) > max_words:
                return ' '.join(words[:max_words]) + '...'
            return content
    
    def enhance_search_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Enhance search results with summaries and relevance explanations."""
        if not results:
            return results
        
        enhanced_results = []
        
        for result in results:
            enhanced_result = result.copy()
            
            # Add content summary
            if len(result['content'].split()) > 100:
                enhanced_result['summary'] = self.summarize_content(result['content'], 50)
            else:
                enhanced_result['summary'] = result['content']
            
            # Add relevance explanation (simplified)
            relevance_score = result.get('similarity_score', 0)
            if relevance_score > 0.8:
                enhanced_result['relevance_explanation'] = "Highly relevant - strong semantic match"
            elif relevance_score > 0.6:
                enhanced_result['relevance_explanation'] = "Moderately relevant - good conceptual match"
            elif relevance_score > 0.4:
                enhanced_result['relevance_explanation'] = "Somewhat relevant - partial match"
            else:
                enhanced_result['relevance_explanation'] = "Limited relevance - weak match"
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def generate_search_suggestions(self, query: str, results: List[Dict[str, Any]]) -> List[str]:
        """Generate search suggestions based on query and results."""
        try:
            if not results:
                return []
            
            # Extract common categories and tags from results
            categories = set(result['category'] for result in results)
            all_tags = []
            for result in results:
                all_tags.extend(result['tags'])
            
            # Count tag frequency
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Get most common tags
            common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            suggestions = []
            
            # Add category-based suggestions
            for category in categories:
                suggestions.append(f"{query} in {category.lower()}")
            
            # Add tag-based suggestions
            for tag, _ in common_tags:
                if tag.lower() not in query.lower():
                    suggestions.append(f"{query} {tag.lower()}")
            
            return suggestions[:5]
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return []
    
    def analyze_search_intent(self, query: str) -> Dict[str, Any]:
        """Analyze search intent and provide query insights."""
        try:
            query_lower = query.lower()
            
            # Determine query type
            question_words = ['what', 'how', 'why', 'when', 'where', 'who']
            is_question = any(word in query_lower for word in question_words)
            
            # Determine domain
            tech_keywords = ['ai', 'machine learning', 'programming', 'software', 'technology', 'computer']
            science_keywords = ['research', 'study', 'experiment', 'biology', 'physics', 'chemistry']
            business_keywords = ['marketing', 'management', 'strategy', 'finance', 'business']
            health_keywords = ['health', 'medical', 'medicine', 'wellness', 'fitness']
            
            likely_domain = "General"
            if any(keyword in query_lower for keyword in tech_keywords):
                likely_domain = "Technology"
            elif any(keyword in query_lower for keyword in science_keywords):
                likely_domain = "Science"
            elif any(keyword in query_lower for keyword in business_keywords):
                likely_domain = "Business"
            elif any(keyword in query_lower for keyword in health_keywords):
                likely_domain = "Health"
            
            return {
                "query_type": "Question" if is_question else "Topic",
                "likely_domain": likely_domain,
                "query_length": len(query.split()),
                "complexity": "High" if len(query.split()) > 5 else "Medium" if len(query.split()) > 2 else "Low"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze search intent: {e}")
            return {"query_type": "Unknown", "likely_domain": "General", "query_length": 0, "complexity": "Unknown"}

# Global processor instance
langchain_processor = LangChainProcessor()