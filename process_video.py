import os
import sys
import shutil
import subprocess
import time

FFMPEG = r"C:\Users\Arpit Yadav\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\bin\ffmpeg.exe"
INPUT_VIDEO = r"C:\Users\Arpit Yadav\Downloads\final video.mp4"
BGM_MUSIC = r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\chronofact\bg_music.mp3"
OUTPUT_LOCAL = r"C:\Users\Arpit Yadav\.gemini\antigravity\scratch\chronofact\CHRONOFACT_Final_Enhanced_Video.mp4"
OUTPUT_DOWNLOADS = r"C:\Users\Arpit Yadav\Downloads\CHRONOFACT_Final_Enhanced_Video.mp4"
OUTPUT_DESKTOP = r"C:\Users\Arpit Yadav\OneDrive\Desktop\CHRONOFACT_Final_Enhanced_Video.mp4"

print("=" * 70)
print("CHRONOFACT - PROFESSIONAL 100% QUALITY VIDEO ENHANCEMENT ENGINE")
print("=" * 70)
print(f"Input Video: {INPUT_VIDEO}")
print(f"BGM Audio:   {BGM_MUSIC}")

if not os.path.exists(INPUT_VIDEO):
    print("ERROR: Input video not found!")
    sys.exit(1)

if not os.path.exists(BGM_MUSIC):
    print("ERROR: Background music file not found!")
    sys.exit(1)

# Get video duration using ffprobe
ffprobe = r"C:\Users\Arpit Yadav\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\bin\ffprobe.exe"
probe_cmd = [
    ffprobe, "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    INPUT_VIDEO
]
duration_str = subprocess.check_output(probe_cmd).decode().strip()
duration = float(duration_str)
print(f"Video Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")

fade_start = max(0, duration - 6.0)
print(f"Configuring Audio: Vocal clean + BGM fade-out starting at {fade_start:.1f}s")

filter_complex = (
    f"[0:a]highpass=f=80,lowpass=f=16000,acompressor=threshold=-20dB:ratio=3.5:attack=15:release=150:makeup=2.5dB[vocal];"
    f"[1:a]aloop=loop=-1:size=2e+09,volume=0.10,afade=t=in:st=0:d=2.5,afade=t=out:st={fade_start:.1f}:d=5.8[bgm];"
    f"[vocal][bgm]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-16:TP=-1.5:LRA=7[aout];"
    f"[0:v]eq=contrast=1.04:brightness=0.01:saturation=1.05,unsharp=5:5:0.7:5:5:0.0[vout]"
)

cmd = [
    FFMPEG, "-y",
    "-i", INPUT_VIDEO,
    "-i", BGM_MUSIC,
    "-filter_complex", filter_complex,
    "-map", "[vout]",
    "-map", "[aout]",
    "-c:v", "libx264",
    "-crf", "16",
    "-preset", "medium",
    "-profile:v", "high",
    "-level", "4.2",
    "-pix_fmt", "yuv420p",
    "-color_primaries", "bt709",
    "-color_trc", "bt709",
    "-colorspace", "bt709",
    "-movflags", "+faststart",
    "-c:a", "aac",
    "-b:a", "256k",
    OUTPUT_LOCAL
]

print("\nStarting FFmpeg Master Render...")
start_time = time.time()

# Run process
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

out, err = process.communicate()
elapsed = time.time() - start_time

if process.returncode != 0:
    print(f"\n[ERROR] FFmpeg failed with exit code {process.returncode}")
    print(err[-1000:])
    sys.exit(1)

out_size_mb = os.path.getsize(OUTPUT_LOCAL) / (1024 * 1024)
print(f"\nRender Complete in {elapsed:.1f} seconds!")
print(f"Output File Size: {out_size_mb:.2f} MB")

# Copy to Downloads and Desktop
print(f"Copying to Downloads: {OUTPUT_DOWNLOADS}")
shutil.copy2(OUTPUT_LOCAL, OUTPUT_DOWNLOADS)

if os.path.exists(r"C:\Users\Arpit Yadav\OneDrive\Desktop"):
    print(f"Copying to Desktop: {OUTPUT_DESKTOP}")
    shutil.copy2(OUTPUT_LOCAL, OUTPUT_DESKTOP)

print("\nAll deliverables saved successfully!")
