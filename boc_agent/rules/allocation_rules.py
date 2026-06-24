# Fictional allocation mapping rules and constants for the BOC Allocation Review Agent

# Define the 16 target allocation columns exactly
ALLOCATION_COLUMNS = [
    "Out of Canada costs",
    "Ontario Salary (41)",
    "ONT individual (45)",
    "ONT loan-out corporation (42)",
    "ONT labor multi-share (44)",
    "ONT labor paid to VICE Canada",
    "Ontario Spend (40)",
    "ONT non eligible",
    "Fed labor paid to VICE Canada",
    "Fed salary",
    "Fed individual",
    "Fed loan-out",
    "Fed multi-share",
    "Fed partnership",
    "Fed non eligible",
    "Meal (catering, craft, per diem)",
    "Quebec qualified labour",
    "Quebec qualified properties / spend",
    "Quebec non-qualified",
    "Quebec needs review"
]

# Set of allowed Episode codes
ALLOWED_EP_CODES = {40, 41, 42, 44, 45, 50, 51, 52, 54, 55, 60, 61, 62, 64, 65}

# Set of allowed Location codes
ALLOWED_LOCATION_CODES = {900, 910, 920}

# Standard labor account prefixes/patterns
LABOR_ACCOUNTS = [
    "T04-0500",  # Producer
    "T22-1000",  # Camera
    "T23-0100",  # Gaffer
    "T24-",      # Other labor prefixes
    "T25-",
    "T26-",
    "T27-",
    "T28-",
    "T29-",
    "T30-"
]
