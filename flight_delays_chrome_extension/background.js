console.log("Hello from background!");
//While predictions for flights within the next 15 days are computed based on real hourly  weather forecasts, later predictions are made on weather means based on historical weather. Still, airports and carriers still affect the predictions quite a lot so don\'t be discouraged :)\n Come back 15 days before your flight to get a clearer glimpse into the delays.
chrome.runtime.onMessage.addListener(
    function(message, sender, onSuccess) {
        if (message.type == 'notification') {
            console.log('notification');
            var notification_options = {
                type: 'basic',
                title: 'Something to know about these predictions',
                iconUrl: 'logo_24.png',
                message: 'Come back within 15 days before your flight to get even better predictions!'
            };
            chrome.notifications.create('', notification_options);
        }
        else {
            fetch(message.url)
                .then(response => response.json())
                .then(responseText => {
                    console.log("background: received server response");
                    onSuccess(responseText["result"]);
            });
            return true;
        }
    }
);