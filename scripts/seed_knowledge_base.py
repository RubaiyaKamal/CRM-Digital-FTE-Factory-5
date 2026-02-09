"""
Seed the knowledge_base table with embeddings from context/*.md files.

Usage:
    python scripts/seed_knowledge_base.py

Requires: DATABASE_URL and OPENAI_API_KEY in environment (or .env file).
"""
from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path
from typing import Optional

import asyncpg
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.environ["DATABASE_URL"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

CONTEXT_DIR = Path(__file__).parent.parent / "context"
MARKDOWN_FILES = [
    ("product-docs.md", "Product Documentation"),
    ("brand-voice.md", "Brand Voice Guidelines"),
    ("escalation-rules.md", "Escalation Rules"),
    ("company-profile.md", "Company Profile"),
]


def chunk_markdown(text: str, source_file: str, document_title: str) -> list[dict]:
    """Split markdown into sections at ## headings. Each section is one KB entry."""
    chunks = []

    # Split on ## headings (keep the heading)
    parts = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        lines = part.split("\n", 1)
        heading = lines[0].lstrip("#").strip() if lines[0].startswith("#") else ""
        content = lines[1].strip() if len(lines) > 1 else lines[0].strip()

        # Skip if too short to be useful
        if len(content) < 50:
            continue

        title = f"{document_title} — {heading}" if heading else document_title
        chunks.append(
            {
                "title": title[:500],
                "content": content[:8000],  # token limit safety
                "section": source_file,
            }
        )

    return chunks


async def embed_texts(client: AsyncOpenAI, texts: list[str]) -> list[list[float]]:
    """Batch-embed texts using text-embedding-3-small."""
    # OpenAI supports up to 2048 texts per request, max 8191 tokens each
    response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


async def seed():
    print(f"Connecting to database...")
    pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=3)
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    # Check existing count
    async with pool.acquire() as conn:
        existing = await conn.fetchval("SELECT COUNT(*) FROM knowledge_base")
        if existing > 0:
            print(f"Knowledge base already has {existing} entries.")
            answer = input("Re-seed (delete + reload)? [y/N]: ").strip().lower()
            if answer != "y":
                print("Aborted.")
                return
            await conn.execute("DELETE FROM knowledge_base")
            print("Cleared existing entries.")

    all_chunks = []
    for filename, doc_title in MARKDOWN_FILES:
        filepath = CONTEXT_DIR / filename
        if not filepath.exists():
            print(f"  SKIP {filename} (not found)")
            continue
        text = filepath.read_text(encoding="utf-8")
        chunks = chunk_markdown(text, filename, doc_title)
        print(f"  {filename}: {len(chunks)} chunks")
        all_chunks.extend(chunks)

    if not all_chunks:
        print("No chunks to embed.")
        return

    print(f"\nGenerating embeddings for {len(all_chunks)} chunks...")
    texts = [f"{c['title']}\n\n{c['content']}" for c in all_chunks]

    # Embed in batches of 50
    embeddings = []
    batch_size = 50
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        print(f"  Embedding batch {i // batch_size + 1}/{(len(texts) - 1) // batch_size + 1}...")
        batch_embeddings = await embed_texts(client, batch)
        embeddings.extend(batch_embeddings)

    print(f"\nInserting {len(all_chunks)} entries into knowledge_base...")
    async with pool.acquire() as conn:
        # Register vector type
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")

        for chunk, embedding in zip(all_chunks, embeddings):
            await conn.execute(
                """
                INSERT INTO knowledge_base (title, content, section, embedding)
                VALUES ($1, $2, $3, CAST($4 AS vector))
                """,
                chunk["title"],
                chunk["content"],
                chunk["section"],
                str(embedding),
            )

    async with pool.acquire() as conn:
        count = await conn.fetchval("SELECT COUNT(*) FROM knowledge_base")

    print(f"\nDone! Knowledge base now has {count} entries.")
    await pool.close()


if __name__ == "__main__":
    asyncio.run(seed())
