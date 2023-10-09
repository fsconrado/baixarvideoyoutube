from app import App

__version__ = "1.0.0"

def main():
    # url_playlist = 'https://www.youtube.com/playlist?list=PLsSJYwgcH6SNeDYsic6lyjLQbZHXUcghP'
    # Uso da classe
    # downloader = YouTubeDownloader(modo='PLAYLIST', url_playlist=url_playlist)
    # downloader.baixar_url_playlist()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()