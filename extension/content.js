function getJobPageText() {
    const title = document.querySelector("h1")?.innerText || document.title;
    const bodyText = document.body.innerText.slice(0, 8000);
  
    return {
      title,
      text: bodyText,
      url: window.location.href,
    };
  }
  
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "GET_JOB_TEXT") {
      sendResponse(getJobPageText());
    }
  });