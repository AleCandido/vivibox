Start-BitsTransfer -Source "https://www.python.org/ftp/python/3.9.9/python-3.9.9-amd64.exe"
.\python-3.9.9-amd64.exe
rm .\python-3.9.9-amd64.exe
setx PATH "%PATH%;$HOME\AppData\Local\Programs\Python\Python39\Scripts\;$HOME\AppData\Local\Programs\Python\Launcher\"