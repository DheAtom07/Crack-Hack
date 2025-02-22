test_data = """UPX0 VirtualAlloc CreateRemoteThread CryptEncrypt
http://malicious-site.com
Software\Microsoft\Windows\CurrentVersion\Run"""

with open("suspicious_file.exe", "w") as f:
    f.write(test_data)

print("Fake malware test file created: test_malware.exe")
