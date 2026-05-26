#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple GUI for DonghuaWorld Downloader
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys

try:
    from donghua_downloader import DonghuaWorldDownloader
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from donghua_downloader import DonghuaWorldDownloader


class DownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DonghuaWorld Downloader")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        self.downloader = None
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL input
        url_frame = ttk.LabelFrame(main_frame, text="Download URL", padding="5")
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(url_frame, width=60)
        self.url_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        url_frame.columnconfigure(1, weight=1)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="5")
        options_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(options_frame, text="Output Dir:").grid(row=0, column=0, sticky=tk.W)
        self.dir_entry = ttk.Entry(options_frame, width=50)
        self.dir_entry.insert(0, os.path.join(os.path.expanduser("~"), "Downloads", "donghua"))
        self.dir_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        ttk.Button(options_frame, text="Browse", command=self.browse_dir).grid(row=0, column=2)
        
        ttk.Label(options_frame, text="Episode Range:").grid(row=1, column=0, sticky=tk.W)
        range_frame = ttk.Frame(options_frame)
        range_frame.grid(row=1, column=1, sticky=tk.W)
        
        self.start_ep = ttk.Spinbox(range_frame, from_=1, to=999, width=5)
        self.start_ep.set(1)
        self.start_ep.pack(side=tk.LEFT)
        ttk.Label(range_frame, text=" - ").pack(side=tk.LEFT)
        self.end_ep = ttk.Spinbox(range_frame, from_=1, to=999, width=5)
        self.end_ep.set(999)
        self.end_ep.pack(side=tk.LEFT)
        
        options_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.download_btn = ttk.Button(button_frame, text="Download Single Episode", command=self.download_single)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        self.download_series_btn = ttk.Button(button_frame, text="Download Series", command=self.download_series)
        self.download_series_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_download, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X)
    
    def browse_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def download_single(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        self.start_download(url, single=True)
    
    def download_series(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a series URL")
            return
        
        start = int(self.start_ep.get())
        end = int(self.end_ep.get())
        
        self.start_download(url, single=False, start_ep=start, end_ep=end)
    
    def start_download(self, url, single=True, start_ep=1, end_ep=999):
        self.download_btn.config(state=tk.DISABLED)
        self.download_series_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("Downloading...")
        
        output_dir = self.dir_entry.get()
        
        def run_download():
            try:
                self.downloader = DonghuaWorldDownloader(output_dir=output_dir, verbose=False)
                
                if single:
                    self.log(f"Downloading: {url}")
                    success = self.downloader.download_episode(url)
                    if success:
                        self.log("Download completed!")
                    else:
                        self.log("Download failed!")
                else:
                    self.log(f"Downloading series: {url}")
                    self.log(f"Episode range: {start_ep} - {end_ep}")
                    self.downloader.download_series(url, start_ep, end_ep)
                    self.log("Series download completed!")
                
            except Exception as e:
                self.log(f"Error: {str(e)}")
            finally:
                self.download_btn.config(state=tk.NORMAL)
                self.download_series_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.status_var.set("Ready")
        
        thread = threading.Thread(target=run_download, daemon=True)
        thread.start()
    
    def stop_download(self):
        self.status_var.set("Stopping...")
        self.log("Stopping download...")


if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderGUI(root)
    root.mainloop()
