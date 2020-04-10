from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)


file1 = drive.CreateFile()
file1.SetContentFile(path_to_your_file)
file1.Upload()