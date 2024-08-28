const baseUrl = 'http://localhost:5005';

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

async function getJobStatus(jobId) {
    const response = await fetch(`${baseUrl}/job/${jobId}?minimal=true`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch job status');
    }

    return await response.json(); // Should return { status: 'pending' | 'done' }
}

async function getJobDetails(jobId) {
    const response = await fetch(`${baseUrl}/job/${jobId}`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch job details');
    }

    return await response.json(); // Should return job details
}

async function getJobImage(jobId) {
    const response = await fetch(`${baseUrl}/job/image/${jobId}`, {
        method: 'GET',
    });

    if (!response.ok) {
        throw new Error('Failed to fetch job image');
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob); // Create a URL for the image blob
}