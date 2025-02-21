from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/scan/")
async def scan_file(file: UploadFile = File(...)):
    # Check if file is an .exe
    if not file.filename.endswith(".exe"):
        raise HTTPException(status_code=400, detail="Only .exe files are allowed.")

    # Define new filename
    new_filename = "suspicious_file.exe"
    file_path = os.path.join(UPLOAD_FOLDER, new_filename)

    # Save file with new name
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process the renamed file (Dummy scan for now)
    verdict = "Clean" if "safe" in file.filename.lower() else "Malicious"

    return {"file": new_filename, "verdict": verdict}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
