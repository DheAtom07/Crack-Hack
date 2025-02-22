import { useState } from "react";
import axios from "axios";
import BACKEND_URL from "./config"; // Import the backend URL

export default function FileUploader() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axios.post(`${BACKEND_URL}/upload/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadMessage(response.data.message);
    } catch (error) {
      setUploadMessage("Failed to upload file.");
      console.error("Upload error:", error);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4 p-5 bg-gray-100 rounded-lg shadow-lg">
      <input type="file" onChange={handleFileChange} className="border p-2 rounded" />
      <button
        onClick={handleUpload}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Upload File
      </button>
      {uploadMessage && <p className="text-gray-700">{uploadMessage}</p>}
    </div>
  );
}
