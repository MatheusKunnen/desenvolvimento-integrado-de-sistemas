const baseUrl = 'http://localhost:5005'; // Replace with your actual base URL if needed

// Submit a job request
async function submitJobRequest(requestData) {
    const response = await fetch(`${baseUrl}/job`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
    });

    if (!response.ok) {
        throw new Error('Failed to submit job request');
    }

    return await response.json(); // Should return { job_id: string }
}

// Check job status
async function getJobStatus(jobId) {
    const response = await fetch(`${baseUrl}/job/${jobId}?minimal=true`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch job status');
    }

    // console.log(response);
    return await response.json(); // Should return { status: 'pending' | 'done' }
}

// Fetch job details
async function fetchJobDetails(jobId) {
    const response = await fetch(`${baseUrl}/job/${jobId}`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch job details');
    }

    return await response.json(); // Should return job details as specified
}

// Fetch job image
async function fetchJobImage(jobId) {
    const response = await fetch(`${baseUrl}/job/image/${jobId}`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch job image');
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob); // Create a URL for the image blob
}