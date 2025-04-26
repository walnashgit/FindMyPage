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
}); 