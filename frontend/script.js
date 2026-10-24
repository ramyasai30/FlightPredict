
const flightForm = document.getElementById("flightForm");
const predictButton = document.getElementById("predictButton");
const resultCard = document.getElementById("resultCard");

const originInput = document.getElementById("origin");
const destinationInput = document.getElementById("destination");
const routeInput = document.getElementById("route");

async function loadDropdownOptions() {
    try {
                const options = AIRPORT_OPTIONS;

        function populateDropdown(id, values, placeholder) {
            const dropdown = document.getElementById(id);

            dropdown.innerHTML = "";

            const defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = placeholder;
            defaultOption.disabled = true;
            defaultOption.selected = true;

            dropdown.appendChild(defaultOption);

            values.forEach(item => {
    const option = document.createElement("option");

    if (typeof item === "string") {
        option.value = item;
        option.textContent = item;
    } else {
        option.value = item.value;
        option.textContent = item.label;
    }

    dropdown.appendChild(option);
});
        }

        const airlineNames = {
    AA: "American Airlines",
    AS: "Alaska Airlines",
    B6: "JetBlue Airways",
    DL: "Delta Air Lines",
    EV: "Atlantic Southeast Airlines",
    F9: "Frontier Airlines",
    HA: "Hawaiian Airlines",
    MQ: "American Eagle Airlines",
    NK: "Spirit Airlines",
    OO: "SkyWest Airlines",
    UA: "United Airlines",
    US: "US Airways",
    VX: "Virgin America",
    WN: "Southwest Airlines"
};

populateDropdown(
    "airline",
    options.airlines.map(code => ({
        value: code,
        label: `${airlineNames[code] || code} (${code})`
    })),
    "Select airline"
);
                const airportOptions = AIRPORT_DISPLAY_OPTIONS;

populateDropdown(
    "origin",
    airportOptions.origin_airports,
    "Select origin airport"
);

populateDropdown(
    "destination",
    airportOptions.destination_airports,
    "Select destination airport"
);

        updateRoute();

        console.log("Dropdown options loaded successfully.");
    } catch (error) {
        console.error("Dropdown loading error:", error);
        alert(
            "Could not load dropdown options. Check the browser console."
        );
    }
}

loadDropdownOptions();

// Automatically construct the route when airport codes change.
function updateRoute() {
    const origin = originInput.value.trim().toUpperCase();
    const destination = destinationInput.value.trim().toUpperCase();

    if (origin && destination) {
        routeInput.value = `${origin}_${destination}`;
    } else {
        routeInput.value = "";
    }
}

originInput.addEventListener("change", updateRoute);
destinationInput.addEventListener("change", updateRoute);

// Normalize text codes before sending them to the backend.
function getFlightData() {
    return {
        MONTH: Number(document.getElementById("month").value),
        DAY: Number(document.getElementById("day").value),
        DAY_OF_WEEK: Number(document.getElementById("dayOfWeek").value),

        AIRLINE: document.getElementById("airline").value.trim().toUpperCase(),
        ORIGIN_AIRPORT: originInput.value.trim().toUpperCase(),
        DESTINATION_AIRPORT: destinationInput.value.trim().toUpperCase(),

        DISTANCE: Number(document.getElementById("distance").value),

        DEP_HOUR: Number(document.getElementById("depHour").value),
        DEP_MINUTE: Number(document.getElementById("depMinute").value),

        ARR_HOUR: Number(document.getElementById("arrHour").value),
        ARR_MINUTE: Number(document.getElementById("arrMinute").value),

        IS_WEEKEND: Number(document.getElementById("weekend").value),

        ROUTE: routeInput.value.trim().toUpperCase()
    };
}

function showMessage(title, message) {
    resultCard.hidden = false;

    document.getElementById("resultBadge").textContent = "NOTICE";
    document.getElementById("resultBadge").className = "result-badge";

    document.getElementById("predictionText").textContent = title;
    document.getElementById("resultDescription").textContent = message;
    document.getElementById("probabilityText").textContent = "--.--%";
    document.getElementById("probabilityFill").style.width = "0%";

    resultCard.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}

flightForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    if (!flightForm.reportValidity()) {
        return;
    }

    const flightData = getFlightData();

    if (flightData.ORIGIN_AIRPORT === flightData.DESTINATION_AIRPORT) {
        showMessage(
            "Check your route",
            "Origin and destination airports must be different."
        );
        return;
    }

    if (!/^[A-Z0-9]+$/.test(flightData.AIRLINE)) {
        showMessage(
            "Check airline code",
            "Enter a valid airline code using letters or numbers."
        );
        return;
    }

    if (
        !/^[A-Z0-9]+$/.test(flightData.ORIGIN_AIRPORT) ||
        !/^[A-Z0-9]+$/.test(flightData.DESTINATION_AIRPORT)
    ) {
        showMessage(
            "Check airport codes",
            "Enter airport codes using letters or numbers."
        );
        return;
    }

    
predictButton.disabled = true;
predictButton.textContent = "Predicting...";

try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(flightData)
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || "Prediction failed.");
    }

    resultCard.hidden = false;

    const isDelayed = result.prediction === "DELAYED";

    const badge = document.getElementById("resultBadge");
    badge.textContent = isDelayed ? "DELAY RISK" : "ON-TIME OUTLOOK";
    badge.className = `result-badge ${isDelayed ? "delayed" : "not-delayed"}`;

    document.getElementById("predictionText").textContent =
        result.prediction === "DELAYED"
            ? "Delay predicted"
            : "No delay predicted";

    document.getElementById("resultDescription").textContent =
    `Flagged as a delay risk when the estimated probability is at least ${(result.threshold * 100).toFixed(0)}%.`;

    document.getElementById("probabilityText").textContent =
        `${Number(result.delay_probability).toFixed(2)}%`;

    document.getElementById("probabilityFill").style.width =
        `${Math.max(0, Math.min(100, Number(result.delay_probability)))}%`;
    

    resultCard.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

} catch (error) {
    showMessage(
        "Prediction unavailable",
        error.message || "Could not connect to the prediction server. Make sure Flask is running."
    );
    console.error("Prediction error:", error);

} finally {
    predictButton.disabled = false;
    predictButton.textContent = "Predict Flight Delay";
}

});
document.getElementById("dayOfWeek").addEventListener("change", function () {
    document.getElementById("weekend").value =
        (this.value === "6" || this.value === "7") ? "1" : "0";
});