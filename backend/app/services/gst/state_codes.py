"""Indian GST state codes — the first 2 digits of a GSTIN encode the state.

Source: https://www.gst.gov.in/help/statecode (official, stable).
"""

# state_code → (state_name, ISO short)
STATE_CODES: dict[str, tuple[str, str]] = {
    "01": ("Jammu and Kashmir", "JK"),
    "02": ("Himachal Pradesh", "HP"),
    "03": ("Punjab", "PB"),
    "04": ("Chandigarh", "CH"),
    "05": ("Uttarakhand", "UK"),
    "06": ("Haryana", "HR"),
    "07": ("Delhi", "DL"),
    "08": ("Rajasthan", "RJ"),
    "09": ("Uttar Pradesh", "UP"),
    "10": ("Bihar", "BR"),
    "11": ("Sikkim", "SK"),
    "12": ("Arunachal Pradesh", "AR"),
    "13": ("Nagaland", "NL"),
    "14": ("Manipur", "MN"),
    "15": ("Mizoram", "MZ"),
    "16": ("Tripura", "TR"),
    "17": ("Meghalaya", "ML"),
    "18": ("Assam", "AS"),
    "19": ("West Bengal", "WB"),
    "20": ("Jharkhand", "JH"),
    "21": ("Odisha", "OR"),
    "22": ("Chhattisgarh", "CT"),
    "23": ("Madhya Pradesh", "MP"),
    "24": ("Gujarat", "GJ"),
    "25": ("Daman and Diu", "DD"),
    "26": ("Dadra and Nagar Haveli", "DN"),
    "27": ("Maharashtra", "MH"),
    "28": ("Andhra Pradesh (Old)", "AP"),
    "29": ("Karnataka", "KA"),
    "30": ("Goa", "GA"),
    "31": ("Lakshadweep", "LD"),
    "32": ("Kerala", "KL"),
    "33": ("Tamil Nadu", "TN"),
    "34": ("Puducherry", "PY"),
    "35": ("Andaman and Nicobar Islands", "AN"),
    "36": ("Telangana", "TG"),
    "37": ("Andhra Pradesh", "AP"),
    "38": ("Ladakh", "LA"),
    "97": ("Other Territory", "OT"),
    "99": ("Centre Jurisdiction", "CJ"),
}


def state_name(code: str) -> str | None:
    """Return state name for a 2-digit GST state code, or None if unknown."""
    if not code or len(code) != 2:
        return None
    entry = STATE_CODES.get(code)
    return entry[0] if entry else None


def code_from_state_name(name: str) -> str | None:
    """Reverse lookup — fuzzy match state name → code. Returns None if no match."""
    if not name:
        return None
    needle = name.strip().lower()
    for code, (full_name, short) in STATE_CODES.items():
        if full_name.lower() == needle or short.lower() == needle:
            return code
    # Loose contains match
    for code, (full_name, _) in STATE_CODES.items():
        if needle in full_name.lower() or full_name.lower() in needle:
            return code
    return None


def is_valid_state_code(code: str | None) -> bool:
    """True if the 2-digit code is a known GST state code."""
    return bool(code) and code in STATE_CODES
