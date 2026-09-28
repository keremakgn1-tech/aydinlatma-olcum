[app]
title = Aydinlatma Olcum
package.name = aydinlatmaolcum
package.domain = org.kerem

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 1.0

requirements = hostpython3==3.11.9,python3==3.11.9,kivy==2.3.1,openpyxl,fpdf2,fonttools,et_xmlfile
p4a.source_dir = ./p4a-src

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/app_icon.png
presplash.filename = %(source.dir)s/presplash.png
android.presplash_color = #0E0F12

# p4a'nin Kivy (sdl2) bootstrap'i AndroidManifest'e windowSoftInputMode HIC
# eklemiyor (bu sadece webview bootstrap'inde var) - yani klavye acilinca
# pencere native olarak hicbir zaman "adjustResize" ile kucalmiyordu. Bu hook
# derleme sirasinda uretilen manifest'i yamayip bu ozelligi ekliyor - klavye
# kasma/kayma sorunlarinin gercek kok nedeni buydu. Detay icin hook.py'a bak.
p4a.hook = %(source.dir)s/hook.py

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
#android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
