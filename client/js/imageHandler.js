function downloadImage() {
    const ctx = canvasElement.getContext('2d');
    // Set canvas dimensions to match the image
    canvasElement.width = jobImage.naturalWidth;
    canvasElement.height = jobImage.naturalHeight;
    
    // Draw the image onto the canvas
    ctx.drawImage(jobImage, 0, 0);

    // Convert the canvas content to a data URL (PNG format)
    const pngUrl = canvasElement.toDataURL('image/png');

    // Create a temporary link to trigger the download
    const link = document.createElement('a');
    link.href = pngUrl;
    link.download = 'image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link); // Clean up
}