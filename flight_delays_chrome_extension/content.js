class Flight {
    constructor(index, selector, dates, route_origin_airport, route_destination_airport) {
        this.index = index;
        this.selector = selector;
        this.text = $(selector).text().split(/\b\s+/);
        this.origin_airport = this.text[0].substring(5, 8);
        this.destination_airport = this.text[2].substring(5, 8);
    
        if (this.origin_airport == route_origin_airport) {
            this.origin_dt = new Date(dates[0]);    
            this.destination_dt = new Date(dates[1]);        
        }
        else {
            this.origin_dt = new Date(dates[1]);
            this.destination_dt = new Date(dates[0]);
        }
        let origin_time = this.text[0].substring(0, 5).split(":");
        console.log(origin_time);
        this.origin_dt.setHours(origin_time[0], origin_time[1]);
        let destination_time = this.text[2].substring(0, 5).split(":");
        console.log(destination_time);
        this.destination_dt.setHours(destination_time[0], destination_time[1]);

        if (this.text[2].substring(5, 7) === "+1") {
            console.log(this.destination_dt.getDate());
            this.destination_dt.setDate(this.destination_dt.getDate() + 1);
        }
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
        console.log($(value).attr('aria-label'));
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