console.log("Hello from background!");

chrome.runtime.onMessage.addListener(
    function(url, sender, onSuccess) {
        fetch(url)
            .then(response => response.json())
            .then(responseText => {
                console.log("background: received server response");
                onSuccess(responseText["result"]);
            });
        return true;
    }
);