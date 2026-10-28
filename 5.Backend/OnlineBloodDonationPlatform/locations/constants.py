from accounts.models import User


# Roles allowed to search for donors and open the donor map.
# The team has not decided yet whether "blood seeker" becomes its own
# role, so this is the ONE place to change who can search.
DONOR_SEARCH_ROLES = (
    User.Role.DONOR,
    User.Role.HOSPITAL,
    User.Role.ADMIN,
)


# Coordinates are rounded to this many decimal places before they are
# shown anywhere. 2 decimals is roughly 1 km.
APPROXIMATE_DECIMALS = 2


# Rough bounding box of Afghanistan, used to validate map clicks.
AFGHANISTAN_BOUNDS = {
    "min_lat": 29.3,
    "max_lat": 38.5,
    "min_lng": 60.5,
    "max_lng": 75.0,
}

# Default map view when the user has no location.
AFGHANISTAN_CENTER = {"lat": 34.0, "lng": 66.0, "zoom": 6}


# Search radius options in km. An empty value means "any distance".
RADIUS_CHOICES = [
    ("", "Any distance"),
    ("5", "5 km"),
    ("10", "10 km"),
    ("25", "25 km"),
    ("50", "50 km"),
]


# Standard ABO/Rh red cell compatibility:
# recipient blood type -> blood types they can receive from.
COMPATIBLE_DONORS = {
    "O-": ["O-"],
    "O+": ["O+", "O-"],
    "A-": ["A-", "O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"],
    "AB+": ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"],
}


# The 34 provinces of Afghanistan with the approximate centre of each
# provincial capital (lat, lng). Used as the search origin when a user
# picks a province instead of clicking the map.
# NOTE: approximate values - the team should verify them.
PROVINCES = {
    "Badakhshan": (37.12, 70.58),
    "Badghis": (34.98, 63.13),
    "Baghlan": (35.94, 68.71),
    "Balkh": (36.71, 67.11),
    "Bamyan": (34.82, 67.83),
    "Daykundi": (33.72, 66.13),
    "Farah": (32.37, 62.11),
    "Faryab": (35.92, 64.78),
    "Ghazni": (33.55, 68.42),
    "Ghor": (34.52, 65.25),
    "Helmand": (31.59, 64.37),
    "Herat": (34.35, 62.20),
    "Jowzjan": (36.67, 65.75),
    "Kabul": (34.53, 69.17),
    "Kandahar": (31.61, 65.71),
    "Kapisa": (35.02, 69.33),
    "Khost": (33.34, 69.92),
    "Kunar": (34.87, 71.15),
    "Kunduz": (36.73, 68.86),
    "Laghman": (34.65, 70.21),
    "Logar": (33.99, 69.02),
    "Nangarhar": (34.43, 70.45),
    "Nimroz": (30.96, 61.86),
    "Nuristan": (35.42, 70.92),
    "Paktia": (33.60, 69.23),
    "Paktika": (33.14, 68.73),
    "Panjshir": (35.31, 69.52),
    "Parwan": (35.01, 69.17),
    "Samangan": (36.27, 68.02),
    "Sar-e Pol": (36.22, 65.93),
    "Takhar": (36.74, 69.53),
    "Uruzgan": (32.63, 65.87),
    "Wardak": (34.40, 68.87),
    "Zabul": (32.11, 66.91),
}

PROVINCE_CHOICES = [(name, name) for name in PROVINCES]
