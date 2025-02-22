# -*- coding: utf-8 -*-

import sys
import os
import yara
import logging
import traceback
import codecs
import re

# Directories for rules, IOCs, and files to scan
YARA_RULE_DIRECTORIES = [r'./yara']
FILENAME_IOC_DIRECTORY = r'./iocs'
SCAN_DIRECTORY = r'./scans'
SIGNATURE_FILE = r'./file-type-signatures.txt'
# Maximum possible harmful score
MAX_POSSIBLE_SCORE = 100  
def load_file_signatures():
    """Load file-type signatures from the signature-base list."""
    signatures = {}
    try:
        with open(SIGNATURE_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                parts = line.split(";")
                if len(parts) < 2:
                    continue
                
                signature = parts[0].strip().replace(" ", "").upper()  # Normalize hex format
                file_type = parts[1].strip()
                signatures[signature] = file_type

        logging.info(f"Loaded {len(signatures)} file-type signatures.")
    except FileNotFoundError:
        logging.error("Signature file not found!")
    except Exception as e:
        logging.error(f"Error loading signatures: {e}")

    return signatures

def get_file_magic_bytes(file_path, num_bytes=16):
    """Extract first few bytes of a file as a hex string."""
    try:
        with open(file_path, "rb") as file:
            magic_bytes = file.read(num_bytes)
            return magic_bytes.hex().upper()  # Convert to uppercase hex
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None
    
def walk_error(err):
    """Handle directory walk errors."""
    try:
        if "Error 3" in str(err):
            logging.error("Directory walk error")
            sys.exit(1)
    except UnicodeError:
        print("Unicode decode error in walk error message")
        sys.exit(1)

def initialize_yara_rules():
    """Compile and load YARA rules."""
    yara_rules = {}
    try:
        for yara_rule_directory in YARA_RULE_DIRECTORIES:
            if not os.path.exists(yara_rule_directory):
                continue
            for root, _, files in os.walk(yara_rule_directory, onerror=walk_error, followlinks=False):
                for file in files:
                    yara_rule_file = os.path.join(root, file)
                    if file.startswith((".", "~", "_")):
                        continue
                    try:
                        compiled_rules = yara.compile(yara_rule_file, externals={
                            'filename': '',
                            'filepath': '',
                            'extension': '',
                            'filetype': '',
                            'md5': ''
                        })
                        yara_rules[file] = compiled_rules
                        logging.info(f"Loaded YARA rule: {file}")
                    except yara.SyntaxError:
                        logging.error(f"Syntax error in YARA rule: {yara_rule_file}")
                        traceback.print_exc()
    except Exception as e:
        logging.error(f"Unexpected error while loading YARA rules: {e}")
        traceback.print_exc()
    return yara_rules

def initialize_filename_iocs():
    """Compile regex-based filename IOCs."""
    filename_iocs = []
    try:
        for ioc_filename in os.listdir(FILENAME_IOC_DIRECTORY):
            if 'filename' in ioc_filename.lower():
                logging.info(f"Compiling Filename IOCs from {ioc_filename}")
                with codecs.open(os.path.join(FILENAME_IOC_DIRECTORY, ioc_filename), 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        try:
                            cleaned_regex = re.sub(r"\(\?i\)", "", line)  # Remove misplaced (?i)
                            cleaned_regex = f"(?i){cleaned_regex}"  # Ensure (?i) is at the start
                            filename_iocs.append(re.compile(cleaned_regex))
                        except re.error as e:
                            logging.warning(f"Skipping invalid regex: {line} | Error: {e}")
    except FileNotFoundError:
        logging.error("IOC directory not found!")
    except Exception as e:
        logging.error(f"Error reading IOC file: {e}")
    return filename_iocs

def scan_file(file_path, yara_rules, filename_iocs):
    """Scan a file for threats using YARA rules and filename IOCs."""
    file_name = os.path.basename(file_path)
    harmful_score = 0
    # File-Type Signature Matching
    magic_bytes = get_file_magic_bytes(file_path)
    if magic_bytes:
        for signature, file_type in file_signatures.items():
            if magic_bytes.startswith(signature):  # Check if file matches known signature
                logging.info(f"File {file_name} detected as {file_type} (Signature: {signature})")
                if file_type.lower() in ["exe", "dll", "vbs", "scr", "bat"]:  # Potentially dangerous types
                    harmful_score += 15  # Increase harmful score for risky types
                break

    # YARA Scan
    match_count = 0
    for rule_name, rule in yara_rules.items():
        try:
            matches = rule.match(file_path)
            if matches:
                match_count += len(matches)
                harmful_score += len(matches) * 10  # Each match contributes +10
        except Exception as e:
            logging.error(f"Error scanning {file_name} with rule {rule_name}: {e}")

    # Filename IOC Match
    for ioc in filename_iocs:
        if ioc.search(file_name):
            harmful_score += 20  # Filename match adds +20
            break

    # Calculate Harmfulness %
    harmfulness_percentage = min((harmful_score / MAX_POSSIBLE_SCORE) * 100, 100)

    # Determine Verdict
    verdict = "Malicious" if harmfulness_percentage > 50 else "Clean"

    print(f"File: {file_name} | Harmfulness: {harmfulness_percentage:.2f}% | Verdict: {verdict}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    yara_rules = initialize_yara_rules()
    filename_iocs = initialize_filename_iocs()
    file_signatures = load_file_signatures()
    
    if not os.path.exists(SCAN_DIRECTORY):
        os.makedirs(SCAN_DIRECTORY)

    for file in os.listdir(SCAN_DIRECTORY):
        file_path = os.path.join(SCAN_DIRECTORY, file)
        if os.path.isfile(file_path):
            scan_file(file_path, yara_rules, filename_iocs)