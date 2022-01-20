from src.util.toespraken import download_conferences


def download_input():
    """
    Downloads the required files for the project
    """
    download_conferences()


if __name__ == "__main__":
    download_input()
