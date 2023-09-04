"""
This script is used to download the latest release of a specified GitHub project.

Not used in Github Actions.

"""
import requests
import os

owner = "nishio"
repo = "omoikane-embed"
output_dir = "."


def download_latest_release(owner, repo, output_dir="."):
    """
    Download the latest release of a specified GitHub project.

    Parameters:
    - owner (str): Owner of the GitHub repository.
    - repo (str): Name of the GitHub repository.
    - output_dir (str, optional): Directory to save the downloaded files. Defaults to current directory.
    """

    # Construct the API URL
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

    # Fetch the latest release data
    response = requests.get(api_url)
    response.raise_for_status()  # raise exception if invalid response
    data = response.json()

    # Check for assets
    if not data.get("assets"):
        print("No assets found for the latest release.")
        return

    # Download each asset
    for asset in data["assets"]:
        download_url = asset["browser_download_url"]
        filename = os.path.join(output_dir, asset["name"])

        print(f"Downloading {filename} ...")
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    print("Download completed!")


if __name__ == "__main__":
    download_latest_release(owner, repo, output_dir)
