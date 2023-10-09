import tkinter as tk
from tkinter import messagebox, filedialog
from pytube import YouTube, Playlist
import webbrowser
import os
import subprocess
import threading
import requests
from bs4 import BeautifulSoup
import ctypes


class App(tk.Tk):


    def __init__(self):
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        super().__init__()
        self.base_download_path = ""
        self.title("Super Downloads Youtube")
        # self.base_download_path = os.path.join(os.getcwd(), "music")
        if self.base_download_path and not os.path.exists(self.base_download_path):
            os.makedirs(self.base_download_path)

        # self.url_entry = ttk.Entry(self, width=60, font=("Arial", 12))
        self.url_entry = tk.Entry(self, width=60, font=("Arial", 12))
        self.url_entry.pack(pady=10)

        self.download_btn = tk.Button(self, text="Baixar video(s)", command=self.initiate_download, bg="blue", fg="black", font=("Arial", 12, "bold"), height=2, width=20)
        self.download_btn.pack(pady=10)

        self.cancel_btn = tk.Button(self, text="Cancelar", command=self.cancel_download, fg="red", font=("Arial", 12, "bold"), height=2, width=20)
        self.cancel_btn.pack(pady=10)
        self.cancel_btn.config(state=tk.DISABLED)

        self.terminal_output = tk.Text(self, bg='black', fg='green', height=15, width=60, font=("Courier", 12))
        self.terminal_output.pack(pady=20, fill=tk.BOTH, expand=True)

        self.github_frame = tk.Frame(self, bg="black")
        self.github_frame.pack(fill=tk.X, pady=10)
        self.github_label = tk.Label(self.github_frame, text="Desenvolvido por fsconrado", fg="blue", bg="black", cursor="hand2")
        self.github_label.pack(pady=5, padx=20)
        self.github_label.bind("<Button-1>", self.open_github)

        self.cancel_flag = threading.Event()

        # Adicionar o placeholder
        self.placeholder_text = "Adicione aqui a URL do vídeo do YouTube ou da playlist"
        self.url_entry.insert(0, self.placeholder_text)
        self.url_entry.bind("<FocusIn>", self.clear_placeholder)
        self.url_entry.bind("<FocusOut>", self.add_placeholder)
        self.url_entry.config(fg="grey")  # Cor do placeholder

    def initiate_download(self):
        self.ask_directory()
        self.download_thread = threading.Thread(target=self.start_download)
        self.download_thread.start()
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)

    def cancel_download(self):
        self.cancel_flag.set()

    def start_download(self):
        url = self.url_entry.get()
        if "youtube.com/watch?" in url:
            video_folder = os.path.join(self.base_download_path, self.clean_title(YouTube(url).title))
            if not os.path.exists(video_folder):
                os.makedirs(video_folder)
            self.download_video(url, video_folder)
        elif "youtube.com/playlist?" in url:
            playlist_name = self.get_playlist_name(url)
            playlist_folder = os.path.join(self.base_download_path, playlist_name)
            if not os.path.exists(playlist_folder):
                os.makedirs(playlist_folder)
            for video_url in Playlist(url).video_urls:
                if self.cancel_flag.is_set():
                    self.terminal_output.insert(tk.END, "Download cancelado pelo usuário.\n")
                    break
                self.download_video(video_url, playlist_folder)
        else:
            self.terminal_output.insert(tk.END, "URL fornecida inválida.\n")

        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.cancel_flag.clear()
        self.post_download()

    def get_playlist_name(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.split('-')[0].strip()  # Assume the format "Playlist Name - YouTube"
        return self.clean_title(title)

    def download_video(self, url, download_folder):
        yt = YouTube(url, on_progress_callback=self.show_progress)
        video = yt.streams.get_highest_resolution()
        self.current_download_file = os.path.join(download_folder, video.default_filename)
        self.terminal_output.insert(tk.END, f"Baixando o vídeo: {yt.title}\n")
        video.download(output_path=download_folder)

    def show_progress(self, stream, chunk, bytes_remaining):
        self.terminal_output.insert(tk.END, ".")
        self.terminal_output.see(tk.END)
        self.update()

        # Check for cancel flag
        if self.cancel_flag.is_set():
            self.terminal_output.insert(tk.END, "Cancelando o download...\n")
            # If file exists, remove it
            if os.path.exists(self.current_download_file):
                os.remove(self.current_download_file)
            raise Exception("Download foi cancelado pelo usuário.")

    def clean_title(self, title):
        return "".join([c if c.isalnum() else "_" for c in title])

    def show_progress(self, stream, chunk, bytes_remaining):
        self.terminal_output.insert(tk.END, ".")
        self.terminal_output.see(tk.END)
        self.update()

    def post_download(self):
        response = messagebox.askyesnocancel("Download Completo", "Deseja encerrar o programa e ir para os vídeos baixados ou continuar baixando novos vídeos?")
        if response:  # Yes
            self.open_folder()
            self.quit()
        elif response is None:  # Cancel
            return
        else:  # No
            self.terminal_output.delete(1.0, tk.END)

    def open_folder(self):
        if os.name == 'nt':  # For Windows
            subprocess.Popen(['explorer', self.base_download_path])
        elif os.name == 'posix':  # For MacOS and Linux
            subprocess.Popen(['open', self.base_download_path])
        else:
            self.terminal_output.insert(tk.END, "Não foi possível abrir a pasta.\n")

    def open_github(self, event):
        webbrowser.open("https://github.com/fsconrado")

    # Função para remover o placeholder
    def clear_placeholder(self, e=None):
        if self.url_entry.get() == self.placeholder_text:
            self.url_entry.delete(0, tk.END)
            self.url_entry.config(fg="black")  # Cor do texto padrão

    # Função para adicionar o placeholder
    def add_placeholder(self, e=None):
        if not self.url_entry.get():
            self.url_entry.insert(0, self.placeholder_text)
            self.url_entry.config(fg="grey")  # Cor do placeholder

    def ask_directory(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:  # Se o usuário selecionar uma pasta
            # Adicionando o subdiretório "YouTubeDownloads" ao diretório selecionado pelo usuário
            self.base_download_path = os.path.join(folder_selected, "YouTubeDownloads")
        else:  # Se o usuário cancelar a seleção
            self.base_download_path = os.path.join(os.getcwd(), "YouTubeDownloads")

        # Criar o diretório base se ele não existir
        if self.base_download_path and not os.path.exists(self.base_download_path):
            os.makedirs(self.base_download_path)


if __name__ == "__main__":
    app = App()
    app.mainloop()
