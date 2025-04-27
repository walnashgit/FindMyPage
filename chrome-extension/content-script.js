// Content script to highlight search terms on a page

// Function to create a wrapper for text nodes
function wrapTextWithHighlight(textNode, searchTerm) {
  const text = textNode.nodeValue;
  const regex = new RegExp(searchTerm, 'gi');
  
  if (!regex.test(text)) return;
  
  const parent = textNode.parentNode;
  if (!parent) return;
  
  // If parent is already a highlight, don't re-highlight
  if (parent.className === 'smart-bookmark-highlight') return;
  
  // Create a fragment to hold the new nodes
  const fragment = document.createDocumentFragment();
  let lastIndex = 0;
  let match;
  
  // Reset regex state
  regex.lastIndex = 0;
  
  // Find and wrap all matches
  while ((match = regex.exec(text)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      fragment.appendChild(document.createTextNode(text.substring(lastIndex, match.index)));
    }
    
    // Create highlighted span for the match
    const highlightSpan = document.createElement('span');
    highlightSpan.className = 'smart-bookmark-highlight';
    highlightSpan.style.backgroundColor = '#FFFF00';
    highlightSpan.style.color = '#000000';
    highlightSpan.appendChild(document.createTextNode(match[0]));
    fragment.appendChild(highlightSpan);
    
    lastIndex = regex.lastIndex;
  }
  
  // Add any remaining text
  if (lastIndex < text.length) {
    fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
  }
  
  // Replace the original text node with the fragment
  parent.replaceChild(fragment, textNode);
}

// Function to traverse DOM and highlight text
function highlightSearchTerms(searchTerms) {
  if (!searchTerms || searchTerms.trim() === '') return;
  
  // Create a style element for the highlights
  const style = document.createElement('style');
  style.textContent = `
    .smart-bookmark-highlight {
      background-color: #FFFF00;
      color: #000000;
      border-radius: 2px;
      box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.1);
    }
  `;
  document.head.appendChild(style);
  
  // Terms to highlight (split by spaces, remove empty)
  const terms = searchTerms.split(' ').filter(term => term.length > 2);
  
  // Function to walk the DOM tree
  function walkDom(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      // For text nodes, check and highlight each term
      terms.forEach(term => wrapTextWithHighlight(node, term));
    } else {
      // Skip nodes that shouldn't be modified
      const tagName = node.tagName && node.tagName.toLowerCase();
      if (tagName === 'script' || tagName === 'style' || tagName === 'noscript') {
        return;
      }
      
      // Recursively process child nodes (make a copy as the DOM might change)
      const children = Array.from(node.childNodes);
      children.forEach(walkDom);
    }
  }
  
  // Start processing from the body
  walkDom(document.body);
  
  // Scroll to the first highlight
  const firstHighlight = document.querySelector('.smart-bookmark-highlight');
  if (firstHighlight) {
    firstHighlight.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    });
  }
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'highlight' && request.searchTerms) {
    // Delay slightly to ensure page is fully loaded
    setTimeout(() => {
      highlightSearchTerms(request.searchTerms);
      sendResponse({ success: true, count: document.querySelectorAll('.smart-bookmark-highlight').length });
    }, 300);
    return true; // Keep the message channel open for the async response
  }
});

// Check URL parameters for search terms on initial load
const urlParams = new URLSearchParams(window.location.search);
const searchTerms = urlParams.get('smarthighlight');
if (searchTerms) {
  // Remove the parameter from the URL without reloading
  const newUrl = window.location.href.replace(/[\?&]smarthighlight=[^&]+/, '');
  window.history.replaceState({}, document.title, newUrl);
  
  // Wait for page to load before highlighting
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(() => highlightSearchTerms(searchTerms), 300);
    });
  } else {
    setTimeout(() => highlightSearchTerms(searchTerms), 300);
  }
} 