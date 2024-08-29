import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import yt_dlp as youtube_dl
import threading
from PIL import Image, ImageTk
import sys

def resource_path(relative_path):
    """ Get the absolute path to a resource in the packaged executable """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None

def choose_location():
    download_path = filedialog.askdirectory()
    if download_path:
        location_label.config(text=f"Download Location: {download_path}")
        root.download_path = download_path

def download_video():
    if not is_ffmpeg_installed():
        messagebox.showerror("Error", "ffmpeg is required for merging formats but is not installed.")
        return

    url = url_entry.get()
    quality = quality_var.get()
    
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL.")
        return
    
    if not hasattr(root, 'download_path') or not root.download_path:
        messagebox.showerror("Error", "Please choose a download location.")
        return

    ydl_opts = {
        'outtmpl': os.path.join(root.download_path, '%(title)s.%(ext)s'),
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4',
    }

    download_button.config(state=tk.DISABLED)
    progress_var.set(0)  # Reset the progress bar
    progress_bar.pack(pady=10)  # Show the progress bar
    threading.Thread(target=start_download, args=(ydl_opts, url)).start()

def start_download(ydl_opts, url):
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", "Download completed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        download_button.config(state=tk.NORMAL)
        progress_bar.pack_forget()  # Hide the progress bar when done

def progress_hook(d):
    if d['status'] == 'downloading':
        downloaded = d.get('_percent_str', 'N/A').strip()
        speed = d.get('_speed_str', 'N/A').strip()
        eta = d.get('_eta_str', 'N/A').strip()

        # Update progress bar
        if 'total_bytes' in d and d['total_bytes'] > 0:
            progress_percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
            progress_var.set(progress_percentage)

        progress_label.config(text=f"Downloaded: {downloaded} at {speed}, ETA: {eta}")
    elif d['status'] == 'finished':
        progress_label.config(text="Download complete! Processing video...")

# Create the main window
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("500x550")

# Load and resize the logo
image_path = resource_path("logo.png")
image = Image.open(image_path)
image = image.resize((50, 50), Image.Resampling.LANCZOS)
logo = ImageTk.PhotoImage(image)

# Add a banner at the top
banner_frame = tk.Frame(root, bg="#ff6f00")
banner_frame.pack(fill=tk.X)

banner_logo = tk.Label(banner_frame, image=logo, bg="#ff6f00")
banner_logo.pack(side=tk.LEFT, padx=10)

banner_text = tk.Label(banner_frame, text="YouTube Video Downloader", font=("Arial", 16), fg="white", bg="#ff6f00")
banner_text.pack(side=tk.LEFT, padx=10)

# Choose download location
location_button = tk.Button(root, text="Choose Download Location", command=choose_location)
location_button.pack(pady=10)

location_label = tk.Label(root, text="Download Location: Not selected")
location_label.pack(pady=5)

# Create and place widgets
tk.Label(root, text="Enter YouTube URL:").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=10)

tk.Label(root, text="Select Video Quality:").pack(pady=10)
quality_var = tk.StringVar(value="720")
quality_menu = ttk.Combobox(root, textvariable=quality_var, values=["144", "240", "360", "480", "720", "1080"])
quality_menu.pack(pady=10)

download_button = tk.Button(root, text="Download Video", command=download_video)
download_button.pack(pady=10)

# Progress indicator
progress_label = tk.Label(root, text="")
progress_label.pack(pady=10)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack_forget()  # Hide progress bar initially

# Run the application
root.mainloop()
