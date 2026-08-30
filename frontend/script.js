const API_URL = "http://127.0.0.1:8000";


// --------------------------------------------------
// DOM elements
// --------------------------------------------------

const textInput = document.getElementById("textInput");

const characterCount =
    document.getElementById("characterCount");

const summarizeButton =
    document.getElementById("summarizeButton");

const loading =
    document.getElementById("loading");

const errorMessage =
    document.getElementById("errorMessage");

const resultSection =
    document.getElementById("resultSection");

const summaryOutput =
    document.getElementById("summaryOutput");


// --------------------------------------------------
// Character counter
// --------------------------------------------------

textInput.addEventListener("input", () => {

    const count = textInput.value.length;

    characterCount.textContent =
        `${count} / 20,000`;

});


// --------------------------------------------------
// Summarize function
// --------------------------------------------------

async function summarizeText() {

    const text = textInput.value.trim();


    // Validate input

    if (text.length < 20) {

        showError(
            "Please enter at least 20 characters."
        );

        return;
    }


    // Reset UI

    hideError();

    resultSection.classList.add("hidden");

    loading.classList.remove("hidden");

    summarizeButton.disabled = true;


    try {

        const response = await fetch(
            `${API_URL}/summarize`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    text: text
                })
            }
        );


        const data = await response.json();


        // Handle API error

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Something went wrong."
            );

        }


        // Display summary

        summaryOutput.textContent =
            data.summary;

        resultSection.classList.remove(
            "hidden"
        );


    } catch (error) {

        console.error(error);

        showError(
            error.message ||
            "Unable to connect to the server."
        );


    } finally {

        loading.classList.add("hidden");

        summarizeButton.disabled = false;

    }

}


// --------------------------------------------------
// Copy summary
// --------------------------------------------------

async function copySummary() {

    const summary =
        summaryOutput.textContent;


    if (!summary) {
        return;
    }


    try {

        await navigator.clipboard.writeText(
            summary
        );


        const button =
            document.getElementById("copyButton");

        const oldText =
            button.textContent;


        button.textContent = "Copied!";


        setTimeout(() => {

            button.textContent = oldText;

        }, 1500);


    } catch (error) {

        console.error(
            "Copy failed:",
            error
        );

    }

}


// --------------------------------------------------
// Error functions
// --------------------------------------------------

function showError(message) {

    errorMessage.textContent = message;

    errorMessage.classList.remove(
        "hidden"
    );

}


function hideError() {

    errorMessage.classList.add(
        "hidden"
    );

}