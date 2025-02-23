async function uploadFile() {
    const fileInput = document.getElementById("fileInput"),
          result = document.getElementById("result");

    if (fileInput.files.length === 0) {
        result.innerText = "⚠️ Please select a file!";
        result.classList.add("error");
        return;
    }

    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://localhost:8000/upload/", {  // ✅ Fixed URL
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("File upload failed");

        const data = await response.json();
        result.innerText = `✅ Scan Result: ${data.verdict}`;
        result.classList.remove("error");

    } catch (error) {
        console.error("Error:", error);
        result.innerText = "❌ Error scanning file.";
        result.classList.add("error");
    }
}

// Ensure the function is available globally if used in index.html
window.uploadFile = uploadFile;
