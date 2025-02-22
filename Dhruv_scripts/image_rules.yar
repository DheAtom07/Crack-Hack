rule Malware_Image {
    meta:
        description = "Detects suspicious images"
        author = "YourName"

    strings:
        $exif = "Exif" nocase
        $hidden_payload = "base64," nocase
        $steganography = "stegano" nocase

    condition:
        any of them
}
