from src.util.conferences import download_conferences
from src.util.infections import download_infections


def download_input():
    """
    Downloads the required files for the project
    """
    download_conferences()
    download_infections()


if __name__ == "__main__":
    download_input()
