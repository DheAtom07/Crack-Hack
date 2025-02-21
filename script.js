async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const resultText = document.getElementById("result");
    const history = document.getElementById("history");
    const progressBar = document.querySelector(".progress-bar");
    const progress = document.getElementById("progress");

    if (fileInput.files.length === 0) {
        resultText.innerText = "⚠️ Please select a file!";
        return;
    }

    const file = fileInput.files[0];

    // Ensure only .exe files are uploaded
    if (!file.name.endsWith(".exe")) {
        resultText.innerText = "❌ Only .exe files are allowed!";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Show progress bar
    progressBar.style.display = "block";
    progress.style.width = "0%";

    try {
        const response = await fetch("http://127.0.0.1:8000/scan/", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("File upload failed");
        }

        const data = await response.json();
        resultText.innerHTML = `✅ Scan Result: <strong>${data.verdict}</strong>`;

        // Add file to scan history
        const listItem = document.createElement("li");
        listItem.textContent = `File: suspicious_file.exe - Verdict: ${data.verdict}`;
        history.appendChild(listItem);

        // Animate progress bar
        progress.style.width = "100%";

    } catch (error) {
        resultText.innerText = "❌ Error scanning file.";
    }
}
