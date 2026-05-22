const grabBtn = document.getElementById("grabBtn");
const openBtn = document.getElementById("openBtn");
const jobText = document.getElementById("jobText");

grabBtn.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.tabs.sendMessage(tab.id, { type: "GET_JOB_TEXT" }, (response) => {
    if (response) {
      jobText.value = response.text;
      chrome.storage.local.set({ fastcover_job_text: response.text });
    }
  });
});

openBtn.addEventListener("click", () => {
  const text = encodeURIComponent(jobText.value);
  chrome.tabs.create({
    url: `http://localhost:5173/?job=${text}`
  });
});