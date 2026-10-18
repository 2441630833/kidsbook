"""Encode a complete PNG sequence and verify the decoded H.264 movie with FFmpeg."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


def run(command):
    result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(result.stderr[-8000:])
    return result.stderr


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    parser.add_argument("--audio", type=Path, help="Optional authorized audio; short tracks are padded")
    args = parser.parse_args()
    if not args.ffmpeg:
        parser.error("Supply --ffmpeg or install FFmpeg; imageio_ffmpeg.get_ffmpeg_exe() is also supported")
    output = args.output.resolve()
    status = json.loads((output / "render_progress.json").read_text(encoding="utf-8"))
    if status["state"] != "complete":
        raise ValueError("Render has not completed")
    start, end, fps = status["start"], status["end"], status["fps"]
    total = end - start + 1
    expected = {f"frame_{i:04d}.png" for i in range(start, end + 1)}
    actual = {p.name for p in (output / "frames").glob("*.png")}
    if actual != expected or any((output / "frames" / name).stat().st_size == 0 for name in expected):
        raise ValueError("Frame count/names do not match the completed render")
    signature = hashlib.sha256((output / "project.blend").read_bytes()).hexdigest()
    if signature != status["blend_sha256"]:
        raise ValueError("Project changed after rendering; use a separate output directory and render again")
    destination = output / "animation.mp4"
    if destination.exists():
        raise FileExistsError("Movie already exists; rename it before re-encoding")
    duration = total / fps
    command = [args.ffmpeg, "-hide_banner", "-n", "-framerate", str(fps), "-start_number", str(start),
               "-i", str(output / "frames" / "frame_%04d.png")]
    if args.audio:
        command += ["-i", str(args.audio.resolve()), "-map", "0:v:0", "-map", "1:a:0",
                    "-af", "apad", "-c:a", "aac", "-b:a", "192k"]
    command += ["-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
                "-t", str(duration), "-movflags", "+faststart", str(destination)]
    run(command)
    decoded = run([args.ffmpeg, "-hide_banner", "-i", str(destination), "-map", "0:v:0", "-f", "null", "-"])
    counts = re.findall(r"frame=\s*(\d+)", decoded)
    if not counts or int(counts[-1]) != total:
        raise ValueError("Decoded movie frame count differs from the rendered sequence")
    stream = next((line for line in decoded.splitlines() if "Video: h264" in line), "")
    rate = re.search(r"\b(\d+(?:\.\d+)?) fps", stream)
    size = re.search(r",\s*(\d+)x(\d+)(?=[\s,])", stream)
    duration_match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", decoded)
    if not rate or abs(float(rate[1]) - fps) > max(.02, fps * .0001):
        raise ValueError("Encoded video frame rate does not match the rendered sequence")
    if not duration_match:
        raise ValueError("Could not verify the encoded duration")
    if not size:
        raise ValueError("Could not verify the encoded dimensions")
    actual_duration = int(duration_match[1]) * 3600 + int(duration_match[2]) * 60 + float(duration_match[3])
    if abs(actual_duration - duration) > max(.02, 1 / fps):
        raise ValueError("Encoded duration does not match frame count / fps")
    (output / "video_validation.txt").write_text(decoded, encoding="utf-8")
    run([args.ffmpeg, "-hide_banner", "-y", "-ss", str(duration / 2), "-i", str(destination),
         "-frames:v", "1", str(output / "poster.png")])
    manifest = {"movie": str(destination), "frames": total, "fps": fps, "duration_seconds": duration,
                "bytes": destination.stat().st_size, "decoded_all_frames": True,
                "blend_sha256": signature, "render_signature": status["render_signature"],
                "encoded_resolution": [int(size[1]), int(size[2])],
                "verified_fps": float(rate[1]), "verified_duration_seconds": actual_duration}
    (output / "delivery_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
