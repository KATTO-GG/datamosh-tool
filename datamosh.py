#!/usr/bin/env python3
"""
Data moshing tool - removes I-frames to create glitch effects.
Usage: python datamosh.py input.mp4 output.mp4 [--start SEC] [--end SEC] [--intensity 0-1]
"""
import argparse
import subprocess
import tempfile
import os
import sys

def run(cmd, check=True):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)

def get_duration(path):
    r = run(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{path}"')
    return float(r.stdout.strip())

def get_keyframes(path):
    r = run(f'ffprobe -v error -select_streams v -show_frames -show_entries frame=pict_type,pts_time -of json "{path}"')
    import json
    data = json.loads(r.stdout)
    frames = []
    for f in data.get('frames', []):
        if 'pict_type' in f and 'pts_time' in f:
            frames.append((f['pict_type'], float(f['pts_time'])))
    return frames

def datamosh(input_path, output_path, start=0, end=None, intensity=1.0):
    duration = get_duration(input_path)
    if end is None or end > duration:
        end = duration

    frames = get_keyframes(input_path)
    iframe_times = [pts for t, pts in frames if t == 'I' and start <= pts <= end]

    if not iframe_times:
        print("No I-frames in range, copying input")
        run(f'cp "{input_path}" "{output_path}"')
        return

    remove_count = int(len(iframe_times) * intensity)
    if remove_count == 0:
        remove_count = 1
    remove_times = set(iframe_times[:remove_count])

    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        tmp_path = tmp.name

    filter_parts = []
    for t in sorted(remove_times):
        filter_parts.append(f'between(t,{t-0.5},{t+0.5})')
    select_filter = '+'.join(filter_parts) if filter_parts else '0'

    cmd = (
        f'ffmpeg -y -i "{input_path}" '
        f'-vf "select=\'not({select_filter})\',setpts=N/FRAME_RATE/TB" '
        f'-af "aselect=\'not({select_filter})\',asetpts=N/SR/TB" '
        f'-c:v libx264 -preset fast -crf 23 "{tmp_path}"'
    )
    run(cmd)

    run(f'ffmpeg -y -i "{tmp_path}" -c copy "{output_path}"')
    os.unlink(tmp_path)
    print(f"Done: {output_path} (removed {len(remove_times)} I-frames)")

def main():
    p = argparse.ArgumentParser(description='Data moshing tool')
    p.add_argument('input')
    p.add_argument('output')
    p.add_argument('--start', type=float, default=0)
    p.add_argument('--end', type=float, default=None)
    p.add_argument('--intensity', type=float, default=1.0, help='0-1 fraction of I-frames to remove')
    args = p.parse_args()

    if not os.path.exists(args.input):
        print(f"Input not found: {args.input}")
        sys.exit(1)

    datamosh(args.input, args.output, args.start, args.end, args.intensity)

if __name__ == '__main__':
    main()