import os
import yt_dlp
import tkinter as tk
from tkinter import messagebox
from youtube_search_python import YoutubeSearch



# Function to search YouTube for videos
def search_youtube(query):
    results = YoutubeSearch(query, max_results=5).to_dict()
    return results

# Function to display search results in the GUI
def display_results(results):
    for widget in result_frame.winfo_children():
        widget.destroy()  # Clear previous results
    
    for result in results:
        title = result['title']
        url = f"https://www.youtube.com{result['url_suffix']}"
        
        # Create a button for each video result
        button = tk.Button(result_frame, text=title, width=40, command=lambda url=url: download_video(url))
        button.pack(pady=5)

# Function to download video using yt-dlp
def download_video(url):
    try:
        # yt-dlp options
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(os.getcwd(), '%(title)s.%(ext)s'),
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        messagebox.showinfo("Success", "Download complete!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while downloading: {str(e)}")

# Function to handle search button click
def search_button_click():
    query = search_entry.get()
    if query:
        results = search_youtube(query)
        display_results(results)
    else:
        messagebox.showwarning("Input Error", "Please enter a search term.")

# Create the GUI using Tkinter
root = tk.Tk()
root.title("YouTube Browser & Downloader")

# Create the search input field
search_label = tk.Label(root, text="Enter YouTube search query:")
search_label.pack(pady=10)
search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=5)

# Create the search button
search_button = tk.Button(root, text="Search", command=search_button_click)
search_button.pack(pady=10)

# Frame to display the results
result_frame = tk.Frame(root)
result_frame.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()
