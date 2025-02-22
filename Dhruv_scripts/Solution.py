import yara
import magic

# 🔍 Threat Weights (Assign risk scores)
THREAT_WEIGHTS = {
    "virtualalloc": 20, "writeprocessmemory": 25, "createremotethread": 30,
    "loadlibrary": 10, "getprocaddress": 10, "ntunmapviewofsection": 25,
    "runkey": 15, "task_scheduler": 20, "wmic": 15,
    "ransom_extension": 30, "ransom_note": 40, "crypto_api": 50,
    "http": 10, "https": 10, "dns": 15, "useragent": 15,
    "getasynckeystate": 20, "cred_dump": 35, "clipboard": 10,
    "shellcode1": 50, "shellcode2": 50,
    "pdf_javascript": 30, "pdf_launch": 40, "pdf_cmd": 35, "pdf_exploit": 45,
    "image_exif": 10, "image_base64": 20
}

# 📌 Load YARA rules for different file types
rules = {
    "exe": yara.compile(filepath="exe_rules.yar"),
    "pdf": yara.compile(filepath="pdf_rules.yar"),
    "image": yara.compile(filepath="image_rules.yar")
}

# 🔍 Detect file type
def detect_file_type(file_path):
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

# 🛠 Calculate threat percentage
def calculate_threat_score(matches):
    total_score = 0
    max_possible_score = sum(THREAT_WEIGHTS.values())

    for match in matches:
        for string_match in match.strings:
            name = string_match.identifier.lower()  # Convert to lowercase
            print(f"✅ Matched String: {name}")  # Debug print
            
            if name in THREAT_WEIGHTS:
                total_score += THREAT_WEIGHTS[name]

    # Prevent 0% when something is detected
    if total_score == 0 and matches:
        return 1.0

    threat_percentage = (total_score / max_possible_score) * 100 if total_score > 0 else 0
    return round(threat_percentage, 2)

# 🚀 Scan file
def scan_file(file_path):
    file_type = detect_file_type(file_path)
    
    if "pdf" in file_type:
        rule = rules["pdf"]
    elif "x-dosexec" in file_type:  # EXE file
        rule = rules["exe"]
    elif "image" in file_type:
        rule = rules["image"]
    else:
        print(f"⚠️ Unsupported file type: {file_type}")
        return "Unknown file type"

    matches = rule.match(file_path)

    if matches:
        threat_level = calculate_threat_score(matches)
        print(f"⚠️ MALICIOUS FILE DETECTED ({threat_level}% THREAT LEVEL)")
        return f"Malicious ({threat_level}%)"
    else:
        print(f"✅ File is clean ({file_type})")
        return "Clean"

# 🔍 Test File
file_to_scan = "suspicious_file.exe"  # Change to your test file
result = scan_file(file_to_scan)
print(f"🔎 Scan Result: {result}")
