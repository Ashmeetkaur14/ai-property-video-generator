import argparse
import os
import sys

from video_maker import build_video


def main():
    p = argparse.ArgumentParser(
        description="Make a property promo video from a JSON file and photos.")
    p.add_argument("--input", default="sample_property.json",
                   help="path to the property JSON file")
    p.add_argument("--output", default="output/property_video.mp4",
                   help="where to save the MP4")
    p.add_argument("--no-voice", action="store_true",
                   help="skip the voice-over (works offline)")
    p.add_argument("--music", default="music/bg.mp3",
                   help="optional background music file")
    args = p.parse_args()

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    try:
        build_video(args.input, args.output,
                    use_voice=not args.no_voice, music_path=args.music)
    except ValueError as e:          # problems with the input
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:           # anything unexpected
        print(f"Unexpected error: {type(e).__name__}: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()