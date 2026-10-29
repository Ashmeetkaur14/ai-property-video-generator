import json
import os
import shutil

import streamlit as st

from script_generator import build_script
from video_maker import build_video

st.set_page_config(page_title="AI Property Video Generator", page_icon="🏠")
st.title("🏠 AI Property Video Generator")
st.write("Fill in the details, upload 4-8 photos, and get a ready-to-share video.")

# ---------- The form ----------
name = st.text_input("Property name *", "Green Valley Residency")
location = st.text_input("Location *", "Kharar, Punjab")
ptype = st.text_input("Property type *", "2-BHK Apartment")
price = st.text_input("Price (optional)", "Rs. 45 Lakh")
features_text = st.text_area(
    "Key features (one per line, max 5 are used)",
    "Spacious balcony\nGated society with 24x7 security\nNear market and schools\nCovered parking",
)
cta = st.text_input("Contact / call-to-action", "Call 98XXXXXX10 to book a site visit")
files = st.file_uploader("Property photos (4-8)", type=["jpg", "jpeg", "png"],
                         accept_multiple_files=True)
use_voice = st.checkbox("Add voice-over (needs internet)", value=True)

if st.button("Generate video", type="primary"):
    # ---------- Check the input and show friendly messages ----------
    missing = [label for label, value in
               [("Property name", name), ("Location", location), ("Property type", ptype)]
               if not value.strip()]
    if missing:
        st.error("Please fill in: " + ", ".join(missing))
        st.stop()
    if not files:
        st.error("Please upload at least one photo.")
        st.stop()
    if len(files) < 4:
        st.warning("Only %d photo(s) uploaded. 4-8 is best, so photos will be reused." % len(files))
    if len(files) > 8:
        st.warning("More than 8 photos uploaded. Only the first 8 will be used.")
        files = files[:8]

    # ---------- Save the photos and a JSON file ----------
    shutil.rmtree("uploads", ignore_errors=True)
    os.makedirs("uploads")
    image_paths = []
    for i, f in enumerate(files, 1):
        ext = os.path.splitext(f.name)[1].lower() or ".jpg"
        path = f"uploads/{i}{ext}"
        with open(path, "wb") as out:
            out.write(f.getbuffer())
        image_paths.append(path)

    prop = {
        "name": name.strip(),
        "location": location.strip(),
        "type": ptype.strip(),
        "price": price.strip(),
        "features": [x.strip() for x in features_text.splitlines() if x.strip()],
        "cta": cta.strip(),
        "images": image_paths,
    }
    with open("uploads/property.json", "w", encoding="utf-8") as jf:
        json.dump(prop, jf, indent=2)

    # ---------- Show the script ----------
    with st.expander("Script used in the video"):
        for i, s in enumerate(build_script(prop), 1):
            st.write(f"**Scene {i}:** {s['caption']}  \n*Voice:* {s['voice']}")

    # ---------- Make the video ----------
    out_path = "output/property_video.mp4"
    try:
        with st.spinner("Making your video... this takes about a minute."):
            build_video("uploads/property.json", out_path, use_voice=use_voice)
        with open(out_path, "rb") as v:
            video_bytes = v.read()
        st.success("Video is ready!")
        st.video(video_bytes)
        st.download_button("Download MP4", video_bytes,
                           file_name="property_video.mp4", mime="video/mp4")
    except Exception as e:
        st.error(f"Something went wrong: {e}")