"""
python-for-android'in build.py dosyasindaki bilinen hatayi duzeltir.
Hata: run_pymodules_install adiminda 'pip install -U pip' calistirilirken,
      bozuk/yarim kalmis bir sanal ortam (venv) varsa ImportError olusuyor.
Resmi duzeltme (kivy/python-for-android PR #3360) su iki degisikligi yapar:
  1) venv olusturulurken --clear bayragi eklenir (eski/bozuk klasor temizlenir)
  2) 'pip install -U pip' adimi tamamen kaldirilir (gereksiz ve riskli)

Bu script, o duzeltmeyi PIP ILE KURULMUS olan python-for-android paketine
dogrudan uygular - hangi surumden geldigi onemli degil, garantili calisir.
"""
import re
import os
import pythonforandroid

path = os.path.join(os.path.dirname(pythonforandroid.__file__), "build.py")
print(f"Yamalanacak dosya: {path}")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

original_len = len(content)

# 1) venv olusturma satirina --clear ekle
before = content
content = content.replace(
    "'-m', 'venv', 'venv'",
    "'-m', 'venv', '--clear', 'venv'",
)
if content != before:
    print("OK: --clear bayragi eklendi.")
else:
    print("UYARI: --clear icin hedef satir bulunamadi (zaten yamali olabilir).")

# 2) 'Upgrade pip to latest version' blogunu (info + shprint cagrisi) kaldir
pattern = re.compile(
    r"info\('Upgrade pip to latest version'\)\s*\n"
    r"\s*shprint\(sh\.bash,\s*'-c',\s*\(\s*\n"
    r"\s*\"source venv/bin/activate && pip install -U pip\"\s*\n"
    r"\s*\),\s*_env=copy\.copy\(base_env\)\)\s*\n",
    re.MULTILINE,
)
new_content, n = pattern.subn("", content)
if n > 0:
    print(f"OK: 'pip install -U pip' adimi kaldirildi ({n} yer).")
else:
    print("UYARI: pip-upgrade blogu bulunamadi (zaten yamali olabilir).")
content = new_content

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Bitti. Dosya boyutu: {original_len} -> {len(content)} bayt")
