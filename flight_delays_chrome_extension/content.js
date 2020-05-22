let carriers = {
    "American Airlines": "AA",
    "Alaska Airlines": "AS",
    "jetBlue": "B6",
    "Delta": "DL",
    "Frontier Airlines": "F9",
    "Allegiant Air": "G4",
    "Hawaiian Airlines": "HA",
    "Spirit Airlines": "NK",
    "United": "UA",
    "Southwest Airlines": "WN"
}

class Flight {
    constructor(index, selector, dates, route_origin_airport, route_destination_airport) {
        this.index = index;
        this.selector = selector;
        this.text = $(selector).text().split(/\b\s+/);
        this.origin_airport = this.text[0].substring(5, 8);

        let extra_day = this.text[2].substring(5, 7) === "+1";
        if (extra_day) {
            this.destination_airport = this.text[2].substring(7, 10);
        }
        else {
            this.destination_airport = this.text[2].substring(5, 8);
        }
        
    
        if (this.origin_airport == route_origin_airport) {
            this.origin_dt = new Date(dates[0]);    
            this.destination_dt = new Date(dates[0]);        
        }
        else {
            this.origin_dt = new Date(dates[1]);
            this.destination_dt = new Date(dates[1]);
        }
        let origin_time = this.text[0].substring(0, 5).split(":");
        this.origin_dt.setHours(origin_time[0], origin_time[1]);
        let destination_time = this.text[2].substring(0, 5).split(":");
        this.destination_dt.setHours(destination_time[0], destination_time[1]);

        if (extra_day) {
            this.destination_dt.setDate(this.destination_dt.getDate() + 1);
        }

        this.carrier_code = carriers[$(this.selector).find("img").attr("alt")];   

        this.request_delay();
    }

    get_params() {
        var params = {}
        params["carrier_code"] = this.carrier_code;
        params["origin_airport"] = this.origin_airport;
        params["destination_airport"] = this.destination_airport;
        params["origin_dt"] = moment(this.origin_dt).format("DD/MM/YY HH:MM");
        params["destination_dt"] = moment(this.destination_dt).format("DD/MM/YY HH:MM");
        return params;
    }

    request_delay() {
        var params = this.get_params();
        if (params["carrier_code"]) {
            params = $.param(params);

            let url = 'http://127.0.0.1:8000/predict/?' + params; 
            chrome.runtime.sendMessage(
                url,
                this.handle_response
          );

            // fetch('http://127.0.0.1:8000/predict/?' + params)
            // .then(r => console.log(r))
            // .then(result => {
            //     console.log("Result: " + result);
            // })
        }
    }

    handle_response(response) {
        console.log(response);
    }
}

var dates = [], origin_airport, destination_airport;

function waitForElementToDisplay(selector, time, callback) {
    if(document.querySelector(selector) != null && document.querySelector(selector).length != 0) {
        console.log("The element is displayed, you can put your code instead of this alert.");
        callback();
        return;
    }
    else {
        console.log("Start timeout");
        setTimeout(function() {
            waitForElementToDisplay(selector, time, callback);
        }, time);
    }
}

function get_dates() {
    console.log("Get dates");
    elems = $("[id='datepicker']");
    $.each(elems, function(index, value) {
        dates.push(new Date($(value).attr('aria-label')));
    });
    console.log("Dates ready: " + dates);
}

function get_airports() {
    console.log("Get airports");
    route = $("#flights-search-summary-root > div > section > div.searchDetailsNudgerContainer-3NQaR > div > span").text();
    console.log("route: " + route);
    airports = [...route.matchAll(/\(([A-Z]*)\)/g)];
    console.log(airports);
    origin_airport = airports[0][1];
    destination_airport = airports[1][1];
    console.log("Airports done: " + origin_airport + " " + destination_airport);
}

function get_summary() {
    get_dates();
    get_airports();
}

function get_flights() {
    console.log("Get flights");
    flights_selector = $("*[class^=LegDetails]");
    flights = []
    $.each(flights_selector, function (index, value) {
        if ($(value).text().includes("Direct"))
            flights.push(new Flight(index, value, dates, origin_airport, destination_airport));
    })
    console.log(flights);
}

$(document).ready(function() {
    console.log("Document ready");
    // $.getScript("domain.js", function() {console.log("Loaded model file");});
    elems = $("[id='datepicker']");
    console.log(elems);
    waitForElementToDisplay("[id='datepicker']", 100, get_summary);
    waitForElementToDisplay("*[class^=LegDetails]", 100, get_flights);
});