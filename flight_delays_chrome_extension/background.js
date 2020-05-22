console.log("Hello from background!");

chrome.runtime.onMessage.addListener(
    function(url, onSuccess) {
        fetch(url)
            .then(response => response.json())
            .then(responseText => onSuccess(responseText))

        return true;  // Will respond asynchronously.
    }
);