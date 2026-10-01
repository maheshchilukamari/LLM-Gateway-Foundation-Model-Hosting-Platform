# RAG

The RAG pipeline ingests documents, chunks text, generates embeddings, stores vectors locally, retrieves top-k matching chunks, builds an augmented prompt, and routes generation through the same gateway execution path.

```mermaid
flowchart LR
    Docs[Documents] --> Chunker[Chunker]
    Chunker --> Embed[Embedding Model]
    Embed --> Store[Vector Store]
    Query[User Query] --> QueryEmbed[Query Embedding]
    QueryEmbed --> Search[Similarity Search]
    Store --> Search
    Search --> Prompt[Prompt Builder]
    Prompt --> Gateway[LLM Gateway]
```

The local implementation uses an in-memory vector store and deterministic local embeddings by default so tests and demos run without downloads. The configured embedding model is `sentence-transformers/all-MiniLM-L6-v2`, which can be used through the optional Hugging Face provider path.
