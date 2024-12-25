# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# import yt_dlp
# import os
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from urllib.parse import urlparse, parse_qs

# # Initialize FastAPI app
# app = FastAPI()

# # Add CORS middleware to allow frontend communication
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins, modify if necessary
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all HTTP methods
#     allow_headers=["*"],  # Allows all headers
# )

# # Path to store the downloaded video temporarily
# TEMP_DIR = "downloads"
# if not os.path.exists(TEMP_DIR):
#     os.makedirs(TEMP_DIR)

# # Use ThreadPoolExecutor to handle yt-dlp synchronously
# executor = ThreadPoolExecutor(1)

# # Function to download video using yt-dlp
# def download_video_sync(url: str, filename: str):
#     ydl_opts = {
#         'format': 'best',
#         'outtmpl': os.path.join(TEMP_DIR, filename),
#         'noplaylist': True,  # Avoid downloading playlists
#     }
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([url])

# # Extract video ID from URL
# def extract_video_id(url: str) -> str:
#     try:
#         query_params = parse_qs(urlparse(url).query)
#         video_id = query_params.get('v', [None])[0]
#         if not video_id:
#             raise ValueError("Invalid YouTube URL")
#         return video_id
#     except Exception as e:
#         raise HTTPException(status_code=400, detail="Invalid URL format")

# # Endpoint to download video
# @app.post("/download_video/")
# async def download_video_endpoint(url: str):
#     try:
#         # Extract video ID from the URL
#         video_id = extract_video_id(url)
#         filename = f"{video_id}.mp4"

#         # Run the download in a separate thread to avoid blocking
#         await asyncio.get_event_loop().run_in_executor(executor, download_video_sync, url, filename)
        
#         # Return the path to the downloaded video
#         return {"file": filename}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error downloading video: {str(e)}")

# # Endpoint to serve the video file
# @app.get("/download/{filename}")
# async def get_downloaded_video(filename: str):
#     video_path = os.path.join(TEMP_DIR, filename)
#     if os.path.exists(video_path):
#         return FileResponse(video_path)
#     raise HTTPException(status_code=404, detail="File not found")
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import uuid

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, modify if necessary
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Path to store the downloaded video temporarily
TEMP_DIR = "downloads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Function to download video using yt-dlp
def download_video(url: str, filename: str):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(TEMP_DIR, filename),
        'noplaylist': True,  # Avoid downloading playlists
        'quiet': False,  # Set to False for verbose output (for debugging)
        'progress_hooks': [lambda d: print(d)]  # For download progress
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading video: {str(e)}")

# Endpoint to download video
@app.post("/download_video/")
async def download_video_endpoint(url: str):
    try:
        # Generate a unique filename using UUID
        filename = f"{uuid.uuid4().hex}.mp4"
        
        # Download the video
        download_video(url, filename)
        
        # Return the filename of the downloaded video
        return {"file": filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading video: {str(e)}")

# Endpoint to serve the downloaded video file
@app.get("/download/{filename}")
async def get_downloaded_video(filename: str):
    video_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(video_path):
        return FileResponse(video_path)
    raise HTTPException(status_code=404, detail="File not found")
