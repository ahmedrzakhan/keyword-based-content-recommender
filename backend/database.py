import json
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from config.settings import settings
import logging
from datetime import datetime
import uuid
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentDatabase:
    def __init__(self):
        self.client = None
        self.collection = None
        self.search_stats = []
        self.last_embedding_call = 0
        self.embedding_call_count = 0
        self.initialize_gemini()
        self.initialize_db()
    
    def initialize_gemini(self):
        """Initialize Google Generative AI client."""
        try:
            if settings.google_api_key:
                genai.configure(api_key=settings.google_api_key)
                logger.info("Google Generative AI configured successfully")
            else:
                logger.warning("Google API key not provided. Embedding generation will use fallback.")
        except Exception as e:
            logger.error(f"Failed to configure Google Generative AI: {e}")
    
    def initialize_db(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.chroma_db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaDB initialized with collection: {settings.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def _rate_limit_embedding_calls(self):
        """Rate limit embedding API calls to respect Google's free tier limits."""
        current_time = time.time()
        
        # Reset counter if a minute has passed
        if current_time - self.last_embedding_call > 60:
            self.embedding_call_count = 0
            self.last_embedding_call = current_time
        
        # If we've hit the rate limit, wait
        if self.embedding_call_count >= settings.embedding_rate_limit:
            sleep_time = 60 - (current_time - self.last_embedding_call)
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                self.embedding_call_count = 0
                self.last_embedding_call = time.time()
        
        self.embedding_call_count += 1

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Google Generative AI."""
        try:
            if not settings.google_api_key:
                logger.warning("Google API key not provided, using dummy embedding")
                return [0.1] * settings.embedding_dimension
            
            # Rate limit API calls
            self._rate_limit_embedding_calls()
            
            # Generate embedding using Gemini
            response = genai.embed_content(
                model=f"models/{settings.embedding_model}",
                content=text,
                task_type="retrieval_document"  # Optimized for document retrieval
            )
            
            embedding = response['embedding']
            
            # Ensure embedding has correct dimensions
            if len(embedding) != settings.embedding_dimension:
                logger.warning(f"Embedding dimension mismatch: got {len(embedding)}, expected {settings.embedding_dimension}")
                # Pad or truncate to match expected dimensions
                if len(embedding) < settings.embedding_dimension:
                    embedding.extend([0.0] * (settings.embedding_dimension - len(embedding)))
                else:
                    embedding = embedding[:settings.embedding_dimension]
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate Gemini embedding: {e}")
            # Return dummy embedding for development
            return [0.1] * settings.embedding_dimension
    
    def load_sample_data(self):
        """Load sample data into ChromaDB."""
        try:
            with open('data/sample_content.json', 'r') as f:
                content_data = json.load(f)
            
            # Check if data already exists
            if self.collection.count() > 0:
                logger.info("Data already exists in collection")
                return
            
            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []
            embeddings = []
            
            for item in content_data:
                # Combine title and content for embedding
                text_for_embedding = f"{item['title']} {item['content']}"
                
                documents.append(item['content'])
                metadatas.append({
                    'title': item['title'],
                    'category': item['category'],
                    'tags': ','.join(item['tags']),
                    'difficulty': item['difficulty'],
                    'read_time': item['read_time'],
                    'author': item['author'],
                    'created_at': item['created_at']
                })
                ids.append(item['id'])
                
                # Generate embedding
                embedding = self.generate_embedding(text_for_embedding)
                embeddings.append(embedding)
            
            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"Loaded {len(content_data)} items into ChromaDB")
            
        except Exception as e:
            logger.error(f"Failed to load sample data: {e}")
            raise
    
    def search_content(self, query: str, max_results: int = 10, 
                      category_filter: Optional[str] = None,
                      difficulty_filter: Optional[str] = None,
                      min_similarity: float = 0.0) -> List[Dict[str, Any]]:
        """Search for content using semantic similarity."""
        start_time = datetime.now()
        
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            
            # Build where clause for filtering
            where_clause = {}
            if category_filter:
                where_clause['category'] = category_filter
            if difficulty_filter:
                where_clause['difficulty'] = difficulty_filter
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                where=where_clause if where_clause else None
            )
            
            # Process results
            content_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    similarity_score = 1 - results['distances'][0][i]  # Convert distance to similarity
                    
                    if similarity_score >= min_similarity:
                        content_results.append({
                            'id': results['ids'][0][i],
                            'title': results['metadatas'][0][i]['title'],
                            'content': results['documents'][0][i],
                            'category': results['metadatas'][0][i]['category'],
                            'tags': results['metadatas'][0][i]['tags'].split(','),
                            'difficulty': results['metadatas'][0][i]['difficulty'],
                            'read_time': results['metadatas'][0][i]['read_time'],
                            'author': results['metadatas'][0][i]['author'],
                            'created_at': results['metadatas'][0][i]['created_at'],
                            'similarity_score': round(similarity_score, 4)
                        })
            
            # Record search stats
            search_time = (datetime.now() - start_time).total_seconds()
            self.search_stats.append({
                'query': query,
                'results_count': len(content_results),
                'search_time': search_time,
                'timestamp': datetime.now().isoformat()
            })
            
            return content_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get specific content by ID."""
        try:
            results = self.collection.get(ids=[content_id])
            
            if results['documents']:
                return {
                    'id': results['ids'][0],
                    'title': results['metadatas'][0]['title'],
                    'content': results['documents'][0],
                    'category': results['metadatas'][0]['category'],
                    'tags': results['metadatas'][0]['tags'].split(','),
                    'difficulty': results['metadatas'][0]['difficulty'],
                    'read_time': results['metadatas'][0]['read_time'],
                    'author': results['metadatas'][0]['author'],
                    'created_at': results['metadatas'][0]['created_at']
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get content by ID: {e}")
            return None
    
    def add_content(self, content_data: Dict[str, Any]) -> str:
        """Add new content to the database."""
        try:
            content_id = str(uuid.uuid4())
            text_for_embedding = f"{content_data['title']} {content_data['content']}"
            embedding = self.generate_embedding(text_for_embedding)
            
            self.collection.add(
                documents=[content_data['content']],
                metadatas=[{
                    'title': content_data['title'],
                    'category': content_data['category'],
                    'tags': ','.join(content_data['tags']),
                    'difficulty': content_data['difficulty'],
                    'read_time': content_data['read_time'],
                    'author': content_data['author'],
                    'created_at': datetime.now().strftime('%Y-%m-%d')
                }],
                ids=[content_id],
                embeddings=[embedding]
            )
            
            logger.info(f"Added new content with ID: {content_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"Failed to add content: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            total_content = self.collection.count()
            
            # Get all metadata to calculate category distribution
            all_data = self.collection.get()
            categories = {}
            for metadata in all_data['metadatas']:
                category = metadata['category']
                categories[category] = categories.get(category, 0) + 1
            
            # Calculate search stats
            total_searches = len(self.search_stats)
            avg_search_time = sum(s['search_time'] for s in self.search_stats) / max(total_searches, 1)
            
            # Get popular queries (last 100 searches)
            recent_searches = self.search_stats[-100:] if self.search_stats else []
            query_counts = {}
            for search in recent_searches:
                query = search['query']
                query_counts[query] = query_counts.get(query, 0) + 1
            
            popular_queries = [
                {'query': query, 'count': count}
                for query, count in sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            return {
                'total_content': total_content,
                'categories': categories,
                'total_searches': total_searches,
                'average_search_time': round(avg_search_time, 4),
                'popular_queries': popular_queries
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                'total_content': 0,
                'categories': {},
                'total_searches': 0,
                'average_search_time': 0.0,
                'popular_queries': []
            }
    
    def get_similar_content(self, content_id: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Find content similar to a specific content item."""
        try:
            # Get the original content
            original_content = self.get_content_by_id(content_id)
            if not original_content:
                return []
            
            # Search for similar content using the original content's text
            query_text = f"{original_content['title']} {original_content['content']}"
            similar_results = self.search_content(query_text, max_results + 1)  # +1 to exclude original
            
            # Remove the original content from results
            similar_results = [r for r in similar_results if r['id'] != content_id][:max_results]
            
            return similar_results
            
        except Exception as e:
            logger.error(f"Failed to get similar content: {e}")
            return []

# Global database instance
db = ContentDatabase()