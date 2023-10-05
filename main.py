import os
from tkinter import Tk, Label, Entry, Button, END
from tkinter.ttk import Style
from ttkthemes import ThemedTk
from youtube_downloader import YouTubeDownloader
from app import App


def main():
    # url_playlist = 'https://www.youtube.com/playlist?list=PLsSJYwgcH6SNeDYsic6lyjLQbZHXUcghP'
    # Uso da classe
    # downloader = YouTubeDownloader(modo='PLAYLIST', url_playlist=url_playlist)
    # downloader.baixar_url_playlist()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()