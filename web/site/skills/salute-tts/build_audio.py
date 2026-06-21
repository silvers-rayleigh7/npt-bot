#!/usr/bin/env python3
"""Batch TTS generation for Тропа POIs via Sber Salute Speech.

Usage:
    python build_audio.py                        # all POIs, default voice (Bys)
    python build_audio.py --poi 01 05            # specific POIs by number
    python build_audio.py --voice Nec_24000      # different voice
    python build_audio.py --ssml-dir narrations/ # custom SSML files
    python build_audio.py --output-dir site/audio/
"""

import argparse
import glob
import os
import subprocess
import sys
import uuid

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_AUTH_DATA = os.environ.get("SALUTE_AUTH_DATA", "")
DEFAULT_VOICE = "Bys_24000"
AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
SYNTH_URL = "https://smartspeech.sber.ru/rest/v1/text:synthesize"
EDGE_TTS_VOICE = "ru-RU-DmitryNeural"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUTPUT = os.path.join(REPO_ROOT, "site", "audio")
DEFAULT_SSML_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "narrations")


def get_token(auth_data: str) -> str | None:
    if not auth_data:
        return None
    try:
        resp = requests.post(
            AUTH_URL,
            headers={
                "Authorization": f"Basic {auth_data}",
                "RqUID": str(uuid.uuid4()),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data="scope=SALUTE_SPEECH_PERS",
            verify=False,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    except Exception as e:
        print(f"  Salute Speech auth failed: {e}", file=sys.stderr)
        return None


def synthesize(token: str, ssml: str, output_mp3: str, voice: str = DEFAULT_VOICE):
    resp = requests.post(
        SYNTH_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/ssml",
        },
        params={"voice": voice},
        data=ssml.encode("utf-8"),
        verify=False,
        timeout=30,
    )
    if not resp.ok:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        return False

    wav = output_mp3.replace(".mp3", ".wav")
    with open(wav, "wb") as f:
        f.write(resp.content)

    subprocess.run(
        ["ffmpeg", "-y", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "128k", output_mp3],
        capture_output=True,
        check=True,
    )
    os.remove(wav)
    return True


def strip_ssml(ssml: str) -> str:
    """Strip SSML tags to get plain text for Edge TTS."""
    import re
    text = re.sub(r"<[^>]+>", " ", ssml)
    text = re.sub(r"['’]", "", text)  # remove stress marks
    text = re.sub(r"\s+", " ", text).strip()
    return text


def synthesize_edge(text: str, output_mp3: str, voice: str = EDGE_TTS_VOICE) -> bool:
    try:
        subprocess.run(
            ["edge-tts", "--voice", voice, "--text", text, "--write-media", output_mp3],
            capture_output=True, check=True, timeout=60,
        )
        return True
    except Exception as e:
        print(f"  Edge TTS error: {e}", file=sys.stderr)
        return False


BUILTIN_NARRATIONS: dict[str, str] = {}  # Narrations are now in narrations/*.xml files


def load_narrations(ssml_dir: str | None) -> dict[str, str]:
    """Load SSML narrations from .xml files in the narrations directory.

    Expected naming: {nn}_{poi_id}_{level}.xml
    Examples: 01_university_entrance_l1.xml, 03_robot_path_l2.xml

    Output MP3 filenames will match: 01_university_entrance_l1.mp3, etc.
    """
    if ssml_dir and os.path.isdir(ssml_dir):
        narrations = {}
        for f in sorted(glob.glob(os.path.join(ssml_dir, "*.xml"))):
            name = os.path.splitext(os.path.basename(f))[0]
            with open(f) as fh:
                content = fh.read()
            if not content.strip():
                print(f"  WARNING: empty file {f}, skipping", file=sys.stderr)
                continue
            narrations[name] = content
        if narrations:
            print(f"Loaded {len(narrations)} narrations from {ssml_dir}")
            return narrations
        print(f"WARNING: no .xml files found in {ssml_dir}", file=sys.stderr)
    return BUILTIN_NARRATIONS


def main():
    parser = argparse.ArgumentParser(description="Generate TTS audio for Тропа POIs")
    parser.add_argument("--poi", nargs="*", help="POI numbers to generate (e.g. 01 05)")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Voice ID (default: {DEFAULT_VOICE})")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument("--ssml-dir", default=DEFAULT_SSML_DIR, help="Directory with .xml SSML files")
    parser.add_argument("--auth", default=DEFAULT_AUTH_DATA, help="Base64 auth data")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    narrations = load_narrations(args.ssml_dir)

    if args.poi:
        prefixes = [p.zfill(2) for p in args.poi]
        narrations = {k: v for k, v in narrations.items() if any(k.startswith(p) for p in prefixes)}

    if not narrations:
        print("No narrations to generate.", file=sys.stderr)
        sys.exit(1)

    print("Checking Salute Speech credentials...")
    token = get_token(args.auth)
    use_salute = token is not None
    if use_salute:
        print(f"[Salute Speech] Token ok. Generating {len(narrations)} audio files with voice {args.voice}...")
    else:
        print(f"[Edge TTS] Salute Speech unavailable, using Microsoft Edge TTS ({EDGE_TTS_VOICE})...")

    for name, ssml in sorted(narrations.items()):
        mp3_path = os.path.join(args.output_dir, f"{name}.mp3")
        if use_salute:
            ok = synthesize(token, ssml, mp3_path, args.voice)
        else:
            ok = synthesize_edge(strip_ssml(ssml), mp3_path)
        if ok:
            sz = os.path.getsize(mp3_path) // 1024
            print(f"  {name}.mp3 ({sz}KB)")
        else:
            print(f"  {name}: FAILED")

    print("Done.")


if __name__ == "__main__":
    main()
