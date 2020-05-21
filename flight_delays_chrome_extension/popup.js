document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('button').addEventListener('click', onclick, false)
        function onclick() {
            chrome.tabs.executeScript({file: 'jquery-3.5.1.min.js'},function() {
                var carrier_code = document.getElementById("carrier_code").value;
                var origin_airport = document.getElementById("origin_airport").value;
                var destination_airport = document.getElementById("destination_airport").value;
                var origin_dt = document.getElementById("origin_dt").value;
                var destination_dt = document.getElementById("destination_dt").value;
                chrome.runtime.sendMessage({
                    method: 'GET',
                    action: 'xhttp',
                    url: 'http://127.0.0.1:8000/predict',
                    data: {
                        carrier_code: carrier_code, 
                        origin_airport: origin_airport, destination_airport: destination_airport,
                        origin_dt: origin_dt, destination_dt: destination_dt
                    }
                }, function(data) {
                    var node = document.createElement("p");                 // Create a <li> node
                    var textnode = document.createTextNode("Result: " + data);         // Create a text node
                    node.appendChild(textnode);                              // Append the text to <li>
                    document.getElementById("body").appendChild(node);
                });
            });
        }
}, false)