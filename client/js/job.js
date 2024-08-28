async function submitForm() {
    const user = document.getElementById("user").value;
    const useGain = document.getElementById("useGain").checked;
    const signalFile = document.getElementById("signalFile").files[0];

    if (!signalFile) {
        alert('Please upload a CSV file for the signal.');
        return;
    }

    try {
        const signal = await parseCSV(signalFile);
        const model = checkSignalSize(signal);

        const requestData = {
            user: user,
            use_gain: useGain,
            model: model,
            signal: signal
        };

        const response = await submitJobRequest(requestData);
        document.getElementById("response").textContent = response.data.job_id;
        pollJobStatus(response.data.job_id);
    } catch (error) {
        console.error('Error processing the form:', error);
        document.getElementById("response").textContent = 'An error occurred while processing the form.';
    }
}

async function fetchJobDetails(jobId) {
    try {
        const response = await getJobDetails(jobId);
        document.getElementById("jobDetails").textContent = JSON.stringify(response.data, null, 2);
    } catch (error) {
        console.error('Error fetching job details:', error);
        document.getElementById("jobDetails").textContent = 'An error occurred while fetching job details.';
    }
}

async function fetchJobImage(jobId) {
    try {
        const response = await getJobImage(jobId);
        console.log(response);
        document.getElementById("jobImageText").textContent = response;
        document.getElementById("jobImage").src = response;
    } catch (error) {
        console.error('Error fetching job image:', error);
        document.getElementById("jobImage").alt = 'An error occurred while fetching job image.';
    }
}