"""
Vector Manager for AI Builder
Handles document storage and retrieval using ChromaDB
"""

import os
import hashlib
from typing import List, Dict, Any, Optional
from core.config_manager import config
from core.logger import logger


class VectorManager:
    def __init__(self):
        self.collection_name = config.vector_store.collection_name
        self.persist_directory = config.vector_store.persist_directory
        self._client = None
        self._collection = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Ensure persist directory exists
            os.makedirs(self.persist_directory, exist_ok=True)
            
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.logger.info(f"Initialized ChromaDB collection: {self.collection_name}")
            
        except ImportError:
            raise ImportError("chromadb package not installed. Run: pip install chromadb")
        except Exception as e:
            logger.log_error(e, "Initializing ChromaDB client")
            raise
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add document to vector store
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            Document ID
        """
        try:
            # Generate unique ID based on content hash
            doc_id = hashlib.md5(content.encode()).hexdigest()
            
            # Add metadata
            doc_metadata = metadata or {}
            doc_metadata.update({
                "length": len(content),
                "type": "document"
            })
            
            # Add to collection
            self._collection.add(
                documents=[content],
                metadatas=[doc_metadata],
                ids=[doc_id]
            )
            
            logger.logger.info(f"Added document to vector store: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.log_error(e, "Adding document to vector store")
            raise
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of matching documents with metadata
        """
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = []
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'id': results['ids'][0][i],
                    'content': doc,
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
            
            logger.logger.info(f"Found {len(documents)} matching documents")
            return documents
            
        except Exception as e:
            logger.log_error(e, "Searching vector store")
            return []
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        try:
            results = self._collection.get(ids=[doc_id])
            
            if results['documents']:
                return {
                    'id': doc_id,
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0]
                }
            return None
            
        except Exception as e:
            logger.log_error(e, f"Getting document: {doc_id}")
            return None
    
    def delete_document(self, doc_id: str):
        """Delete document by ID"""
        try:
            self._collection.delete(ids=[doc_id])
            logger.logger.info(f"Deleted document: {doc_id}")
        except Exception as e:
            logger.log_error(e, f"Deleting document: {doc_id}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self._collection.count()
            return {
                "document_count": count,
                "collection_name": self.collection_name
            }
        except Exception as e:
            logger.log_error(e, "Getting collection stats")
            return {"document_count": 0, "collection_name": self.collection_name}


# Global vector manager instance
vector_manager = VectorManager()
