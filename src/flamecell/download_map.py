# download_data.py
import urllib.request

url = "https://heidata.uni-heidelberg.de/file.xhtml?fileId=23053&version=2.0#"  
output_path = "maps/test.tif"

print("Downloading data...")
urllib.request.urlretrieve(url, output_path)
print("Download complete.")
