"""
download cache from Github Release
When some error occurs, ignore it and continue.
"""
import subprocess


def main():
    try:
        LATEST_RELEASE_TAG = subprocess.check_output(
            "gh release view --json tagName --jq '.tagName'", shell=True
        ).strip()
        print("LATEST_RELEASE_TAG:", LATEST_RELEASE_TAG)
    except subprocess.CalledProcessError:
        print("Failed to get latest release tag.")
        return

    try:
        ASSET_DOWNLOAD_URL = subprocess.check_output(
            f"gh release view {LATEST_RELEASE_TAG} --json assets --jq '.assets[0].url'",
            shell=True,
        ).strip()
        print("ASSET_DOWNLOAD_URL:", ASSET_DOWNLOAD_URL)
    except subprocess.CalledProcessError:
        print("Failed to get asset download url.")
        return

    try:
        subprocess.run(f"wget {ASSET_DOWNLOAD_URL}", shell=True, check=False)
    except subprocess.CalledProcessError:
        print("Failed to download asset.")
        return


main()
