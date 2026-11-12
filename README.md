# datamosh

Data moshing tool - removes I-frames to create glitch/video corruption effects.

## Usage

```bash
python datamosh.py input.mp4 output.mp4 [--start SEC] [--end SEC] [--intensity 0-1]
```

- `--start SEC` - Start time in seconds (default: 0)
- `--end SEC` - End time in seconds (default: video duration)
- `--intensity 0-1` - Fraction of I-frames to remove (default: 1.0 = all)

## Example

```bash
python datamosh.py video.mp4 glitched.mp4 --start 5 --end 15 --intensity 0.7
```

## Requirements

- Python 3
- ffmpeg / ffprobe in PATH

## How it works

1. Finds all I-frames (keyframes) in the specified time range
2. Removes a fraction of them based on `--intensity`
3. Re-encodes with libx264, causing P/B frames to reference missing I-frames → glitch effect