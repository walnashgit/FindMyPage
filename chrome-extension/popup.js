document.addEventListener('DOMContentLoaded', function() {
  const queryInput = document.getElementById('query-input');
  // const submitBtn = document.getElementById('submit-btn');  // Commented out for future use
  const searchBtn = document.getElementById('search-btn');
  const responseContainer = document.getElementById('response-container');
  const addPageBtn = document.getElementById('add-page-btn');

  // Function to process a query and show results
  async function processQuery(query) {
    if (!query) {
      responseContainer.innerHTML = '<p style="color: red;">Please enter a query</p>';
      return;
    }

    // Display loading message
    responseContainer.innerHTML = '<p class="loading">Processing your query...</p>';

    try {
      // Send the query to our endpoint
      const response = await fetch('http://127.0.0.1:7172/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();
      
      // Display the response
      responseContainer.innerHTML = `<p><strong>Response:</strong></p><p>${data.result}</p>`;
      
    } catch (error) {
      console.error('Error:', error);
      responseContainer.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
  }
  
  // Function to handle search
  async function searchContent(query) {
    if (!query) {
      responseContainer.innerHTML = '<p style="color: red;">Please enter a search query</p>';
      return;
    }

    // Display loading message
    responseContainer.innerHTML = '<p class="loading">Searching indexed content...</p>';

    try {
      // Send the query to our search endpoint
      const response = await fetch('http://127.0.0.1:7172/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();
      
      // Display the search results
      if (data.error) {
        responseContainer.innerHTML = `<p style="color: red;">Search error: ${data.error}</p>`;
        return;
      }
      
      if (data.results.length === 0) {
        responseContainer.innerHTML = `<p>No results found for "${query}"</p><p>Try adding some pages first using the "Add Page" button.</p>`;
        return;
      }
      
      // Limit to top 3 results
      const limitedResults = data.results.slice(0, 3);
      
      let resultsHtml = `<h3>Top Results for "${query}":</h3>`;
      
      limitedResults.forEach(result => {
        const metadata = result.metadata;
        const title = metadata.title || metadata.url || "Unknown";
        const url = metadata.url || "#";
        
        resultsHtml += `
          <div class="search-result">
            <div class="search-result-title">${title}</div>
            <div class="search-result-url" data-url="${url}">${url}</div>
          </div>
        `;
      });
      
      responseContainer.innerHTML = resultsHtml;
      
      // Add event listeners to all URL elements after they're added to the DOM
      document.querySelectorAll('.search-result-url').forEach(element => {
        element.addEventListener('click', function() {
          const url = this.getAttribute('data-url');
          if (url) {
            chrome.tabs.create({ url: url });
          }
        });
      });
      
    } catch (error) {
      console.error('Error:', error);
      responseContainer.innerHTML = `<p style="color: red;">Search error: ${error.message}</p>`;
    }
  }

  // Handle Enter key press in the query input (acts like submit button)
  queryInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      // processQuery(queryInput.value.trim());  // Commented out for future use
      searchContent(queryInput.value.trim());
    }
  });

  // Commented out submit button functionality for future use
  /* 
  submitBtn.addEventListener('click', function() {
    processQuery(queryInput.value.trim());
  });
  */

  // Search button functionality
  searchBtn.addEventListener('click', function() {
    searchContent(queryInput.value.trim());
  });

  // Add page functionality
  addPageBtn.addEventListener('click', async function() {
    try {
      // Display loading message
      responseContainer.innerHTML = '<p class="loading">Adding current page to search index...</p>';
      
      // Request the page content from the background script
      chrome.runtime.sendMessage(
        { action: "getPageContent" },
        async function(response) {
          if (response.error) {
            responseContainer.innerHTML = `<p style="color: red;">Error: ${response.error}</p>`;
            return;
          }
          
          try {
            // Send the page content to the server
            const serverResponse = await fetch('http://127.0.0.1:7172/api/add-page', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                url: response.url,
                title: response.title,
                html: response.html
              })
            });
            
            if (!serverResponse.ok) {
              throw new Error(`Server responded with status: ${serverResponse.status}`);
            }
            
            const data = await serverResponse.json();
            
            // Display success message
            responseContainer.innerHTML = `<p style="color: green;">${data.message}</p>`;
          } catch (error) {
            console.error('Error sending to server:', error);
            responseContainer.innerHTML = `<p style="color: red;">Error adding page: ${error.message}</p>`;
          }
        }
      );
    } catch (error) {
      console.error('Error:', error);
      responseContainer.innerHTML = `<p style="color: red;">Error adding page: ${error.message}</p>`;
    }
  });
}); 