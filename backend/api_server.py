from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import logging
import asyncio
from Solution import initialize_yara_rules, initialize_filename_iocs, load_file_signatures, scan_file

UPLOAD_FOLDER = "./incoming"
SCAN_DIRECTORY = "./scans"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SCAN_DIRECTORY, exist_ok=True)

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YARA rules, IOCs, and file signatures
yara_rules = initialize_yara_rules()
filename_iocs = initialize_filename_iocs()
file_signatures = load_file_signatures()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads and move them to the scan directory."""
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logging.info(f"Received file: {file.filename}")

    # Move file to scan directory
    shutil.move(file_path, os.path.join(SCAN_DIRECTORY, file.filename))

    return {"message": "File uploaded successfully", "filename": file.filename}

async def scanner_task():
    """Continuously scans files in the scan directory."""
    while True:
        for file in os.listdir(SCAN_DIRECTORY):
            file_path = os.path.join(SCAN_DIRECTORY, file)
            if os.path.isfile(file_path):
                scan_file(file_path, yara_rules, filename_iocs)
                os.remove(file_path)  # Clean up after scanning
                logging.info(f"Scanned and removed: {file}")
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Start the scanner background task when FastAPI starts."""
    asyncio.create_task(scanner_task())
