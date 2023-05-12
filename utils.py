import os
import tempfile
import requests
from ffmpeg_downloader import _backend as ffdl
import shutil

def check_download_file_size(url):
    header = requests.get(url)
    if 'Content-length' not in header.headers:
        return 0
    size = header.headers['Content-length']
    return int(size)

def file_download(url, *, auth=None):
    file_name = url[url.rfind('/') + 1:] #aaaa/bbb/ccc.png -> ccc.png
    save_path = os.getcwd() + "/downloaded_files/" + file_name
    with requests.get(url, stream=True, auth=auth) as r:
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return save_path

def make_download_link(path):
    with open(path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"https://file.io", files=files).json()
    return response['link']

def init():
    os.makedirs("downloaded_files", exist_ok=True)
    os.makedirs("items", exist_ok=True)

    items_path = os.path.join(os.getcwd(), "items")
    platform_extension = ".exe" if os.name == "nt" else ""

    if not os.path.isfile(os.path.join(items_path, "ffmpeg" + platform_extension)):
        print("downloading ffmpeg")
        
        with tempfile.TemporaryDirectory() as tempdir:

            version = ffdl.search("release", True)

            info = ffdl.gather_download_info(*version)
            ffdl.download(info, dst=os.path.join(os.getcwd(), tempdir))
            shutil.unpack_archive(os.path.join(tempdir, info[0][0]), tempdir)

            if os.name == "nt":
                archive_name = info[0][0].replace(".zip", "")
                shutil.move(os.path.join(tempdir, archive_name, "bin", "ffmpeg") + platform_extension, os.path.join(items_path, "ffmpeg" + platform_extension))
                shutil.move(os.path.join(tempdir, archive_name, "bin", "ffprobe") + platform_extension, os.path.join(items_path, "ffprobe" + platform_extension))
            else:
                archive_name = info[0][0].replace(".tar.xz", "")
                shutil.move(os.path.join(tempdir, archive_name, "ffmpeg") + platform_extension, os.path.join(items_path, "ffmpeg" + platform_extension))
                shutil.move(os.path.join(tempdir, archive_name, "ffprobe") + platform_extension, os.path.join(items_path, "ffprobe" + platform_extension))
