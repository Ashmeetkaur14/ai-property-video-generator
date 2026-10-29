AI Property Video Generator

Turns property details and photos into a short, ready-to-share promotional MP4 (about 30-35 seconds) with captions, voice-over, fade transitions and optional background music. No manual video editing is needed.

Built for the AI Property Video Generator assignment (AI Content Creation / Multimedia).

Author: ASHMEET KAUR
## Quick links
What	Where
Sample video	sample_output/sample_video.mp4
Sample script	sample_output/sample_script.txt
Sample frame	sample_output/sample_frame.png
Sample input	sample_property.json + images/
Demo recording	<ADD DEMO LINK HERE>
What it does

Input: property name, location, type, price, key features, contact text and 4-8 photos.

Output: an MP4 with this structure.

Scene	                    Content
Opening 	                Property name, location, price (dark overlay on a photo)
Feature scenes (up to 5)	One photo each, with one feature as the caption
Closing	"Book Your Visit" with the contact / call-to-action text

Every scene has a text overlay, a fade-in / fade-out transition and a narration line. Background music is optional.
## How it works:
Input (web form  or  JSON file + photos)
        |
        v
1. Validate input    -> clear message if name / location / type is missing
        |
        v
2. Script generator  -> template-based captions and voice-over lines
        |
        v
3. Fact-checker      -> stops the build if any number or word is not from the input
        |
        v
4. Scene builder     -> crop photo to 16:9, dark band, text overlay (Pillow)
        |
        v
5. Audio             -> gTTS narration placed at exact times + optional quiet music
        |
        v
6. Export            -> MP4 (MoviePy + ffmpeg), preview and download in the web app
Input format

Example: sample_property.json
{
  "name": "Green Valley Residency",
  "location": "Kharar, Punjab",
  "type": "2-BHK Apartment",
  "price": "Rs. 45 Lakh",
  "features": [
    "Spacious balcony",
    "Gated society with 24x7 security",
    "Near market and schools",
    "Covered parking"
  ],
  "cta": "Call 98XXXXXX10 to book a site visit",
  "images": ["images/1.jpg", "images/2.jpg", "images/3.jpg",
             "images/4.jpg", "images/5.jpg", "images/6.jpg"]
}
Field       	Required	         Notes
name	            Yes	            Property name
location        	Yes	            City / area
type	            Yes	            For example "2-BHK Apartment"
price	             No	            If empty, the price is simply left out
features	         No	            Up to 5 are used, one per scene
cta	                 No	            If empty, "Contact us to know more" is used
images	Recommended	4-8 photos. Paths are relative to the project folder
Requirements
Python 3.10 or newer (developed and tested on Python 3.14, Windows 11)
Internet connection for the voice-over (gTTS). Without internet, use --no-voice
No API keys, accounts or paid services
A separate ffmpeg install is not needed. MoviePy uses imageio-ffmpeg, which downloads its own copy
Installation

## Windows (PowerShell)
cd property-video
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
If PowerShell blocks activate, run this once in the same window and try again:
Set-ExecutionPolicy -Scope Process Bypass
Usage

Run all commands from inside the property-video folder, because image paths in the JSON are relative to it.

Option 1: Web app (form, preview, download)
python -m streamlit run app.py
Open http://localhost:8501, fill in the form, upload photos and click Generate video. The app shows the script used, a video preview and a download button.
python generate.py                                   # uses sample_property.json
python generate.py --input my_property.json --output output/my_video.mp4
python generate.py --no-voice                        # works offline, no narration
python generate.py --music music/bg.mp3              # custom background music
On Windows you can replace python with py.

Option	Default	Meaning
--input	sample_property.json	Property JSON file
--output	output/property_video.mp4	Where the MP4 is saved
--no-voice	off	Skip narration
--music	music/bg.mp3	Optional music file. If it does not exist, music is skipped

The generated video is saved in output/. Temporary files (frames, voice clips) go to output/work/.
Run the tests
bash
python test_fact_check.py

Expected output: three PASS lines, plus the list of fake facts that were caught in test 2.

## How the AI output is checked (fact-check)

The script is built from fixed templates filled with the user's own values, so it cannot invent amenities, prices or locations. As a second safeguard, fact_check.py runs before every video:

Every number in the script must also appear in the input.
Every word must come from the input or from a short list of template words (for example "Introducing", "Priced at").

If a check fails, no video is rendered and the exact problem lines are shown, for example:

Fact-check failed:
  Scene 7 (caption): word 'pool' is not in the input

test_fact_check.py proves three things: a clean script passes, a fake feature is caught, and a wrong price is caught.

The same checker is designed to guard an LLM writer if one is added later (see "Possible improvements").

## Error handling
Error handling
Situation	                                          Behaviour
Name, location or type missing	                      Clear error message, no crash
Input file missing	                                  Clear error message
Invalid JSON	                                      "Input file is not valid JSON" message
An image is missing or corrupted	                   Warning printed, that image is skipped
No usable images	                                   Warning, plain colour background is used
Fewer than 4 photos	Photos are reused across scenes
More than 8 photos (web app)                        	Only the first 8 are used, with a warning
Price missing	                                      Opening scene shows location only, narration          price
Contact text missing	                             Default "Contact us to know more" is used
Very long feature text                           	Text wraps onto several lines and stays on screen
No internet / voice fails	                        Warning, video is made without narration
No music file	                                    Video is made without music
Fact-check fails	                                No video, problem lines are listed
Any other unexpected error	Short readable message with exit code, no raw traceback


## AI models, libraries and services used:
 Tool | Purpose |
|---|---|
| Template logic (own code) | Writes captions and voice-over. Chosen because it is reliable and cannot invent facts |
| gTTS (Google Text-to-Speech) | Converts the script into narration. The script text is sent to Google's TTS service |
| MoviePy 1.0.3 | Joins scenes, fades, audio mixing, MP4 export |
| Pillow | Crops photos to 16:9 and draws text overlays |
| NumPy | Passes frames to MoviePy |
| Streamlit | Web form, preview and download |
| Royalty-free music (optional) | <track name, source, licence> |



No large language model is used. The script is rule-based on purpose: the
assignment requires "only use facts supplied in the input", and templates give
that guarantee with no hallucination risk. The only AI component is
text-to-speech.

## Key decisions
- **Templates over an LLM:** zero hallucination, zero cost, works offline.
- **Pillow for text instead of MoviePy TextClip:** avoids the ImageMagick
  dependency, which is hard to install on Windows.
- **One mixed audio track:** voice lines are placed at exact times and attached
  once, which keeps narration in sync with scenes.
- **Fact-check before rendering:** fails early with a readable message.

## Limitations
- Narration needs internet (gTTS). The voice is a standard TTS voice.
- Fact-check compares words and numbers, not meaning.
- Photos are not analysed, so a caption is not matched to what the photo shows.
- Captions are in English only. Fixed 16:9 (1280x720) output.
- Rendering takes about a minute and runs on a single CPU thread.

## Possible improvements
- Optional LLM script writer whose output must pass `fact_check.py`, with
  automatic fallback to the template script.
- Image classification to match captions with photos (balcony, kitchen).
- Vertical 9:16 export for Reels and Shorts, Hindi/Punjabi narration,
  ken-burns zoom on photos, brand logo overlay.

## Project structure
property-video/
├── app.py                 Streamlit web app
├── generate.py            Command-line tool
├── video_maker.py         Scene drawing, voice, music, MP4 export
├── script_generator.py    Input loading, validation, template script
├── fact_check.py          Fact verification
├── test_fact_check.py     Tests for the fact-checker
├── sample_property.json   Sample input
├── requirements.txt       Dependencies
├── images/                Sample photos (free stock photos)
├── music/                 Optional background music (bg.mp3)
├── sample_output/         Sample video, script and frame
└── output/                Generated videos (work/ holds temporary files)
## Data and privacy
All sample data is synthetic. The phone number is a placeholder. No API keys,
passwords or customer data are included.