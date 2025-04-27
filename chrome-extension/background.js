// Background script for MCP Agent extension

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getPageContent") {
    // Get the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      if (!tabs || tabs.length === 0) {
        sendResponse({
          error: "No active tab found"
        });
        return;
      }
      
      const tab = tabs[0];
      
      try {
        // Execute script to get the page content
        const results = await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          function: () => {
            return {
              html: document.documentElement.outerHTML,
              title: document.title
            };
          }
        });
        
        // Send the response back with the page content and URL
        sendResponse({
          success: true,
          url: tab.url,
          title: results[0].result.title,
          html: results[0].result.html
        });
      } catch (error) {
        console.error("Error executing script:", error);
        sendResponse({
          error: error.message || "Failed to get page content"
        });
      }
    });
    
    // Return true to indicate that sendResponse will be called asynchronously
    return true;
  }
  
  // Handle opening URLs with search highlighting
  if (request.action === "openUrlWithHighlight") {
    const { url, searchTerms } = request;
    
    if (!url) {
      sendResponse({ error: "URL is required" });
      return;
    }
    
    // Create a URL with search terms parameter
    let urlToOpen = url;
    if (searchTerms && searchTerms.trim() !== '') {
      const separator = url.includes('?') ? '&' : '?';
      urlToOpen = `${url}${separator}smarthighlight=${encodeURIComponent(searchTerms)}`;
    }
    
    // Open the URL in a new tab
    chrome.tabs.create({ url: urlToOpen }, (tab) => {
      // We'll also send a message to the tab to highlight the search terms directly
      // This is a backup in case the URL parameter approach doesn't work
      chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo) {
        if (tabId === tab.id && changeInfo.status === 'complete') {
          // Remove this listener
          chrome.tabs.onUpdated.removeListener(listener);
          
          // Send message to content script to highlight terms
          setTimeout(() => {
            chrome.tabs.sendMessage(tab.id, {
              action: 'highlight',
              searchTerms: searchTerms
            }).catch(err => console.log("Content script may not be ready yet"));
          }, 500);
        }
      });
      
      sendResponse({ success: true, tab: tab.id });
    });
    
    return true;
  }
}); 