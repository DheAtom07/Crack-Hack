rule Malware_EXE {
    meta:
        description = "Detects malicious EXE files"
        author = "YourName"
    
    strings:
        $exe_header = { 4D 5A }  // EXE signature (MZ)
        $virtualalloc = "VirtualAlloc" nocase
        $writeprocessmemory = "WriteProcessMemory" nocase
        $createremotethread = "CreateRemoteThread" nocase
        $http = "http://" nocase

    condition:
        $exe_header and any of ($virtualalloc, $writeprocessmemory, $createremotethread, $http)
}
