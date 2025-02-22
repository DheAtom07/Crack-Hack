rule Malware_PDF {
    meta:
        description = "Detects potentially malicious PDFs"
        author = "YourName"

    strings:
        $pdf_header = "%PDF-"  // Every PDF starts with this
        $javascript = "/JavaScript" nocase
        $launch_action = "/Launch" nocase
        $openaction = "/OpenAction" nocase  // FIXED: This must be used below
        $cmd = "cmd.exe" nocase
        $powershell = "powershell.exe" nocase

    condition:
        $pdf_header and any of ($javascript, $launch_action, $openaction, $cmd, $powershell)  // FIXED: Added $openaction
}
