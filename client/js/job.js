async function submitForm() {
    // Get form values
    const user = document.getElementById("user").value;
    const useGain = document.getElementById("useGain").checked;
    const model = parseInt(document.getElementById("model").value);
    const signalFile = document.getElementById("signalFile").files[0];

    // Ensure a file was selected
    if (!signalFile) {
        alert('Please upload a CSV file for the signal.');
        return;
    }

    try {
        // Parse the CSV file into an array
        const signal = await parseCSV(signalFile);

        // Create the request object
        const requestData = {
            user: user,
            use_gain: useGain,
            model: model,
            signal: signal
        };

        // Display the request data
        // document.getElementById("output").textContent = JSON.stringify(requestData, null, 2);

        // Make an API call to submit the job
        const response = await submitJobRequest(requestData);

        // Display the response data (job_id)
        document.getElementById("response").textContent = response.data.job_id;

        // Poll for job status
        pollJobStatus(response.data.job_id);
    } catch (error) {
        console.error('Error processing the form:', error);
        document.getElementById("response").textContent = 'An error occurred while processing the form.';
    }
}
async function fetchJobDetails(jobId) {
    try {
        const response = await getJobDetails(jobId);
        document.getElementById("jobDetails").textContent = JSON.stringify(response, null, 2);
    } catch (error) {
        console.error('Error fetching job details:', error);
        document.getElementById("jobDetails").textContent = 'An error occurred while fetching job details.';
    }
}

async function fetchJobImage(jobId) {
    try {
        const imageUrl = await fetchJobImage(jobId);
        document.getElementById("jobImage").src = imageUrl;
    } catch (error) {
        console.error('Error fetching job image:', error);
        document.getElementById("jobImage").alt = 'An error occurred while fetching job image.';
    }
}