import customtkinter as ctk
import os
import subprocess
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

# настройка темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SoundCloudDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("SoundCloud Likes Downloader")
        self.root.geometry("800x600")
        self.root.configure(fg_color="#2a2a2a")

        # переменные
        self.download_path = ctk.StringVar(value=str(Path.home() / "Downloads" / "SoundCloud"))
        self.username = ctk.StringVar()
        self.is_downloading = False

        self.download_likes = ctk.BooleanVar(value=True)
        self.high_quality = ctk.BooleanVar(value=True)
        self.create_playlist = ctk.BooleanVar(value=False)

        self.create_widgets()
        self.check_scdl()

    def create_widgets(self):
        # мейнфрейм
        main_frame = ctk.CTkFrame(self.root, fg_color="#2a2a2a")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # тайтлы
        title_label = ctk.CTkLabel(main_frame, text="SoundCloud Likes Downloader",
                                   font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))

        # инпут
        input_frame = ctk.CTkFrame(main_frame, fg_color="#2a2a2a")
        input_frame.pack(fill='x', pady=(0, 20))

        ctk.CTkLabel(input_frame, text="SoundCloud Username:").pack(anchor="w", pady=(0,5))
        ctk.CTkEntry(input_frame, textvariable=self.username).pack(fill='x', pady=(0,10))

        ctk.CTkLabel(input_frame, text="Download Path:").pack(anchor="w", pady=(0,5))
        path_frame = ctk.CTkFrame(input_frame, fg_color="#2a2a2a")
        path_frame.pack(fill='x')
        ctk.CTkEntry(path_frame, textvariable=self.download_path).pack(side="left", fill='x', expand=True, padx=(0,10))
        ctk.CTkButton(path_frame, text="Browse", command=self.browse_folder, width=80).pack(side="right")

        # кнопашк
        options_frame = ctk.CTkFrame(main_frame, fg_color="#2a2a2a")
        options_frame.pack(fill='x', pady=(0,20))
        ctk.CTkLabel(options_frame, text="Download Options:").pack(anchor="w", pady=(0,5))
        ctk.CTkCheckBox(options_frame, text="Download Likes", variable=self.download_likes).pack(anchor="w")
        ctk.CTkCheckBox(options_frame, text="High Quality (320kbps)", variable=self.high_quality).pack(anchor="w")
        ctk.CTkCheckBox(options_frame, text="Create M3U Playlist", variable=self.create_playlist).pack(anchor="w")

        # бар
        button_frame = ctk.CTkFrame(main_frame, fg_color="#2a2a2a")
        button_frame.pack(fill='x', pady=(0,20))
        self.download_btn = ctk.CTkButton(button_frame, text="Start Download", command=self.start_download)
        self.download_btn.pack(side="left", padx=(0,10))
        self.stop_btn = ctk.CTkButton(button_frame, text="Stop", command=self.stop_download, state="disabled")
        self.stop_btn.pack(side="left")
        self.progress = ctk.CTkProgressBar(main_frame, mode="indeterminate")
        self.progress.pack(fill='x', pady=(10,20))

        # лог
        ctk.CTkLabel(main_frame, text="Log:").pack(anchor="w")
        self.log_text = ctk.CTkTextbox(main_frame, height=15, wrap="word", fg_color="#1e1e1e", text_color="#4CAF50")
        self.log_text.pack(fill="both", expand=True)

        # стат
        self.status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(main_frame, textvariable=self.status_var, font=("Arial", 9)).pack(fill='x', pady=(10,0))

    # дефы ебаные
    def log_message(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.yview("end")

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.download_path.set(folder)

    def validate_input(self):
        if not self.username.get().strip():
            messagebox.showerror("Error", "Enter SoundCloud username")
            return False
        if not self.download_path.get().strip():
            messagebox.showerror("Error", "Select download path")
            return False
        return True

    def check_scdl(self):
        try:
            result = subprocess.run(["scdl","--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_message("✓ scdl found and ready")
            else:
                self.log_message("✗ scdl not found")
        except:
            self.log_message("✗ scdl not found")

    def start_download(self):
        if not self.validate_input() or self.is_downloading:
            return
        self.is_downloading = True
        self.download_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress.start()
        threading.Thread(target=self.download_worker, daemon=True).start()

    def stop_download(self):
        self.is_downloading = False
        self.download_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress.stop()
        self.status_var.set("Download stopped by user")
        self.log_message("Download stopped by user")

    def download_worker(self):
        username = self.username.get().strip()
        download_dir = self.download_path.get().strip()
        os.makedirs(download_dir, exist_ok=True)
        self.log_message(f"Starting download for: {username}")
        cmd = ["scdl","-l",f"https://soundcloud.com/{username}/likes"]
        if self.high_quality.get():
            cmd.extend(["--original-art","--original-name"])
        if self.create_playlist.get():
            cmd.append("--playlist-file")
        cmd.extend(["--path", download_dir])
        self.log_message(" ".join(cmd))
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, universal_newlines=True, cwd=download_dir)
        while True:
            if not self.is_downloading:
                process.terminate()
                break
            line = process.stdout.readline()
            if line == "" and process.poll() is not None:
                break
            if line:
                self.log_message(line.strip())
        self.is_downloading = False
        self.download_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress.stop()
        self.status_var.set("Download finished")

if __name__ == "__main__":
    root = ctk.CTk()
    app = SoundCloudDownloader(root)
    root.mainloop()
