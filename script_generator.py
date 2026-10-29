import json


def load_property(path):
    """Read the JSON file and check the must-have details."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Input file not found: {path}")
    except json.JSONDecodeError:
        raise ValueError("Input file is not valid JSON. Check commas and quotes.")

    required = ["name", "location", "type"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        raise ValueError(f"Missing required details: {', '.join(missing)}")
    return data


def build_script(p):
    """Turn property details into a list of scenes (caption + voice-over)."""
    scenes = []

    # Opening scene
    subtitle = p["location"]
    voice = f"Introducing {p['name']}, a {p['type']} in {p['location']}."
    if p.get("price"):                       # price is optional
        subtitle += f"  |  {p['price']}"
        voice += f" Priced at {p['price']}."
    scenes.append({"caption": p["name"], "subtitle": subtitle, "voice": voice})

    # Feature scenes (max 5)
    for feature in p.get("features", [])[:5]:
        scenes.append({"caption": feature, "subtitle": "", "voice": f"{feature}."})

    # Closing scene
    cta = p.get("cta") or "Contact us to know more"
    scenes.append({"caption": "Book Your Visit", "subtitle": cta, "voice": cta + "."})

    return scenes


if __name__ == "__main__":
    prop = load_property("sample_property.json")
    for i, scene in enumerate(build_script(prop), 1):
        print(i, scene)