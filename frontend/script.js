const analyzeBtn = document.getElementById("analyzeBtn");

analyzeBtn.addEventListener("click", async function () {

    const problem = document.getElementById("problem").value;
    const code = document.getElementById("code").value;
    const language = document.getElementById("language").value;


    // Validation
    if (problem.trim() === "") {
        alert("Please enter the problem.");
        return;
    }

    if (code.trim() === "") {
        alert("Please enter your code.");
        return;
    }


    // Show result section
    document
        .getElementById("resultSection")
        .classList
        .remove("d-none");


    // Send code to FastAPI backend
    try {

        const response = await fetch("http://127.0.0.1:8000/analyze", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                problem: problem,
                code: code,
                language: language
            })
        });


        const result = await response.json();


        // Display backend result
        document.getElementById("approach").innerText =
            result.message;

        document.getElementById("pattern").innerText =
            "Analysis will be added later.";

        document.getElementById("timeComplexity").innerText =
            result.time_complexity;

        document.getElementById("spaceComplexity").innerText =
            result.space_complexity;

        document.getElementById("optimization").innerText =
            "Optimization suggestions will be added later.";

        document.getElementById("explanation").innerText =
            "Code analyzed successfully.";

    } catch (error) {

        console.error(error);

        alert("Unable to connect to the backend. Make sure FastAPI is running.");

    }

});

