import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
from pathlib import Path

class SoundCloudDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("SoundCloud Likes Downloader")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        # Настройка темной темы
        self.setup_dark_theme()
        
        # Переменные
        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads" / "SoundCloud"))
        self.username = tk.StringVar()
        self.is_downloading = False
        
        self.create_widgets()
        self.check_scdl()
    
    def setup_dark_theme(self):
        """Настройка темной темы для виджетов"""
        style = ttk.Style()
        
        # Настройка цветов для ttk виджетов
        style.theme_use('clam')
        
        # Цвета темной темы с зелеными акцентами
        colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'select_bg': '#2d5016',
            'select_fg': '#ffffff',
            'button_bg': '#2d5016',
            'button_fg': '#ffffff',
            'entry_bg': '#2a2a2a',
            'entry_fg': '#ffffff',
            'accent': '#4CAF50'
        }
        
        # Конфигурация стилей
        style.configure('Dark.TFrame', background=colors['bg'])
        style.configure('Dark.TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('Dark.TButton', background=colors['button_bg'], foreground=colors['button_fg'])
        style.map('Dark.TButton', 
                 background=[('active', colors['accent']), ('pressed', '#2d5016')])
        style.configure('Dark.TEntry', background=colors['entry_bg'], foreground=colors['entry_fg'],
                       fieldbackground=colors['entry_bg'])
        
    def create_widgets(self):
        """Создание интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="SoundCloud Likes Downloader", 
                               font=('Arial', 16, 'bold'), style='Dark.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Фрейм для ввода данных
        input_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        input_frame.pack(fill='x', pady=(0, 20))
        
        # Поле для имени пользователя
        ttk.Label(input_frame, text="SoundCloud Username:", style='Dark.TLabel').pack(anchor='w')
        username_entry = ttk.Entry(input_frame, textvariable=self.username, 
                                  font=('Arial', 10), style='Dark.TEntry')
        username_entry.pack(fill='x', pady=(5, 15))
        
        # Поле для пути загрузки
        ttk.Label(input_frame, text="Download Path:", style='Dark.TLabel').pack(anchor='w')
        
        path_frame = ttk.Frame(input_frame, style='Dark.TFrame')
        path_frame.pack(fill='x', pady=(5, 15))
        
        path_entry = ttk.Entry(path_frame, textvariable=self.download_path, 
                              font=('Arial', 10), style='Dark.TEntry')
        path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_folder,
                               style='Dark.TButton')
        browse_btn.pack(side='right')
        
        # Опции загрузки
        options_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        options_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(options_frame, text="Download Options:", style='Dark.TLabel').pack(anchor='w', pady=(0, 5))
        
        # Чекбоксы для опций
        self.download_likes = tk.BooleanVar(value=True)
        self.high_quality = tk.BooleanVar(value=True)
        self.create_playlist = tk.BooleanVar(value=False)
        
        likes_cb = tk.Checkbutton(options_frame, text="Download Likes", 
                                 variable=self.download_likes,
                                 bg='#1e1e1e', fg='#ffffff', selectcolor='#2a2a2a',
                                 activebackground='#1e1e1e', activeforeground='#4CAF50')
        likes_cb.pack(anchor='w', pady=2)
        
        quality_cb = tk.Checkbutton(options_frame, text="High Quality (320kbps)", 
                                   variable=self.high_quality,
                                   bg='#1e1e1e', fg='#ffffff', selectcolor='#2a2a2a',
                                   activebackground='#1e1e1e', activeforeground='#4CAF50')
        quality_cb.pack(anchor='w', pady=2)
        
        playlist_cb = tk.Checkbutton(options_frame, text="Create M3U Playlist", 
                                    variable=self.create_playlist,
                                    bg='#1e1e1e', fg='#ffffff', selectcolor='#2a2a2a',
                                    activebackground='#1e1e1e', activeforeground='#4CAF50')
        playlist_cb.pack(anchor='w', pady=2)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        button_frame.pack(fill='x', pady=(0, 20))
        
        self.download_btn = ttk.Button(button_frame, text="Start Download", 
                                      command=self.start_download, style='Dark.TButton')
        self.download_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                  command=self.stop_download, style='Dark.TButton',
                                  state='disabled')
        self.stop_btn.pack(side='left')
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=(0, 20))
        
        # Лог вывода
        ttk.Label(main_frame, text="Log:", style='Dark.TLabel').pack(anchor='w')
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15,
                                                 bg='#2a2a2a', fg='#ffffff',
                                                 insertbackground='#4CAF50',
                                                 font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                style='Dark.TLabel', font=('Arial', 8))
        status_label.pack(fill='x', pady=(10, 0))
    
    def check_scdl(self):
        """Проверка наличия scdl"""
        try:
            result = subprocess.run(['scdl', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_message("✓ scdl found and ready")
                self.status_var.set("Ready - scdl detected")
            else:
                self.log_message("✗ scdl not found or not working properly")
                self.show_scdl_help()
        except FileNotFoundError:
            self.log_message("✗ scdl not found")
            self.show_scdl_help()
        except subprocess.TimeoutExpired:
            self.log_message("✗ scdl check timed out")
            self.show_scdl_help()
    
    def show_scdl_help(self):
        """Показать помощь по установке scdl"""
        help_text = """
scdl not found! Please install it first:

1. Install Python 3.7+ if not already installed
2. Install scdl using pip:
   pip install scdl

3. Or using pip3:
   pip3 install scdl

For more information visit: https://github.com/flyingrub/scdl
        """
        self.log_message(help_text)
        self.status_var.set("Error: scdl not found")
    
    def browse_folder(self):
        """Выбор папки для загрузки"""
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.download_path.set(folder)
    
    def log_message(self, message):
        """Добавить сообщение в лог"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def validate_input(self):
        """Проверка входных данных"""
        if not self.username.get().strip():
            messagebox.showerror("Error", "Please enter a SoundCloud username")
            return False
        
        if not self.download_path.get().strip():
            messagebox.showerror("Error", "Please select a download path")
            return False
        
        return True
    
    def start_download(self):
        """Запуск загрузки"""
        if not self.validate_input():
            return
        
        if self.is_downloading:
            messagebox.showwarning("Warning", "Download already in progress")
            return
        
        self.is_downloading = True
        self.download_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')
        self.progress.start()
        
        # Запуск в отдельном потоке
        download_thread = threading.Thread(target=self.download_worker, daemon=True)
        download_thread.start()
    
    def stop_download(self):
        """Остановка загрузки"""
        self.is_downloading = False
        self.download_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')
        self.progress.stop()
        self.status_var.set("Download stopped by user")
        self.log_message("Download stopped by user")
    
    def download_worker(self):
        """Рабочий поток для загрузки"""
        try:
            username = self.username.get().strip()
            download_dir = self.download_path.get().strip()
            
            # Создание директории если не существует
            os.makedirs(download_dir, exist_ok=True)
            
            self.log_message(f"Starting download for user: {username}")
            self.log_message(f"Download directory: {download_dir}")
            self.status_var.set(f"Downloading likes for {username}...")
            
            # Формирование команды scdl
            cmd = ['scdl', '-l', f'https://soundcloud.com/{username}/likes']
            
            if self.high_quality.get():
                cmd.extend(['--original-art', '--original-name'])
            
            if self.create_playlist.get():
                cmd.append('--playlist-file')
            
            cmd.extend(['--path', download_dir])
            
            self.log_message(f"Command: {' '.join(cmd)}")
            
            # Запуск scdl
            process = subprocess.Popen(cmd, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT,
                                     text=True, 
                                     universal_newlines=True,
                                     cwd=download_dir)
            
            # Чтение вывода в реальном времени
            while True:
                if not self.is_downloading:
                    process.terminate()
                    break
                
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    self.log_message(output.strip())
            
            return_code = process.poll()
            
            if return_code == 0:
                self.log_message("✓ Download completed successfully!")
                self.status_var.set("Download completed")
                messagebox.showinfo("Success", "Download completed successfully!")
            elif self.is_downloading:  # Если не было остановлено пользователем
                self.log_message(f"✗ Download failed with return code: {return_code}")
                self.status_var.set("Download failed")
                messagebox.showerror("Error", "Download failed. Check the log for details.")
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log_message(error_msg)
            self.status_var.set("Error occurred")
            if self.is_downloading:  # Показать ошибку только если не было остановлено
                messagebox.showerror("Error", error_msg)
        
        finally:
            self.is_downloading = False
            self.download_btn.configure(state='normal')
            self.stop_btn.configure(state='disabled')
            self.progress.stop()

def main():
    root = tk.Tk()
    app = SoundCloudDownloader(root)
    
    # Центрирование окна
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()