# download_data.py
from urllib.request import urlretrieve

def download_tif(file_id, out_path):
    url = "https://heidata.uni-heidelberg.de/file.xhtml?fileId={file_id}&version=2.0"
    dst = out_path
    print("downloading...")
    urlretrieve(url, dst)


download_tif(23030, "maps/CY_landuse_10m.tif")