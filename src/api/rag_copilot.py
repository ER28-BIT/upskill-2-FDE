"""RAG (Retrieval-Augmented Generation) Copilot for document Q&A."""
import os
from typing import List, Dict, Any
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

class RAGCopilot:
    """RAG copilot for answering questions based on local documentation."""
    
    def __init__(self, docs_path: str = "docs", collection_name: str = "fde_docs"):
        self.docs_path = Path(docs_path)
        self.collection_name = collection_name
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB with PersistentClient
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "FDE MVP documentation"}
            )
    
    def index_documents(self) -> Dict[str, Any]:
        """Index all documents from the docs directory."""
        if not self.docs_path.exists():
            return {"status": "error", "message": f"Docs path {self.docs_path} does not exist"}
        
        documents = []
        metadatas = []
        ids = []
        
        # Find all text and markdown files
        for file_path in self.docs_path.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split into chunks (simple paragraph-based chunking)
                chunks = self._chunk_document(content, file_path.name)
                
                for idx, chunk in enumerate(chunks):
                    doc_id = f"{file_path.stem}_{idx}"
                    documents.append(chunk['text'])
                    metadatas.append({
                        'source': str(file_path),
                        'filename': file_path.name,
                        'chunk_index': idx
                    })
                    ids.append(doc_id)
            
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        if documents:
            # Add documents to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "status": "success",
                "indexed_documents": len(set(m['filename'] for m in metadatas)),
                "total_chunks": len(documents)
            }
        else:
            return {
                "status": "warning",
                "message": "No documents found to index"
            }
    
    def _chunk_document(self, content: str, filename: str, chunk_size: int = 500) -> List[Dict[str, Any]]:
        """Split document into chunks."""
        # Simple chunking by paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            if current_size + para_size > chunk_size and current_chunk:
                chunks.append({
                    'text': '\n\n'.join(current_chunk),
                    'source': filename
                })
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
        
        if current_chunk:
            chunks.append({
                'text': '\n\n'.join(current_chunk),
                'source': filename
            })
        
        return chunks if chunks else [{'text': content, 'source': filename}]
    
    def query(self, question: str, max_sources: int = 3, min_confidence: float = 0.3) -> Dict[str, Any]:
        """Query the RAG system with a question."""
        
        # Retrieve relevant documents
        results = self.collection.query(
            query_texts=[question],
            n_results=max_sources
        )
        
        if not results['documents'] or not results['documents'][0]:
            return {
                "answer": "I don't have sufficient information to answer this question. Please refer to the documentation or contact support.",
                "sources": [],
                "confidence": 0.0,
                "has_sufficient_sources": False
            }
        
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results else [0.5] * len(documents)
        
        # Calculate confidence based on retrieval distances
        # Lower distance = higher confidence
        confidences = [max(0, 1 - d) for d in distances]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Check if we have sufficient sources
        has_sufficient_sources = avg_confidence >= min_confidence
        
        if not has_sufficient_sources:
            return {
                "answer": "I found some potentially relevant information, but I'm not confident enough to provide a reliable answer. Please consult the full documentation or seek expert advice.",
                "sources": self._format_sources(documents, metadatas, confidences),
                "confidence": avg_confidence,
                "has_sufficient_sources": False
            }
        
        # Generate answer based on retrieved documents
        answer = self._generate_answer(question, documents, metadatas)
        
        return {
            "answer": answer,
            "sources": self._format_sources(documents, metadatas, confidences),
            "confidence": round(avg_confidence, 3),
            "has_sufficient_sources": True
        }
    
    def _format_sources(self, documents: List[str], metadatas: List[Dict], confidences: List[float]) -> List[Dict[str, str]]:
        """Format sources with citations."""
        sources = []
        for doc, meta, conf in zip(documents, metadatas, confidences):
            sources.append({
                'filename': meta.get('filename', 'unknown'),
                'excerpt': doc[:200] + "..." if len(doc) > 200 else doc,
                'confidence': round(conf, 3)
            })
        return sources
    
    def _generate_answer(self, question: str, documents: List[str], metadatas: List[Dict]) -> str:
        """Generate an answer based on retrieved documents."""
        # Simple answer generation: concatenate relevant excerpts
        context = "\n\n".join(documents)
        
        # Create a structured answer
        answer = f"Based on the available documentation:\n\n{context[:500]}"
        
        if len(context) > 500:
            answer += "...\n\n[See sources for more details]"
        
        return answer
    
    def reset_collection(self):
        """Reset the document collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "FDE MVP documentation"}
            )
            return {"status": "success", "message": "Collection reset"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
