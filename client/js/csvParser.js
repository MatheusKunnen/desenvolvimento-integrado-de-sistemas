function parseCSV(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();

        reader.onload = (event) => {
            const text = event.target.result;
            const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
            const result = lines.map(line => {
                return line.split(',').map(Number);
            }).flat();
            resolve(result);
        };

        reader.onerror = () => {
            reject('Error reading the CSV file.');
        };

        reader.readAsText(file);
    });
}

function checkSignalSize(signal) {
    if (signal.length == 27904) {
        return "2";
    } else if (signal.length == 50816) {
        return "1";
    } else {
        console.log("Error: Signal size is not correct.");
    }
}
