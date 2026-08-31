import imageio_ffmpeg
import os
import shutil

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_exe)
ffmpeg_alias = os.path.join(ffmpeg_dir, "ffmpeg.exe")

if not os.path.exists(ffmpeg_alias):
    try:
        shutil.copy(ffmpeg_exe, ffmpeg_alias)
    except PermissionError:
        pass

if ffmpeg_dir not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]

from pydub import AudioSegment
AudioSegment.converter = ffmpeg_alias

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    try:
        import yt_dlp
    except ImportError as exc:
        raise ImportError(
            "Missing dependency: yt_dlp is required to download YouTube audio. "
            "Install it with 'pip install yt-dlp' or via requirements.txt."
        ) from exc

    final_path = {}

    def post_hook(d):
        if d['status'] == 'finished':
            final_path['filename'] = d.get('info_dict', {}).get('filepath') or d.get('filename')

    js_runtime = shutil.which("node") or shutil.which("deno") or shutil.which("bun")
    if not js_runtime:
        raise RuntimeError(
            "yt-dlp now requires a JavaScript runtime for YouTube downloads. "
            "Install Node.js, Deno, or Bun and make sure it is on PATH."
        )

    ydl_opts = {
        "format": "bestaudio[protocol=m3u8]/bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "ffmpeg_location": imageio_ffmpeg.get_ffmpeg_exe(),
        "postprocessor_hooks": [post_hook],
        "js_runtimes": {os.path.splitext(os.path.basename(js_runtime))[0].lower(): {"path": js_runtime}},
        "extractor_args": {"youtube": {"player_client": ["tv_embedded"]}},
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    return final_path.get('filename')

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks