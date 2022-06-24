import os
modules = ["colorama","youtube_dl","PyNaCl"]
for module in modules:
  os.system(f"pip install {module}")
os.system("python3 main.py")