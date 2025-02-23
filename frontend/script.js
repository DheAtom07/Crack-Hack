async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const resultText = document.getElementById("result");

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

    try {
        const response = await fetch("http://backend:8000/upload/", {  // Use "backend" (service name in Docker)
            method: "POST",
            body: formData,
        });
        

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        const data = await response.json();
        resultText.innerHTML = `✅ Scan Result: <strong>${data.verdict}</strong>`;

    } catch (error) {
        console.error("Upload Error:", error);
        resultText.innerText = "❌ Error uploading file.";
    }
}
