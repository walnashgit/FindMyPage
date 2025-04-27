# Smart Bookmarks System

A semantic search system that allows you to index and search web pages using natural language processing. This project combines a backend server based on MCP (Model Capability Protocol) with a Chrome extension frontend.

## System Overview

This project consists of two main components:

1. **MCP Server**: A Python-based server that processes web content, creates semantic embeddings, and provides search capabilities using FAISS vector indexing.

2. **Chrome Extension**: A browser extension that allows users to capture web pages for indexing and perform semantic searches on previously captured content.

## How It Works

The system enables you to build a personal knowledge base of web pages:

1. The MCP server processes HTML content from web pages, breaking it into chunks
2. These chunks are converted into vector embeddings using nomic-embed-text model running locally in ollama.
3. The embeddings are stored in a FAISS index for efficient similarity search
4. The Chrome extension provides a user-friendly interface to add pages and search your index
5. Search results link directly back to the original web pages with search terms automatically highlighted

## Technical Stack

- **Backend**: Python, FastAPI, FAISS vector database, nomic-embed-text for embedding, gemini-2.0-flash as llm
- **Frontend**: Chrome Extension (HTML, CSS, JavaScript)
- **Communication**: JSON over HTTP
- **Processing**: HTML parsing, text chunking, vector embeddings

## Setup Instructions

### MCP Server Setup

1. **Install dependencies**:
   ```
   uv add -r requirements.txt
   ```

2. **Start the server**:
   ```
   uv run mcp/mcp_server.py sse
   ```

3. The server will run at `http://127.0.0.1:7172`

### Chrome Extension Setup

For details on setting up and using the Chrome extension, see the [Chrome Extension README](chrome-extension/README.md).

## Directory Structure

```
.
├── mcp/                # MCP server code
│   ├── mcp_server.py   # Main server application
│   ├── agent.py        # Agent for processing queries
│   ├── agent_service.py # Service for handling API requests
│   └── faiss_index/    # Storage for indexed content
├── chrome-extension/   # Chrome extension files
│   ├── manifest.json   # Extension configuration
│   ├── popup.html      # Extension UI
│   ├── popup.js        # Extension functionality
│   ├── content-script.js # Handles search term highlighting
│   └── README.md       # Extension documentation
└── README.md           # This file
```

## Features

- **Semantic Search**: Find content based on meaning, not just keywords
- **Web Page Indexing**: Add any web page to your personal search index
- **Simple User Interface**: Easy-to-use Chrome extension
- **Fast Retrieval**: Efficient vector similarity search using FAISS
- **Search Highlighting**: Automatically highlights search terms in the page when viewing results

## Development

The MCP server exposes several API endpoints:

- `/api/query`: Process natural language queries
- `/api/search`: Search the FAISS index
- `/api/add-page`: Add a new web page to the index

## Demo

Watch a demo of the Smart Bookmarks in action:

[![Smart Bookmark Demo](https://img.youtube.com/vi/JKx7mAa_bIY/0.jpg)](https://youtu.be/G1thktyJHnQ)

## License

This project is intended for educational and personal use.

## Acknowledgments

This project uses several open-source technologies:
- FAISS for efficient similarity search
- FastAPI for API development
- Chrome Extensions API for browser integration
