from src.util.toespraken import download_conferences
from src.util.besmettingen import download_infections


def download_input():
    """
    Downloads the required files for the project
    """
    download_conferences()
    download_infections()


if __name__ == "__main__":
    download_input()
