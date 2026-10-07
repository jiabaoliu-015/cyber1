def _project(lat, lon):
    return {
        "x": round((lon + 180.0) / 360.0, 4),
        "y": round((90.0 - lat) / 180.0, 4),
    }

DASHBOARD_ROSTER = [
    ("Mara Okonkwo",     "NIGHTJAR",  "Orbital Surveillance Lead",   "Lagos",        "NG", "COSMIC",   6.4550,   3.3841),
    ("Deacon Rourke",    "SALTWIRE",  "Signals Intercept Officer",   "Reykjavík",    "IS", "TS/SCI",  64.1466, -21.9426),
    ("Yuki Tanabe",      "PALEHORSE", "Payload Systems Engineer",    "Tokyo",        "JP", "COSMIC",  35.6762, 139.6503),
    ("Sofia Vaduva",     "GLASSJAW",  "Counter-ISR Analyst",         "Bucharest",    "RO", "TS/SCI",  44.4268,  26.1025),
    ("Ezra Calloway",    "DRY LAKE",  "Flight Test Director",        "Palmdale",     "US", "COSMIC",  34.5794,-118.1165),
    ("Amara Sithole",    "LODESTAR",  "Ground Station Chief",        "Cape Town",    "ZA", "TS/SCI", -33.9249,  18.4241),
    ("Kel Brannigan",    "IRONWOOD",  "Launch Range Safety",         "Kourou",       "GF", "SECRET",   5.1600, -52.6500),
    ("Priya Anand",      "KESTREL",   "Trajectory Analyst",          "Bengaluru",    "IN", "TS/SCI",  12.9716,  77.5946),
    ("Tomas Herrera",    "REDSHIFT",  "Optics & Sensors",            "Santiago",     "CL", "SECRET", -33.4489, -70.6693),
    ("Nadia Belova",     "COLDIRON",  "Cryogenics Lead",             "Murmansk",     "RU", "TS/SCI",  68.9585,  33.0827),
    ("Owen Finch",       "TALLGRASS", "Comms Relay Architect",       "Winnipeg",     "CA", "SECRET",  49.8951, -97.1384),
    ("Lena Fischer",     "HALFLIGHT", "Cryptologic Engineer",        "Munich",       "DE", "COSMIC",  48.1351,  11.5820),
    ("Idris Farah",      "SUNKENBELL","Threat Modelling",            "Nairobi",      "KE", "TS/SCI",  -1.2921,  36.8219),
    ("Chen Wei",         "PAPER TIGER","Radar Cross-Section",        "Chengdu",      "CN", "TS/SCI",  30.5728, 104.0668),
    ("Bianca Rossi",     "VESPER",    "Orbital Mechanics",           "Turin",        "IT", "SECRET",  45.0703,   7.6869),
    ("Hollis Vance",     "BLACKTOP",  "Autonomy & Guidance",         "Adelaide",     "AU", "COSMIC", -34.9285, 138.6007),
    ("Farrah Nasser",    "QUICKLIME", "Propulsion Diagnostics",      "Amman",        "JO", "TS/SCI",  31.9539,  35.9106),
    ("Gunnar Svensson",  "NORTHWALL", "Space Domain Awareness",      "Kiruna",       "SE", "TS/SCI",  67.8558,  20.2253),
    ("Dolores Marchetti","LONGSHADOW","Mission Assurance",           "Buenos Aires", "AR", "SECRET", -34.6037, -58.3816),
    ("Rashid Al-Amin",   "DUNEGLASS", "Downlink Security",           "Abu Dhabi",    "AE", "COSMIC",  24.4539,  54.3773),
    ("Tabitha Cole",     "WILDFIRE",  "Anomaly Response",            "Denver",       "US", "TS/SCI",  39.7392,-104.9903),
    ("Minh Pham",        "STILLWATER","Telemetry Analyst",           "Hanoi",        "VN", "SECRET",  21.0278, 105.8342),
    ("Iona Sterling",    "GREYVEIL",  "Program Security Officer",    "Edinburgh",    "GB", "COSMIC",  55.9533,  -3.1883),
    ("Marcus Webb",     "HAILSTONE", "Re-entry Systems",            "Houston",      "US", "TS/SCI",  29.7604, -95.3698),
    ("Anaïs Lefevre",    "PORTHOLE",  "Optical Comms Research",      "Toulouse",     "FR", "SECRET",  43.6047,   1.4442),
]

_AVATAR_TONES = ["#2a3240", "#2d3542", "#28303c", "#313a48", "#262e39"]

_STATUS_CYCLE = ["ACTIVE", "ACTIVE", "ACTIVE", "STANDBY", "ACTIVE", "DEPLOYED"]


def get_agents():
    agents = []
    for i, (name, callsign, role, city, country, clr, lat, lon) in enumerate(DASHBOARD_ROSTER):
        p = _project(lat, lon)
        agents.append({
            "index": i + 1,
            "id": f"AC-{4100 + i * 7}",
            "name": name,
            "callsign": callsign,
            "role": role,
            "city": city,
            "country": country,
            "clearance": clr,
            "status": _STATUS_CYCLE[i % len(_STATUS_CYCLE)],
            "lat": lat,
            "lon": lon,
            "x": p["x"],
            "y": p["y"],
            "tone": _AVATAR_TONES[i % len(_AVATAR_TONES)],
        })
    return agents
