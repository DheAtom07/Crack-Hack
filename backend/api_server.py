from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
import shutil
import logging
import asyncio
from Solution import initialize_yara_rules, initialize_filename_iocs, load_file_signatures, scan_file

# Directories for incoming files and scanning
UPLOAD_FOLDER = "./incoming"
SCAN_DIRECTORY = "./scans"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SCAN_DIRECTORY, exist_ok=True)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load YARA rules, IOCs, and file signatures
yara_rules = initialize_yara_rules()
filename_iocs = initialize_filename_iocs()
file_signatures = load_file_signatures()

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Malware Scanner API is running!"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Handles file uploads and scans the file immediately."""
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save file to incoming folder
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logging.info(f"Received file: {file.filename}")

    # Move file to scan directory
    scan_path = os.path.join(SCAN_DIRECTORY, file.filename)
    shutil.move(file_path, scan_path)

    # Scan the file immediately
    verdict = scan_file(scan_path, yara_rules, filename_iocs)

    return {"filename": file.filename, "verdict": verdict}

@app.get("/scan/")
async def scan_existing_files():
    """Manually trigger scanning of all files in the scan directory."""
    results = []
    
    for file in os.listdir(SCAN_DIRECTORY):
        file_path = os.path.join(SCAN_DIRECTORY, file)
        if os.path.isfile(file_path):
            verdict = scan_file(file_path, yara_rules, filename_iocs)
            results.append({"filename": file, "verdict": verdict})
            os.remove(file_path)  # Remove file after scanning
            logging.info(f"Scanned and removed: {file}")

    return {"scanned_files": results}

async def scanner_task():
    """Background task to scan files continuously."""
    while True:
        for file in os.listdir(SCAN_DIRECTORY):
            file_path = os.path.join(SCAN_DIRECTORY, file)
            if os.path.isfile(file_path):
                verdict = scan_file(file_path, yara_rules, filename_iocs)
                logging.info(f"Background Scan - File: {file}, Verdict: {verdict}")
                os.remove(file_path)  # Clean up after scanning
        await asyncio.sleep(5)  # Wait before scanning again

@app.on_event("startup")
async def startup_event():
    """Starts the background scanner task when FastAPI starts."""
    asyncio.create_task(scanner_task())
