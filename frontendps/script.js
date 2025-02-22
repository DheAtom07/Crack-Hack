async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const resultText = document.getElementById("result");

    if (fileInput.files.length === 0) {
        resultText.innerText = "⚠️ Please select a file!";
        resultText.classList.add("error");
        return;
    }

    const file = fileInput.files[0];

    if (!file.name.endsWith(".exe")) {
        resultText.innerText = "❌ Only .exe files are allowed!";
        resultText.classList.add("error");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://127.0.0.1:8000/upload", {
            method: "POST", // ✅ Make sure this is POST
            body: formData,
        });

        if (!response.ok) {
            throw new Error("File upload failed");
        }

        const data = await response.json();
        resultText.innerText = `✅ Scan Result: ${data.verdict}`;
        resultText.classList.remove("error");

    } catch (error) {
        console.error("Error:", error);
        resultText.innerText = "❌ Error scanning file.";
        resultText.classList.add("error");
    }
}
