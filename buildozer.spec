[app]
title = Aydinlatma Olcum
package.name = aydinlatmaolcum
package.domain = org.kerem

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = hostpython3==3.11.9,python3==3.11.9,kivy==2.3.1,openpyxl,fpdf2,fonttools,et_xmlfile

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
