async function pollJobStatus(jobId) {
    const statusElement = document.getElementById("jobStatus");

    const checkStatus = async () => {
        try {
            const response = await getJobStatus(jobId);
            // console.log(jobId);
            // console.log(response);

            // Update the status in the UI
            statusElement.textContent = `Job ID: ${jobId}\nStatus: ${response.data.status}`;

            if (response.data.status === 'done') {
                clearInterval(pollingInterval);
                statusElement.textContent += "\nJob completed successfully!";
                await fetchJobDetails(jobId);
                await fetchJobImage(jobId);
            }
        } catch (error) {
            console.error('Error checking job status:', error);
            statusElement.textContent = 'An error occurred while checking job status.';
        }
    };

    const pollingInterval = setInterval(checkStatus, 2000);
}