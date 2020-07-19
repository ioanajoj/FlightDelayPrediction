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
    constructor(selector, dates, route_origin_airport) {
        this.selector = selector;
        this.raw_text = $(selector).text();
        this.text = $(selector).text().split(/\b\s+/);
        if (this.text[0].includes("Direct")) {
            this.text[2] = this.text[1];
            this.text[1] = "00Direct";
        }
        this.extra_day = this.text[2].substring(5, 7) === "+1";
        
        this.set_airports();
        this.set_datetimes(dates, route_origin_airport);     
        this.set_carrier();
        
        this.request_delay();
    }

    set_airports() {
        this.origin_airport = this.text[0].substring(5, 8);
        if (this.extra_day) {
            this.destination_airport = this.text[2].substring(7, 10);
        }
        else {
            this.destination_airport = this.text[2].substring(5, 8);
        }
    }

    set_datetimes(dates, route_origin_airport) {
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

        if (this.extra_day) {
            this.destination_dt.setDate(this.destination_dt.getDate() + 1);
        }
    }
    
    set_carrier() {
        this.carrier_code = carriers[$(this.selector).find("img").attr("alt")];  

        // cover 'Operated by' case
        if (this.carrier_code == undefined) {
            let raw_text = $(this.selector).text();
            if (raw_text.includes("Operated by American Airlines")) {
                this.carrier_code = carriers["American Airlines"];
            }
            else if (raw_text.includes("Operated by Delta")) {
                this.carrier_code = carriers["Delta"];
            }
        } 
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

    on_get_response = function(response, sender, sendResponse) {
        // console.log("from content: " + response);
        var some_span = document.createElement('span');
        some_span.innerHTML = "This flight has " + Math.round(parseFloat(response) * 100) + "% chances to be delayed.";
        some_span.setAttribute("class", "delay_tooltiptext");

        let tooltip = $(this.selector).addClass("delay_tooltip");
        $(tooltip).append(some_span);
    }

    request_delay() {
        var params = this.get_params();
        if (params["carrier_code"]) {
            params = $.param(params);

            let url = 'http://127.0.0.1:8000/predict/?' + params; 
            chrome.runtime.sendMessage(
                {url: url},
                this.on_get_response.bind(this)
            );
        }
    }
}

var dates = [], origin_airport, destination_airport;

function waitForElementToDisplay(selector, time, callback) {
    if(document.querySelector(selector) != null && document.querySelector(selector).length != 0) {
        callback();
        return;
    }
    else {
        setTimeout(function() {
            waitForElementToDisplay(selector, time, callback);
        }, time);
    }
}

function check_dates() {
    chrome.runtime.sendMessage({type: 'notification'});
    //chrome.notifications.create('limitNotif', notification_options);
}

function get_dates() {
    elems = $("[id='datepicker']");
    $.each(elems, function(index, value) {
        dates.push(new Date($(value).attr('aria-label')));
    });
    check_dates();
}

function get_airports() {
    route = $("#flights-search-summary-root > div > section > div.searchDetailsNudgerContainer-3NQaR > div > span").text();
    airports = [...route.matchAll(/\(([A-Z]*)\)/g)];
    origin_airport = airports[0][1];
}

function get_summary() {
    get_dates();
    get_airports();
}

function get_flights() {
    flights_selector = $("*[class^=LegDetails]");
    flights = []
    $.each(flights_selector, function (index, value) {
        if ($(value).text().includes("Direct"))
            flights.push(new Flight(value, dates, origin_airport));
    })
    console.log(flights);
}

function handle_mutations(mutations) {
    mutations.forEach(function(mutation) {
        for (var i = 0; i < mutation.addedNodes.length; i++)
            if (mutation.addedNodes.length) {
                for (mut of mutation.addedNodes) {
                    let new_flights = $(mut).find("[class^=LegDetails]");
                    for (flight of new_flights) {
                        if ($(flight).text().includes("Direct"))
                            flights.push(new Flight(flight, dates, origin_airport));
                    }
                }
            }
        })
}

function observe_flights() {
    var observer = new MutationObserver(handle_mutations);
    let result_list = $(".Results_dayViewItems__3dVwy");
    observer.observe(result_list[0], { childList: true });
}

$(document).ready(function() {
    elems = $("[id='datepicker']");

    waitForElementToDisplay("[id='datepicker']", 100, get_summary);
    waitForElementToDisplay("*[class^=LegDetails]", 100, get_flights);
    waitForElementToDisplay("*[class^=LegDetails]", 100, observe_flights);
});
