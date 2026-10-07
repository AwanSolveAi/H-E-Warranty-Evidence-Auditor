
PROFILES = {
    "general_heavy_equipment": {
        "display_name": "General Heavy Equipment",
        "requires": []
    },
    "generator": {
        "display_name": "Generator",
        "requires": ["battery_voltage", "output_voltage", "frequency", "load_test"]
    }
}

def validate_profile(profile):
    if profile not in PROFILES:
        raise ValueError(f"Unsupported profile: {profile}")
    return PROFILES[profile]
