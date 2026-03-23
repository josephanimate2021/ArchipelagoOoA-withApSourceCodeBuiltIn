import subprocess
import sys
import os
import platform
import urllib.request
import tarfile
import zipfile
import stat
import Utils

# URLs for prebuilt xdelta3 binaries (official or trusted builds)
XDELTA_BASE = "https://github.com/jmacd/xdelta-gpl/releases/download/v3.1.0/xdelta3-3.1.0-x86_64"

XDELTA_BINARIES = {
    "windows": ".exe.zip",
    "linux":   ".tar.gz"
    # I could not find a macos release for some reason, so sadly I'll have to skip macos.
}
XDELTA_FILE_EXTENSIONS = {
    "windows": ".exe"
}

BIN_DIR = Utils.user_path()

def ensure_xdelta():
    """Ensure the correct xdelta3 binary is available locally."""
    system = platform.system().lower()
    url = XDELTA_BASE + XDELTA_BINARIES[system]
    if not url:
        raise RuntimeError(f"xdelta patching failed due to an unsupported os. OS in question is {system}")

    # Determine binary 
    xdelta_filename = os.path.basename(XDELTA_BASE)
    if XDELTA_FILE_EXTENSIONS[system]:
        xdelta_filename += XDELTA_FILE_EXTENSIONS[system]
    exe_path = os.path.join(BIN_DIR, xdelta_filename)

    if os.path.isfile(exe_path):
        return exe_path  # Already downloaded

    print(f"Downloading xdelta3 for {system}...")
    os.makedirs(BIN_DIR, exist_ok=True)

    archive_path = os.path.join(BIN_DIR, os.path.basename(url))
    urllib.request.urlretrieve(url, archive_path)

    # Extract based on file type
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(BIN_DIR)
    elif archive_path.endswith(".tar.gz"):
        with tarfile.open(archive_path, "r:gz") as tar_ref:
            tar_ref.extractall(BIN_DIR)
    else:
        raise RuntimeError("Unknown archive format for xdelta3.")

    os.remove(archive_path)

    # Make executable on Unix
    if system != "windows":
        os.chmod(exe_path, os.stat(exe_path).st_mode | stat.S_IEXEC)

    print(f"xdelta3 ready at {exe_path}")
    return exe_path


def apply_xdelta_patch(original_file, patch_file) -> bytes: # type: ignore
    print("Because you chose a setting that required xdelta ROM patching, things may take longer depending on whatever or not you have xdelta installed inside Archipelago. When debugging, be sure to look at the logs just in case to find something that may be or feel off.")
    """Apply an xdelta3 patch to a file."""
    exe = ensure_xdelta()
    try:
        if not os.path.isfile(original_file):
            raise FileNotFoundError(f"Original file not found: {original_file}")
        if not os.path.isfile(patch_file):
            raise FileNotFoundError(f"Patch file not found: {patch_file}")

        cmd = [exe, "-f", "-d", "-s", original_file, patch_file, Utils.user_path("ages.gbc")]
        cmd_stats = subprocess.call(cmd)
        if cmd_stats == 0:
            return bytes(open(cmd[6], "rb").read())
        else:
            raise Exception(f"xdelta command has failed with code {cmd_stats}")

    except subprocess.CalledProcessError as e:
        raise Exception(f"Error applying patch: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error: {e}")
