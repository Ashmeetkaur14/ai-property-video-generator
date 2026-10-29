import os
import numpy as np
from fact_check import fact_check
from PIL import Image, ImageDraw, ImageFont, ImageOps
from moviepy.editor import (ImageClip, AudioFileClip, CompositeAudioClip,
                            concatenate_videoclips, vfx, afx)
from gtts import gTTS

from script_generator import load_property, build_script

W, H = 1280, 720
SECONDS_PER_SCENE = 4

FONT_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def get_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def wrap_text(draw, text, font, max_width):
    lines, current = [], ""
    for word in text.split():
        test = (current + " " + word).strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered(draw, lines, font, y, fill):
    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(((W - w) / 2, y), line, font=font, fill=fill)
        y += font.size + 12
    return y


def load_images(paths):
    good = []
    for p in paths:
        try:
            good.append(Image.open(p).convert("RGB"))
        except Exception:
            print(f"Warning: could not open image '{p}' - skipping it.")
    return good


def make_frame(bg_image, caption, subtitle, big):
    if bg_image is None:
        img = Image.new("RGB", (W, H), (30, 60, 90))
    else:
        img = ImageOps.fit(bg_image, (W, H))

    cap_font = get_font(64 if big else 50)
    sub_font = get_font(36)
    measure = ImageDraw.Draw(img)
    cap_lines = wrap_text(measure, caption, cap_font, W - 160)
    sub_lines = wrap_text(measure, subtitle, sub_font, W - 160) if subtitle else []
    text_height = (len(cap_lines) * (cap_font.size + 12)
                   + len(sub_lines) * (sub_font.size + 12) + 20)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    if big:
        od.rectangle([0, 0, W, H], fill=(0, 0, 0, 140))
        y = (H - text_height) / 2
    else:
        y = H - text_height - 50
        od.rectangle([0, y - 30, W, H], fill=(0, 0, 0, 160))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    y = draw_centered(draw, cap_lines, cap_font, y, (255, 255, 255))
    draw_centered(draw, sub_lines, sub_font, y + 8, (255, 215, 0))
    return img


def make_voice(text, path):
    """Turn text into an mp3 voice file. If it fails, return None."""
    try:
        gTTS(text, lang="en", tld="co.in").save(path)
        return path
    except Exception as e:
        print(f"Warning: voice-over failed ({e}). Continuing without narration.")
        return None


def build_video(prop_path, out_path, use_voice=True, music_path="music/bg.mp3"):
    prop = load_property(prop_path)
    scenes = build_script(prop)
    problems = fact_check(prop, scenes)
    if problems:
        raise ValueError("Fact-check failed:\n  " + "\n  ".join(problems))
    print("Fact-check passed: every number and word comes from the input.")
    images = load_images(prop.get("images", []))
    if not images:
        print("Warning: no usable images found. Using a plain background.")

    os.makedirs("output", exist_ok=True)
    os.makedirs("output/work", exist_ok=True)
    clips = []
    voice_tracks = []     # voice clips with their start time
    t = 0.0               # where the current scene starts in the final video

    for i, scene in enumerate(scenes):
        print(f"Making scene {i + 1} of {len(scenes)}...")
        bg = images[i % len(images)] if images else None
        big = (i == 0 or i == len(scenes) - 1)
        frame = make_frame(bg, scene["caption"], scene["subtitle"], big)
        frame.save(f"output/work/frame_{i + 1}.png")

        duration = SECONDS_PER_SCENE
        if use_voice:
            mp3 = make_voice(scene["voice"], f"output/work/voice_{i + 1}.mp3")
            if mp3:
                voice = AudioFileClip(mp3)
                duration = max(SECONDS_PER_SCENE, voice.duration + 1.0)
                # start the voice a little after the scene begins
                voice_tracks.append(voice.set_start(t + 0.3))

        clip = (ImageClip(np.array(frame))
                .set_duration(duration)
                .fx(vfx.fadein, 0.5)
                .fx(vfx.fadeout, 0.5))
        clips.append(clip)
        t += duration

    # all clips are the same size, so "chain" is simple and keeps timing exact
    video = concatenate_videoclips(clips, method="chain")

    # build ONE audio track for the whole video
    audio_parts = list(voice_tracks)
    if os.path.exists(music_path):
        music = AudioFileClip(music_path).volumex(0.12)
        music = afx.audio_loop(music, duration=video.duration)
        audio_parts.append(music)
    else:
        print("Note: no music file at music/bg.mp3 - skipping music.")

    if audio_parts:
        full_audio = CompositeAudioClip(audio_parts).set_duration(video.duration)
        full_audio.fps = 44100
        video = video.set_audio(full_audio)

    video.write_videofile(out_path, fps=24, codec="libx264",
                          audio_codec="aac", audio_fps=44100,
                          temp_audiofile="output/work/temp_audio.m4a",
                          remove_temp=True)
    print(f"\nDone! Video saved to: {out_path}")

if __name__ == "__main__":
    try:
        build_video("sample_property.json", "output/property_video.mp4")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")