"""
Knowledge base search using sentence embeddings.
Uses semantic search to find relevant documentation for customer queries.
"""
import json
import pickle
from pathlib import Path
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models import KnowledgeBaseResult


class KnowledgeBase:
    """Semantic search over product documentation"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize knowledge base with embedding model.

        Args:
            model_name: HuggingFace model for embeddings (default is fast and efficient)
        """
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
        self.index_file = Path("kb_index.pkl")

    def load_from_markdown(self, markdown_file: Path):
        """
        Load knowledge base from markdown documentation file.
        Splits into sections based on headers.
        """
        print(f"Loading knowledge base from {markdown_file}...")

        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by major headers (##)
        sections = self._split_by_headers(content)

        self.documents = []
        for title, text in sections:
            self.documents.append({
                "title": title,
                "content": text,
                "source": str(markdown_file),
                "url": f"https://docs.techcorp-cloudflow.com#{title.lower().replace(' ', '-')}"
            })

        print(f"Loaded {len(self.documents)} documentation sections")

        # Generate embeddings
        self._generate_embeddings()

        # Save index for faster loading next time
        self._save_index()

    def load_index(self):
        """Load pre-computed embeddings index"""
        if not self.index_file.exists():
            raise FileNotFoundError(f"Index file not found: {self.index_file}")

        print("Loading pre-computed knowledge base index...")
        with open(self.index_file, 'rb') as f:
            data = pickle.load(f)

        self.documents = data['documents']
        self.embeddings = data['embeddings']
        print(f"Loaded {len(self.documents)} documents from index")

    def _save_index(self):
        """Save embeddings index to disk"""
        data = {
            'documents': self.documents,
            'embeddings': self.embeddings
        }
        with open(self.index_file, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved knowledge base index to {self.index_file}")

    def _split_by_headers(self, content: str) -> List[Tuple[str, str]]:
        """Split markdown content by headers"""
        sections = []
        lines = content.split('\n')

        current_title = "Introduction"
        current_content = []

        for line in lines:
            # Check for header (## or ###)
            if line.startswith('## ') or line.startswith('### '):
                # Save previous section
                if current_content:
                    sections.append((current_title, '\n'.join(current_content)))

                # Start new section
                current_title = line.lstrip('#').strip()
                current_content = []
            else:
                current_content.append(line)

        # Add final section
        if current_content:
            sections.append((current_title, '\n'.join(current_content)))

        return sections

    def _generate_embeddings(self):
        """Generate embeddings for all documents"""
        print("Generating embeddings...")

        # Create combined text for each document (title + content for better semantic match)
        texts = [
            f"{doc['title']}\n{doc['content']}"
            for doc in self.documents
        ]

        # Generate embeddings
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        print("Embeddings generated")

    def search(
        self,
        query: str,
        top_k: int = 3,
        min_relevance: float = 0.3
    ) -> List[KnowledgeBaseResult]:
        """
        Search knowledge base for relevant documents.

        Args:
            query: User's question
            top_k: Number of results to return
            min_relevance: Minimum relevance score (0-1)

        Returns:
            List of relevant documents with scores
        """
        if self.embeddings is None:
            raise RuntimeError("Knowledge base not loaded. Call load_from_markdown() or load_index() first.")

        # Generate query embedding
        query_embedding = self.model.encode([query])

        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Filter by minimum relevance
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= min_relevance:
                doc = self.documents[idx]
                results.append(KnowledgeBaseResult(
                    content=doc['content'],
                    relevance_score=score,
                    source_section=doc['title'],
                    url=doc.get('url')
                ))

        return results

    def search_with_fallback(self, query: str) -> Tuple[List[KnowledgeBaseResult], float]:
        """
        Search with automatic fallback to lower thresholds if no results.

        Returns:
            (results, confidence)
        """
        # Try with high threshold first
        results = self.search(query, top_k=3, min_relevance=0.7)
        if results:
            return results, 0.9  # High confidence

        # Try with medium threshold
        results = self.search(query, top_k=3, min_relevance=0.5)
        if results:
            return results, 0.6  # Medium confidence

        # Try with low threshold (last resort)
        results = self.search(query, top_k=2, min_relevance=0.3)
        if results:
            return results, 0.3  # Low confidence

        # No relevant results found
        return [], 0.0


# Test knowledge base
if __name__ == "__main__":
    import sys

    kb = KnowledgeBase()

    # Check if index exists
    if kb.index_file.exists():
        print("Loading existing index...")
        kb.load_index()
    else:
        # Load from markdown file
        docs_file = Path("../context/product-docs.md")
        if not docs_file.exists():
            print(f"Error: {docs_file} not found")
            sys.exit(1)

        kb.load_from_markdown(docs_file)

    # Test queries
    test_queries = [
        "How do I reset my password?",
        "GitHub integration not syncing",
        "What's included in Professional plan?",
        "How to export my data?",
        "Can I use CloudFlow offline?",
    ]

    print("\n" + "=" * 60)
    print("Knowledge Base Search Test")
    print("=" * 60)

    for query in test_queries:
        print(f"\nQuery: {query}")
        results, confidence = kb.search_with_fallback(query)

        if results:
            print(f"Confidence: {confidence:.2f}")
            print(f"Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.source_section} (score: {result.relevance_score:.2f})")
                print(f"   {result.content[:200]}...")
                print()
        else:
            print("❌ No relevant results found\n")
