# Smar Bookmarks Chrome Extension

A Chrome extension to communicate with the MCP server and interact with its tools.

## Features

1. **Page Indexing**: Add web pages to your search index for later retrieval
2. **Search**: Search through previously indexed web pages

## Setup Instructions

1. **Start the MCP Server**
   ```
   cd path/to/your/project
   python mcp/mcp_server.py sse
   ```

2. **Load the Chrome Extension**
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in the top-right corner)
   - Click "Load unpacked" and select the `chrome-extension` directory
   - The Smar Bookmarks extension should now be visible in your extensions list

3. **Use the Extension**
   - Click on the Smar Bookmarks icon in your Chrome toolbar to open the popup
   
   
   **To Add a Page to Your Index:**
   - Navigate to the web page you want to add
   - Click on the Smar Bookmarks icon to open the popup
   - Click the "Add Page" button in the top-right corner
   - Wait for the confirmation message
   
   **To Search Indexed Content:**
   - Enter your search terms in the text area
   - Click the "Search" button
   - View the search results showing content from previously indexed pages

## Notes

- The MCP server must be running at http://127.0.0.1:7172 for the extension to work
- This extension requires permission to communicate with your local server and access page content
- For security reasons, keep the extension in development mode and don't distribute it publicly
- Indexed content is stored in the `mcp/faiss_index` directory

## Troubleshooting

- If you encounter connection errors, ensure the MCP server is running
- Check the Chrome console for error messages (right-click extension popup → Inspect)
- Make sure your firewall or security software isn't blocking local connections
- If search returns no results, try adding some pages first using the "Add Page" button 