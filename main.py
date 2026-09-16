# Aydinlatma Olcum Paneli - v6
# Olcum ekrani: Konsept 2 (kartli ust bolum) + Konsept 4 (kompakt tablo) birlesimi.
# Standart secimi bu ekrandan kaldirildi -> ust rozete tasindi, dokunulunca
# Standartlar sekmesine gecer (secim islemi bir sonraki adimda o sekmede yapilacak).

import random
import json
import os
import math
import socket
import threading
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter
from kivy.graphics.texture import Texture
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse, Triangle
from kivy.metrics import sp, dp


def lighten(color, amount=0.12):
    r, g, b, a = color
    return (min(r + amount, 1), min(g + amount, 1), min(b + amount, 1), a)

# ---------------------------------------------------------
# RENK PALETI
# ---------------------------------------------------------
BG = (0.06, 0.06, 0.07, 1)
CARD = (0.10, 0.10, 0.12, 1)
CARD_LIGHT = (0.19, 0.19, 0.23, 1)
BORDER = (0.26, 0.26, 0.30, 1)
TEXT = (0.91, 0.91, 0.92, 1)
TEXT_MUTED = (0.54, 0.54, 0.58, 1)
ACCENT = (0.35, 0.61, 0.85, 1)
SUCCESS = (0.18, 0.55, 0.34, 1)
SUCCESS_TINT = (0.09, 0.20, 0.12, 1)
DANGER = (0.75, 0.25, 0.28, 1)
GREEN_TXT = (0.36, 0.79, 0.54, 1)
RED_TXT = (0.88, 0.48, 0.48, 1)

# --- YENI: Gunduz/Gece Modu tema sistemi ---
DARK_PALETTE = {
    "BG": (0.06, 0.06, 0.07, 1), "CARD": (0.10, 0.10, 0.12, 1),
    "CARD_LIGHT": (0.19, 0.19, 0.23, 1), "BORDER": (0.26, 0.26, 0.30, 1),
    "TEXT": (0.91, 0.91, 0.92, 1), "TEXT_MUTED": (0.54, 0.54, 0.58, 1),
    "ACCENT": (0.35, 0.61, 0.85, 1), "SUCCESS": (0.18, 0.55, 0.34, 1),
    "SUCCESS_TINT": (0.09, 0.20, 0.12, 1), "DANGER": (0.75, 0.25, 0.28, 1),
    "GREEN_TXT": (0.36, 0.79, 0.54, 1), "RED_TXT": (0.88, 0.48, 0.48, 1),
    "NAV_BG": (0.09, 0.09, 0.10, 1),
    "ROW_A": (0.082, 0.082, 0.094, 1), "ROW_B": (0.102, 0.102, 0.122, 1),
    "HEADER_BG": (0.13, 0.13, 0.15, 1), "DANGER_TINT": (0.22, 0.09, 0.10, 1),
}
LIGHT_PALETTE = {
    "BG": (0.95, 0.95, 0.96, 1), "CARD": (0.99, 0.99, 1.00, 1),
    "CARD_LIGHT": (0.89, 0.89, 0.92, 1), "BORDER": (0.78, 0.78, 0.82, 1),
    "TEXT": (0.10, 0.10, 0.12, 1), "TEXT_MUTED": (0.40, 0.40, 0.45, 1),
    "ACCENT": (0.14, 0.40, 0.70, 1), "SUCCESS": (0.14, 0.48, 0.30, 1),
    "SUCCESS_TINT": (0.85, 0.94, 0.87, 1), "DANGER": (0.70, 0.16, 0.18, 1),
    "GREEN_TXT": (0.12, 0.50, 0.28, 1), "RED_TXT": (0.68, 0.16, 0.16, 1),
    "NAV_BG": (0.91, 0.91, 0.94, 1),
    "ROW_A": (0.97, 0.97, 0.99, 1), "ROW_B": (0.93, 0.93, 0.96, 1),
    "HEADER_BG": (0.86, 0.86, 0.90, 1), "DANGER_TINT": (0.96, 0.87, 0.87, 1),
}
CURRENT_THEME = "light"
NAV_BG = DARK_PALETTE["NAV_BG"]


def apply_palette(name):
    """Secilen temanin renklerini modul-seviyesi sabitlere uygular.
    Bu, widget agacini yeniden insa etmeden ONCE cagrilmali - Kivy widget'lari
    renkleri OLUSTURULDUKLARI anda okuyup canvas'a gomuyor."""
    global CURRENT_THEME, STATUS_BG
    palette = LIGHT_PALETTE if name == "light" else DARK_PALETTE
    globals().update(palette)
    STATUS_BG = LIGHT_STATUS_BG if name == "light" else DARK_STATUS_BG
    CURRENT_THEME = name


def load_saved_theme():
    """Uygulama acilirken, widget'lar insa edilmeden ONCE hangi temanin
    kayitli oldugunu okur (dosya yoksa/bozuksa varsayilan: gunduz modu)."""
    try:
        app = App.get_running_app()
        path = os.path.join(app.user_data_dir, "aydinlatma_session.json")
        if not os.path.exists(path):
            return "light"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("theme", "light")
    except Exception:
        return "light"


ROW_A = DARK_PALETTE["ROW_A"]
ROW_B = DARK_PALETTE["ROW_B"]
HEADER_BG = DARK_PALETTE["HEADER_BG"]
DANGER_TINT = DARK_PALETTE["DANGER_TINT"]

# --- FIBA (basketbol) aydinlatma standardi - FIFA/UEFA'dan YAPISAL olarak farkli:
# iki ic ice bolge (PPA/TPA), MAUR yok, EH bir ARALIK, EV icin 4-yon dengesi var.
# Kaynak: FIBA Official Basketball Rules 2024, Bolum 12, Tablo 5-6.
FIBA_STANDARDS = {
    "PPA": {  # Ana Oyun Alani - 19m x 32m (sahanin kendisi)
        "ec_avg": 2000, "ec_u1": 0.7, "ec_u2": 0.8,
        "ev_avg": 1700, "ev_u1": 0.7, "ev_u2": 0.8, "ev_dir_ratio": 0.6,
        "eh_avg_min": 1500, "eh_avg_max": 3000, "eh_u1": 0.7, "eh_u2": 0.8,
    },
    "TPA": {  # Toplam Oyun Alani - 22m x 35m (saha + 1.5m cevre serit)
        "ec_avg": 2000, "ec_u1": 0.6, "ec_u2": 0.7,
        "ev_avg": 1700, "ev_u1": 0.6, "ev_u2": 0.7, "ev_dir_ratio": 0.6,
        "eh_avg_min": 1500, "eh_avg_max": 3000, "eh_u1": 0.6, "eh_u2": 0.7,
    },
    "light_source": {
        "flicker_max_pct": 1.0, "cri_min": 80,
        "cct_min": 4000, "cct_max": 6000, "cct_tolerance": 500,
    },
}

STANDARDS = {
    "FIFA": {
        "Standard A": {
            "Eh_min": 1500, "Eh_avg": 2500, "u1h": 0.50, "u2h": 0.70,
            "Ev_min": 1000, "Ev_avg": 1500, "u1v": 0.50, "u2v": 0.60,
            "mcm": "Isik surekliligine kesinti verilemez",
            "ff": "ort < 1%   maks < 1%",
            "maur": "> 0.60   (en fazla 10 hata)",
            "maur_ratio": 0.6, "maur_max_fail": 10,
            "cct": "5000-6200K", "ra": 80, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
        },
        "Standard B": {
            "Eh_min": 1200, "Eh_avg": 2000, "u1h": 0.50, "u2h": 0.70,
            "Ev_min": 650, "Ev_avg": 1000, "u1v": 0.40, "u2v": 0.50,
            "mcm": "Eh ort > 2000 lx, 15 dakika icinde",
            "ff": "ort < 12%   maks < 15%",
            "maur": "> 0.60   (en fazla 30 hata)",
            "maur_ratio": 0.6, "maur_max_fail": 30,
            "cct": "5000-6200K", "ra": 80, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
        },
        "Standard C": {
            "Eh_min": 800, "Eh_avg": 1250, "u1h": 0.40, "u2h": 0.60,
            "Ev_min": 350, "Ev_avg": 700, "u1v": 0.35, "u2v": 0.45,
            "mcm": "Eh ort > 1000 lx (3 dk) / > 1250 lx (15 dk)",
            "ff": "ort < 20%   maks < 30%",
            "maur": "> 0.50   (en fazla 30 hata)",
            "maur_ratio": 0.5, "maur_max_fail": 30,
            "cct": "5000-6200K", "ra": 80, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
        },
        "Standard D": {
            "Eh_min": None, "Eh_avg": 1000, "u1h": 0.40, "u2h": 0.60,
            "Ev_min": 250, "Ev_avg": 400, "u1v": 0.35, "u2v": 0.45,
            "mcm": "FIFA tarafindan duruma gore belirlenir",
            "ff": "belirtilmemis",
            "maur": "belirtilmemis",
            "maur_ratio": None, "maur_max_fail": None,
            "cct": "4500-6200K", "ra": 70, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
        },
        # --- Grade 1/2/3: FIFA ANTRENMAN SAHASI standartlari - MAC sahasindan
        # FARKLI (yon-bazli, asimetrik gereksinimler). Kaynak: FIFA Lighting
        # Guide, Bolum 1.36-1.39, Tablo (Grade 3/2/1). ---
        "Grade 1": {
            # FIFA Dunya Kupasi Antrenman Sahasi - 96 nokta izgara (12x8)
            "Eh_avg": 750, "u1h": 0.40, "u2h": 0.60,
            "Ev0_min": 350, "Ev0_avg": 500, "Ev0_u1": 0.30, "Ev0_u2": 0.40,
            "Ev90_min": 350, "Ev90_avg": 500, "Ev90_u1": 0.30, "Ev90_u2": 0.40,
            "Ev180_min": 350, "Ev180_avg": 500, "Ev180_u1": 0.30, "Ev180_u2": 0.40,
            "Ev270_min": 350, "Ev270_avg": 500, "Ev270_u1": 0.30, "Ev270_u2": 0.40,
            "mcm": "Gecerli degil (antrenman sahasi)",
            "ff": "< %1",
            "maur": "belirtilmemis (MAUR bu standartta yok)",
            "maur_ratio": None, "maur_max_fail": None,
            "cct": "5000-6200K", "ra": 80, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
            "reference_grid": "96 nokta (12 x 8)",
            "auto_grid": (12, 8),
        },
        "Grade 2": {
            # FIFA Mac Pratigi Antrenman Sahasi - 40 nokta izgara (8x5)
            "Eh_avg": 500, "u1h": 0.40, "u2h": 0.60,
            "Ev90_min": 275, "Ev90_avg": 400, "Ev90_u1": 0.30, "Ev90_u2": 0.40,
            "Ev270_min": 275, "Ev270_avg": 400, "Ev270_u1": 0.30, "Ev270_u2": 0.40,
            "mcm": "Gecerli degil (antrenman sahasi)",
            "ff": "belirtilmemis",
            "maur": "belirtilmemis (MAUR bu standartta yok)",
            "maur_ratio": None, "maur_max_fail": None,
            "cct": "5000-6200K", "ra": 70, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
            "reference_grid": "40 nokta (8 x 5)",
            "auto_grid": (8, 5),
        },
        "Grade 3": {
            # FIFA Standart Antrenman Sahasi - 40 nokta izgara (8x5)
            "Eh_avg": 300, "u1h": 0.40, "u2h": 0.60,
            "Ev90_min": 150, "Ev90_avg": 200, "Ev90_u1": 0.30, "Ev90_u2": 0.40,
            "Ev270_min": 150, "Ev270_avg": 200, "Ev270_u1": 0.30, "Ev270_u2": 0.40,
            "mcm": "Gecerli degil (antrenman sahasi)",
            "ff": "belirtilmemis",
            "maur": "belirtilmemis (MAUR bu standartta yok)",
            "maur_ratio": None, "maur_max_fail": None,
            "cct": "4200-6200K", "ra": 70, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
            "reference_grid": "40 nokta (8 x 5)",
            "auto_grid": (8, 5),
        },
    },
    "UEFA": {
        "Elite Level A": {
            "Eh_min": None, "Eh_avg": 2000, "u1h": 0.50, "u2h": 0.70,
            "Ev_min": 1000, "Ev_avg": 1500, "u1v": 0.50, "u2v": 0.60,
            "mcm": "LED: kesinti yok. HID: FPSL A'ya bakiniz",
            "ff": "ort < 3%   maks < 3%",
            "maur": "> 0.60   (en fazla 10 hata)",
            "maur_ratio": 0.6, "maur_max_fail": 10,
            "cct": "5000-6200K", "ra": 80, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
        },
        "Level A": {
            "Eh_min": None, "Eh_avg": 1500, "u1h": 0.50, "u2h": 0.70,
            "Ev_min": 700, "Ev_avg": 1250, "u1v": 0.40, "u2v": 0.50,
            "mcm": "Guc kesintisinden sonra 15 dakika icinde",
            "ff": "ort < 12%   maks < 15%",
            "maur": "> 0.60   (en fazla 20 hata)",
            "maur_ratio": 0.6, "maur_max_fail": 20,
            "cct": "5000-6200K", "ra": 80, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
        },
        "Level B": {
            "Eh_min": None, "Eh_avg": 1400, "u1h": 0.50, "u2h": 0.70,
            "Ev_min": 600, "Ev_avg": 1000, "u1v": 0.40, "u2v": 0.50,
            "mcm": "Guc kesintisinden sonra 15 dakika icinde",
            "ff": "ort < 12%   maks < 15%",
            "maur": "> 0.60   (en fazla 30 hata)",
            "maur_ratio": 0.6, "maur_max_fail": 30,
            "cct": "5000-6200K", "ra": 80, "rg": "< 50",
            "mf": "0.90 (LED)   0.80 (HID)",
        },
        "Level C": {
            "Eh_min": None, "Eh_avg": 1200, "u1h": 0.40, "u2h": 0.60,
            "Ev_min": 350, "Ev_avg": 700, "u1v": 0.35, "u2v": 0.45,
            "mcm": "Guc kesintisinden sonra 15 dakika icinde",
            "ff": "ort < 20%   maks < 30%",
            "maur": "> 0.50   (en fazla 30 hata)",
            "maur_ratio": 0.5, "maur_max_fail": 30,
            "cct": "4200-6200K", "ra": 70, "rg": "< 50",
            "mf": "0.90 (LED)   0.70 (HID)",
        },
        "Level D": {
            "Eh_min": None, "Eh_avg": 800, "u1h": 0.40, "u2h": 0.60,
            "Ev_min": 200, "Ev_avg": 350, "u1v": None, "u2v": None,
            "mcm": "belirtilmemis",
            "ff": "belirtilmemis",
            "maur": "belirtilmemis",
            "maur_ratio": None, "maur_max_fail": None,
            "cct": "4200-6200K", "ra": 65, "rg": "< 50",
            "mf": "0.90 (LED)   0.70 (HID)",
        },
    },
}

PROBES = [("Eh", "Eh"), ("Ev0", "Ev"), ("Ev90", "Ev"), ("Ev180", "Ev"), ("Ev270", "Ev")]

# --- Sabit olcum cihazi bilgileri (gercek donanimla eslesiyor - degismez) ---
METER_MODEL = "Konica Minolta T-10A"
METER_SERIAL = "20022401"
PROBE_SERIALS = {
    "Eh":   "30023761",  # Alici Kafa No.0
    "Ev0":  "30023200",  # Alici Kafa No.1
    "Ev90": "30023785",  # Alici Kafa No.2
    "Ev180": "30023788",  # Alici Kafa No.3
    "Ev270": "30023165",  # Alici Kafa No.4
}

# --- Sabit kurulus/denetleyen bilgileri (degismez - her seferinde girilmeye gerek yok) ---
ORG_NAME = "ŞAH ELEKTRİK İNŞAAT ÇELİK TAAH. SAN. VE TİC. A.Ş."
ORG_ADDRESS = "Soğanlık Yeni Mah. Balıkesir Cad. Uprise Elite Residence No:6/306 Kartal / İstanbul"
ORG_PHONE_EMAIL = "0216 459 86 26 - kerem.akgun@sahgroup.net"
INSPECTOR_NAME = "Kerem AKGÜN"


# ---------------------------------------------------------
# ORTAK GORSEL BILESENLER
# ---------------------------------------------------------
class PopupContent(BoxLayout):
    """Popup icerigi icin KENDI cizdigimiz temaya-uyumlu arka plan.
    Kivy'nin yerlesik Popup.background_color'i guvenilir calismadigi
    icin (ic gorsel katmanlari bizim renklerimizi gormezden gelebiliyor),
    Card ile ayni yontemi (Color + RoundedRectangle) kullaniyoruz."""
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        with self.canvas.before:
            self.bg_instr = Color(*CARD)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Card(BoxLayout):
    def __init__(self, bg_color=CARD, radius=14, border_color="__default__", **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        if border_color == "__default__":
            border_color = BORDER  # belirtilmemisse ince, sonuk bir kenarlik kullan
        with self.canvas.before:
            self.bg_instr = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
            if border_color:
                Color(*border_color)
                self.border_line = Line(width=1.1)
            else:
                self.border_line = None
        self.bind(pos=self._update, size=self._update)

    def _update(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if self.border_line:
            self.border_line.rounded_rectangle = (
                self.x, self.y, self.width, self.height, self.radius)


class FlatButton(Button):
    def __init__(self, bg_color=CARD_LIGHT, radius=12, **kwargs):
        kwargs.setdefault('color', text_color_for_bg(bg_color))
        super().__init__(background_normal='', background_down='',
                          background_color=(0, 0, 0, 0), **kwargs)
        self.radius = radius
        self._base_color = bg_color
        with self.canvas.before:
            self.bg_instr = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._update, size=self._update, state=self._on_state)

    def _update(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _on_state(self, instance, value):
        self.bg_instr.rgba = lighten(self._base_color, 0.14) if value == 'down' else self._base_color


class TappableCard(Card):
    """Dokunulabilir kart - grid ayari ve standart rozeti icin."""
    def __init__(self, on_tap=None, **kwargs):
        super().__init__(**kwargs)
        self.on_tap = on_tap

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            original = self.bg_instr.rgba[:]
            self.bg_instr.rgba = lighten(original, 0.10)
            Clock.schedule_once(lambda dt: setattr(self.bg_instr, 'rgba', original), 0.15)
            if self.on_tap:
                self.on_tap()
            return True
        return super().on_touch_down(touch)


class ThemedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(
            background_normal='', background_active='', background_color=(0, 0, 0, 0),
            foreground_color=TEXT, cursor_color=ACCENT, hint_text_color=TEXT_MUTED,
            padding=[dp(14), dp(14), dp(14), dp(14)], **kwargs)


class TabIcon(Widget):
    def __init__(self, kind, **kwargs):
        super().__init__(**kwargs)
        self.kind = kind
        self.active = False
        self.size_hint = (None, None)
        self.size = (dp(26), dp(26))
        with self.canvas:
            self.color_instr = Color(*TEXT_MUTED)
        self.bind(pos=self._redraw, size=self._redraw)

    def set_active(self, active):
        self.active = active
        self.color_instr.rgba = ACCENT if active else TEXT_MUTED

    def _redraw(self, *a):
        self.canvas.clear()
        with self.canvas:
            self.color_instr = Color(*(ACCENT if self.active else TEXT_MUTED))
            x, y, w, h = self.x, self.y, self.width, self.height
            if self.kind == "measure":
                Line(circle=(x + w / 2, y + h * 0.62, w * 0.32), width=1.6)
                for dx, dy in [(-0.28, -0.28), (0.28, -0.28), (0, -0.42)]:
                    Line(points=[x + w / 2, y + h * 0.34,
                                 x + w / 2 + dx * w, y + h * 0.34 + dy * h], width=1.6)
            elif self.kind == "standards":
                Line(rounded_rectangle=(x + w * 0.12, y + h * 0.08, w * 0.76, h * 0.84, 4), width=1.6)
                for frac in [0.65, 0.45, 0.25]:
                    Line(points=[x + w * 0.28, y + h * frac, x + w * 0.72, y + h * frac], width=1.4)
            elif self.kind == "result":
                Line(points=[x + w * 0.10, y + h * 0.15, x + w * 0.90, y + h * 0.15], width=1.4)
                bar_w = w * 0.13
                for bx, bh in zip([0.22, 0.42, 0.62, 0.82], [0.35, 0.65, 0.50, 0.80]):
                    Line(rounded_rectangle=(x + w * bx - bar_w / 2, y + h * 0.15,
                                             bar_w, h * bh, 2), width=1.6)
            elif self.kind == "report":
                Line(rounded_rectangle=(x + w * 0.18, y + h * 0.06, w * 0.64, h * 0.88, 3), width=1.6)
                for frac in [0.68, 0.52, 0.36]:
                    Line(points=[x + w * 0.3, y + h * frac, x + w * 0.7, y + h * frac], width=1.3)
            elif self.kind == "settings":
                cx, cy = x + w / 2, y + h / 2
                Line(circle=(cx, cy, w * 0.20), width=1.6)
                Line(circle=(cx, cy, w * 0.07), width=1.6)
                for i in range(8):
                    ang = math.radians(i * 45)
                    inner, outer = w * 0.30, w * 0.42
                    Line(points=[cx + inner * math.cos(ang), cy + inner * math.sin(ang),
                                 cx + outer * math.cos(ang), cy + outer * math.sin(ang)], width=1.6)


class NavButton(BoxLayout):
    def __init__(self, kind, label, on_press, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.on_press_cb = on_press
        with self.canvas.before:
            self.bg_instr = Color(*CARD_LIGHT)
            self.bg_instr.a = 0.0  # baslangicta aktif degil - gorunmez
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.icon = TabIcon(kind)
        icon_wrap = BoxLayout(size_hint_y=0.6)
        icon_wrap.add_widget(Widget())
        icon_wrap.add_widget(self.icon)
        icon_wrap.add_widget(Widget())
        self.add_widget(icon_wrap)
        self.label = Label(text=label, font_size=sp(11.5), size_hint_y=0.4, color=TEXT_MUTED)
        self.add_widget(self.label)

    def _update_bg(self, *a):
        inset_x, inset_y = dp(4), dp(4)
        self.bg_rect.pos = (self.x + inset_x, self.y + inset_y)
        self.bg_rect.size = (self.width - 2 * inset_x, self.height - 2 * inset_y)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.on_press_cb()
            return True
        return super().on_touch_down(touch)

    def set_active(self, active):
        self.icon.set_active(active)
        self.label.color = ACCENT if active else TEXT_MUTED
        self.bg_instr.a = 1.0 if active else 0.0


def fetch_pi_data(ip, port, timeout=2.5):
    """Pi'ye baglanip guncel olcum verisini okur.
    Donen: (durum, veri) - durum: 'connected' | 'device_silent' | 'disconnected'"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, int(port)))
        s.send(b"GET")
        raw = s.recv(1024)
        s.close()
        parsed = json.loads(raw.decode())
        if all(v is None for v in parsed.values()):
            return "device_silent", parsed
        return "connected", parsed
    except Exception:
        return "disconnected", None


STATUS_COLORS = {
    "connected": (0.25, 0.75, 0.40, 1),        # yesil
    "device_silent": (0.90, 0.60, 0.15, 1),     # turuncu
    "disconnected": (0.80, 0.25, 0.25, 1),      # kirmizi
    "checking": (0.80, 0.75, 0.20, 1),          # sari
}
STATUS_LABELS = {
    "connected": "Bagli",
    "device_silent": "Pi bagli, cihaz sessiz",
    "disconnected": "Bagli degil",
    "checking": "Kontrol ediliyor...",
}


class TextSpinner:
    """Bir butonun/etiketin metnine basit, donen bir karakter ekleyerek
    'islem suruyor' hissi verir - agir grafik/animasyon gerektirmeden."""
    FRAMES = ["|", "/", "-", "\\"]

    def __init__(self, widget, base_text):
        self.widget = widget
        self.base_text = base_text
        self.idx = 0
        self.widget.text = f"{self.FRAMES[0]} {base_text}"
        self.event = Clock.schedule_interval(self._tick, 0.12)

    def _tick(self, dt):
        self.idx = (self.idx + 1) % len(self.FRAMES)
        self.widget.text = f"{self.FRAMES[self.idx]} {self.base_text}"

    def stop(self, final_text=None):
        if self.event:
            self.event.cancel()
            self.event = None
        if final_text is not None:
            self.widget.text = final_text


class StatusDot(Widget):
    """Baglanti durumunu gosteren kucuk renkli daire."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(12), dp(12))
        with self.canvas:
            self.color_instr = Color(*STATUS_COLORS["disconnected"])
            self.circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *a):
        self.circle.pos = self.pos
        self.circle.size = self.size

    def set_status(self, status):
        self.color_instr.rgba = STATUS_COLORS.get(status, STATUS_COLORS["disconnected"])


DARK_STATUS_BG = {
    "connected": (0.055, 0.11, 0.075, 1),
    "device_silent": (0.12, 0.09, 0.045, 1),
    "disconnected": (0.13, 0.065, 0.07, 1),
    "checking": (0.10, 0.10, 0.06, 1),
}
LIGHT_STATUS_BG = {
    "connected": (0.85, 0.95, 0.87, 1),
    "device_silent": (0.98, 0.92, 0.80, 1),
    "disconnected": (0.97, 0.87, 0.87, 1),
    "checking": (0.97, 0.96, 0.80, 1),
}
STATUS_BG = DARK_STATUS_BG


class ConnectionStrip(BoxLayout):
    """Ekranin en ustunde ince bir bilgi seridi - sol kenarda renkli bir cizgi
    ve hafif tonlanmis arka planla baglanti durumunu her an gorunur kilar."""
    def __init__(self, on_tap=None, **kwargs):
        super().__init__(size_hint_y=None, height=dp(38), **kwargs)
        self.on_tap = on_tap
        with self.canvas.before:
            self.bg_instr = Color(*STATUS_BG["disconnected"])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            self.border_instr = Color(*STATUS_COLORS["disconnected"])
            self.border_rect = Rectangle(pos=self.pos, size=(dp(3), self.height))
        self.bind(pos=self._update, size=self._update)

        content = BoxLayout(padding=[dp(14), 0, dp(10), 0], spacing=dp(8))
        self.dot = StatusDot()
        self.dot.pos_hint = {"center_y": 0.5}
        dot_wrap = BoxLayout(size_hint_x=None, width=dp(16))
        dot_wrap.add_widget(self.dot)
        content.add_widget(dot_wrap)
        self.label = Label(text=STATUS_LABELS["disconnected"], font_size=sp(12.5), color=TEXT_MUTED,
                            halign="left", valign="middle", text_size=(dp(230), dp(38)))
        content.add_widget(self.label)
        chevron = Label(text=">", font_size=sp(12), color=TEXT_MUTED, size_hint_x=None, width=dp(18),
                         valign="middle", text_size=(dp(18), dp(38)))
        content.add_widget(chevron)
        self.add_widget(content)

    def _update(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = self.pos
        self.border_rect.size = (dp(3), self.height)

    def set_status(self, status):
        self.dot.set_status(status)
        base_text = STATUS_LABELS.get(status, status)
        if status != "checking":
            time_str = datetime.now().strftime("%H:%M")
            self.label.text = f"{base_text}  ·  {time_str}"
        else:
            self.label.text = base_text
        self.bg_instr.rgba = STATUS_BG.get(status, STATUS_BG["disconnected"])
        self.border_instr.rgba = STATUS_COLORS.get(status, STATUS_COLORS["disconnected"])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.on_tap:
            self.on_tap()
            return True
        return super().on_touch_down(touch)



def snake_sequence(rows, cols):
    seq = []
    for r in range(rows):
        col_range = range(cols) if r % 2 == 0 else range(cols - 1, -1, -1)
        for c in col_range:
            seq.append((r, c))
    return seq


def build_measurement_sequence(satir_n, sutun_n):
    """Olcum sirasi: Grid No 1 sol-ustte, once SAGA dogru (satir boyunca) ilerler,
    satir bitince bir SUTUN asagi iner, yilan mantigiyla devam eder.
    (r = satir indeksi, c = sutun indeksi)"""
    raw = snake_sequence(sutun_n, satir_n)  # disli: sutun YAVAS/dis donguy, satir HIZLI/ic dongu
    return [(r, c) for (c, r) in raw]


# ---------------------------------------------------------
# TABLO SATIRI (Konsept 4 stili - renkli metin, sirali zemin)
# ---------------------------------------------------------
COL_WEIGHTS = [0.15, 0.17, 0.17, 0.17, 0.17, 0.17]
COL_HEADERS = ["Grid No", "Eh", "Ev0", "Ev90", "Ev180", "Ev270"]


class TableRow(BoxLayout):
    def __init__(self, bg_color, point_index=None, on_tap=None, **kwargs):
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(34))
        super().__init__(**kwargs)
        self.point_index = point_index
        self.on_tap = on_tap
        self.cell_labels = []
        with self.canvas.before:
            self.color_instr = Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._u, size=self._u)

    def _u(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.point_index is not None and self.collide_point(*touch.pos) and self.on_tap:
            original = self.color_instr.rgba[:]
            self.color_instr.rgba = lighten(original, 0.10)
            Clock.schedule_once(lambda dt: setattr(self.color_instr, 'rgba', original), 0.15)
            self.on_tap(self.point_index)
            return True
        return super().on_touch_down(touch)

    def add_cell(self, text, color=TEXT, bold=False):
        w = COL_WEIGHTS[len(self.cell_labels)] if len(self.cell_labels) < len(COL_WEIGHTS) else 0.15
        lbl = Label(text=text, font_size=sp(11.5), color=color, bold=bold,
                     size_hint_x=w)
        self.add_widget(lbl)
        self.cell_labels.append(lbl)

    def update_cell(self, position, text, color=None):
        """Var olan bir hucreyi yeniden olusturmadan, yerinde gunceller (O(1))."""
        lbl = self.cell_labels[position]
        lbl.text = text
        if color is not None:
            lbl.color = color


# ---------------------------------------------------------
# EKRAN 1: OLCUM VERISI (Konsept 2 + Konsept 4 birlesimi)
# ---------------------------------------------------------
class MeasureScreen(Screen):
    def __init__(self, on_open_standards=None, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BG)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.on_open_standards = on_open_standards
        self.sequence = []
        self.current_index = 0
        self.frontier_index = 0
        self.measurements = {}  # point_index -> {'r','c','values'}
        self.row_widgets = {}   # point_index -> TableRow widget (O(1) guncelleme icin)
        self.rows_count_val = 6
        self.cols_count_val = 10
        self.org = "FIFA"
        self.level = "Standard B"

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))

        # --- Baglanti durumu (dokununca IP/Port ayar penceresi acilir) ---
        # --- Standart rozeti (dokununca Standartlar sekmesine gecer) ---
        self.badge = TappableCard(bg_color=CARD, radius=12, size_hint_y=None, height=dp(46),
                                   padding=[dp(14), 0, dp(14), 0], on_tap=self._open_standards)
        badge_row = BoxLayout()
        self.badge_label = Label(text=f"{self.org} · {self.level}", font_size=sp(13.5), color=TEXT_MUTED)
        badge_row.add_widget(self.badge_label)
        chevron = Label(text=">", font_size=sp(14), color=TEXT_MUTED, size_hint_x=None, width=dp(20))
        badge_row.add_widget(chevron)
        self.badge.add_widget(badge_row)
        root.add_widget(self.badge)

        # --- Izgara karti (dokununca duzenleme penceresi acilir) ---
        self.grid_card = TappableCard(bg_color=CARD, radius=14, size_hint_y=None, height=dp(58),
                                       padding=[dp(16), 0, dp(16), 0], on_tap=self._open_grid_editor)
        grid_row = BoxLayout()
        grid_row.add_widget(Label(text="Izgara", font_size=sp(14.5), color=TEXT, size_hint_x=0.5,
                                   halign="left", text_size=(dp(120), None)))
        self.grid_value_label = Label(text=f"{self.rows_count_val} x {self.cols_count_val}",
                                       font_size=sp(15.5), bold=True, color=TEXT)
        grid_row.add_widget(self.grid_value_label)
        self.grid_card.add_widget(grid_row)
        root.add_widget(self.grid_card)

        # --- Aktif nokta karti (yesil vurgulu) ---
        self.point_card = Card(bg_color=SUCCESS_TINT, radius=14, border_color=SUCCESS,
                                size_hint_y=None, padding=[dp(16), dp(10), dp(16), dp(10)])
        point_row = BoxLayout(size_hint_y=None, height=dp(38))
        point_label_left = Label(text="Aktif nokta", font_size=sp(13), color=SUCCESS,
                                  size_hint_x=0.4, halign="left", valign="middle")
        point_row.add_widget(point_label_left)
        self.active_point_label = Label(text="Izgarayi baslatin", font_size=sp(14), bold=True,
                                         color=TEXT, size_hint_x=0.6, halign="right", valign="middle",
                                         shorten=True, shorten_from="left")
        point_row.add_widget(self.active_point_label)
        for lbl in (point_label_left, self.active_point_label):
            lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.point_card.add_widget(point_row)
        self.point_card.bind(minimum_height=self.point_card.setter("height"))
        root.add_widget(self.point_card)

        # --- OLC butonu ---
        self.measure_btn = FlatButton(text="OLCUM AL", bg_color=SUCCESS, radius=14,
                                       font_size=sp(18), bold=True,
                                       size_hint_y=None, height=dp(58))
        self.measure_btn.bind(on_release=self.take_measurement)
        root.add_widget(self.measure_btn)

        # --- FIBA: 1. tur bitince 2. turu (yatay) baslatma butonu ---
        self.fiba_r2_btn = FlatButton(text="2. Turu Baslat (Yatay Olcum)", bg_color=ACCENT,
                                       radius=14, font_size=sp(14.5), bold=True,
                                       size_hint_y=None, height=0, opacity=0, disabled=True)
        self.fiba_r2_btn.bind(on_release=self._start_fiba_round2)
        root.add_widget(self.fiba_r2_btn)

        # --- Tablo (Konsept 4 stili) ---
        table_card = Card(bg_color=CARD, radius=14, orientation="vertical", padding=0)
        self.header_row = TableRow(HEADER_BG)
        self._rebuild_table_header()
        table_card.add_widget(self.header_row)

        scroll = ScrollView(size_hint=(1, 1))
        self.table_body = BoxLayout(orientation="vertical", size_hint_y=None, spacing=0)
        self.table_body.bind(minimum_height=self.table_body.setter("height"))
        scroll.add_widget(self.table_body)
        table_card.add_widget(scroll)
        root.add_widget(table_card)

        outer = BoxLayout(orientation="vertical")
        self.conn_strip = ConnectionStrip(on_tap=self._open_connection_settings)
        outer.add_widget(self.conn_strip)
        outer.add_widget(root)
        self.add_widget(outer)
        self._recompute_sequence(start=False)
        self.project_info = {"name": "", "location": "",
                              "date": datetime.now().strftime("%d.%m.%Y"), "prepared_by": ""}
        self.fifa_info = {
            "lum1_manufacturer": "", "lum1_model": "",
            "cal_date": "",
            "colour_meter": "", "colour_meter_serial": "", "colour_meter_cal_date": "",
            "pitch_width": "", "pitch_length": "",
            "flicker_avg": "", "flicker_max": "",
            "colour_temp_tc": "", "colour_rendering_ra": "", "glare_rating_rg": "",
            # --- Asagidakiler onceden SABIT (koddan degistirilmesi gereken) degerlerdi.
            # Artik varsayilan olarak ayni degerlerle basliyor ama Rapor > Ek Rapor
            # Bilgilerini Duzenle'den GUNCELLENEBILIR - ileride adres/telefon/
            # denetleyen/prob degisirse koda dokunmaya gerek kalmaz.
            "meter_model": METER_MODEL, "meter_serial": METER_SERIAL,
            "probe_serial_eh": PROBE_SERIALS["Eh"], "probe_serial_ev0": PROBE_SERIALS["Ev0"],
            "probe_serial_ev90": PROBE_SERIALS["Ev90"], "probe_serial_ev180": PROBE_SERIALS["Ev180"],
            "probe_serial_ev270": PROBE_SERIALS["Ev270"],
            "org_name": ORG_NAME, "org_address": ORG_ADDRESS,
            "org_phone_email": ORG_PHONE_EMAIL, "inspector_name": INSPECTOR_NAME,
        }
        self.report_language = "tr"  # "tr" veya "en" - PDF raporunun dili
        self.fiba_ppa_margin = 1  # TPA sinirindan PPA'ya kac "halka" ic - varsayilan 1
        self.ec_values = {}  # idx -> deger: FIBA "EC" (270 probu kameraya cevrilerek, IKINCI Pi olcumu)
        self.fiba_round = 1  # FIBA: 1=dikey+EC turu, 2=yatay (Eh) turu
        self.fiba_step = 1  # FIBA 1. Tur icinde: 1=4 dikey olcum bekleniyor, 2=EC (270->kamera) bekleniyor
        self.fiba_r2_current_index = 0
        self.fiba_r2_frontier_index = 0
        self.pi_ip = "192.168.0.222"
        self.pi_port = 8899
        self.connection_status = "disconnected"
        self._conn_check_gen = 0  # yaris durumunu (eski kontrolun yeniyi ezmesini) onlemek icin
        self._fetch_lock = threading.Lock()  # ayni anda SADECE TEK bir ag istegi olsun diye
        self.load_session()
        Clock.schedule_interval(self._background_connection_check, 30)
        # NOT: acilista ANINDA otomatik kontrol KALDIRILDI - kullanicinin ilk
        # "Baglan" denemesiyle cakisip gereksiz gecikmeye yol aciyordu.

    # --- Kalici kayit (uygulama kapanirsa/coksekirse veri kaybolmasin) ---
    def _update_bg(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _session_path(self):
        try:
            app = App.get_running_app()
            return os.path.join(app.user_data_dir, "aydinlatma_session.json")
        except Exception:
            return None

    def _build_session_dict(self):
        """Tum oturum verisini TEK bir sozluk olarak dondurur - hem otomatik
        kayit (save_session) hem de kullanicinin elle 'Disa Aktar' islemi
        AYNI bu fonksiyonu kullanir, boylece ikisi hep tutarli kalir."""
        return {
            "org": self.org, "level": self.level,
            "rows": self.rows_count_val, "cols": self.cols_count_val,
            "frontier_index": self.frontier_index,
            "measurements": {str(k): v for k, v in self.measurements.items()},
            "project_info": self.project_info,
            "fifa_info": self.fifa_info,
            "report_language": self.report_language,
            "fiba_ppa_margin": self.fiba_ppa_margin,
            "ec_values": {str(k): v for k, v in self.ec_values.items()},
            "fiba_round": self.fiba_round,
            "fiba_step": self.fiba_step,
            "fiba_r2_current_index": self.fiba_r2_current_index,
            "fiba_r2_frontier_index": self.fiba_r2_frontier_index,
            "pi_ip": self.pi_ip,
            "pi_port": self.pi_port,
            "theme": CURRENT_THEME,
            "saved_at": datetime.now().isoformat(),
        }

    def save_session(self):
        path = self._session_path()
        if not path:
            return
        try:
            data = self._build_session_dict()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass  # kayit basarisiz olsa bile uygulama calismaya devam etsin

    def load_session(self):
        path = self._session_path()
        if not path or not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._apply_session_dict(data)
        except Exception:
            pass  # bozuk/eksik kayit dosyasi uygulamayi cokertmesin

    def _apply_session_dict(self, data):
        """Bir oturum sozlugunu (ic otomatik kayittan VEYA kullanicinin
        disaridan yukledigi bir yedek dosyadan) uygulamaya isler."""
        self.org = data.get("org", self.org)
        self.level = data.get("level", self.level)
        self.rows_count_val = data.get("rows", self.rows_count_val)
        self.cols_count_val = data.get("cols", self.cols_count_val)
        self.project_info.update(data.get("project_info", {}))
        self.fifa_info.update(data.get("fifa_info", {}))
        self.report_language = data.get("report_language", self.report_language)
        self.fiba_ppa_margin = data.get("fiba_ppa_margin", self.fiba_ppa_margin)
        raw_ec = data.get("ec_values", {})
        self.ec_values = {int(k): v for k, v in raw_ec.items()} if raw_ec else {}
        self.fiba_round = data.get("fiba_round", 1)
        self.fiba_step = data.get("fiba_step", 1)
        self.fiba_r2_current_index = data.get("fiba_r2_current_index", 0)
        self.fiba_r2_frontier_index = data.get("fiba_r2_frontier_index", 0)
        self.pi_ip = data.get("pi_ip", self.pi_ip)
        self.pi_port = data.get("pi_port", self.pi_port)
        self.grid_value_label.text = f"{self.rows_count_val} x {self.cols_count_val}"
        self.badge_label.text = f"{self.org} \u00b7 {self.level}"
        raw_meas = data.get("measurements", {})
        self.measurements = {int(k): v for k, v in raw_meas.items()} if raw_meas else {}
        self.frontier_index = data.get("frontier_index", 0)
        self.sequence = build_measurement_sequence(self.rows_count_val, self.cols_count_val)
        self.current_index = self.frontier_index
        self.row_widgets = {}
        self._rebuild_table_header()
        self.table_body.clear_widgets()
        for idx in sorted(self.measurements.keys()):
            self._render_row(idx)
        self.measure_btn.disabled = False
        self._update_ec_row_visibility()
        self._update_active_label()

    # --- Baglanti durumu kontrolu ---
    def _background_connection_check(self, dt):
        threading.Thread(target=self._check_connection_once, daemon=True).start()

    def _check_connection_once(self):
        # Baska bir istek (ÖLÇÜM AL, Baglan vb.) zaten suruyorsa bu turu atla -
        # boylece Pi'nin USB portuna AYNI ANDA iki istek gitmez
        if not self._fetch_lock.acquire(blocking=False):
            return
        try:
            self._conn_check_gen += 1
            my_gen = self._conn_check_gen
            status, _ = fetch_pi_data(self.pi_ip, self.pi_port, timeout=3.0)
        finally:
            self._fetch_lock.release()

        def apply(dt):
            if my_gen == self._conn_check_gen:  # daha yeni bir kontrol baslamadiysa uygula
                self._apply_connection_status(status)
        Clock.schedule_once(apply, 0)

    def _apply_connection_status(self, status):
        self.connection_status = status
        self.conn_strip.set_status(status)

    def _open_connection_settings(self):
        content = PopupContent(padding=dp(18), spacing=dp(12))
        _popup_title_lbl = Label(text="Baglanti Ayarlari", font_size=sp(16), bold=True, color=TEXT,
                                 size_hint_y=None, height=dp(30), halign="left")
        _popup_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(_popup_title_lbl)

        row1 = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        row1.add_widget(Label(text="Pi IP", font_size=sp(13), color=TEXT_MUTED, size_hint_x=0.3))
        ip_card = Card(bg_color=CARD_LIGHT, radius=8)
        ip_input = ThemedTextInput(text=self.pi_ip, multiline=False, font_size=sp(14))
        ip_card.add_widget(ip_input)
        row1.add_widget(ip_card)
        content.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        row2.add_widget(Label(text="Port", font_size=sp(13), color=TEXT_MUTED, size_hint_x=0.3))
        port_card = Card(bg_color=CARD_LIGHT, radius=8)
        port_input = ThemedTextInput(text=str(self.pi_port), multiline=False, font_size=sp(14),
                                      input_filter="int")
        port_card.add_widget(port_input)
        row2.add_widget(port_card)
        content.add_widget(row2)

        result_label = Label(text="", font_size=sp(13), color=TEXT_MUTED,
                              size_hint_y=None, height=dp(40), halign="center")
        result_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(result_label)

        popup = Popup(title="", content=content, size_hint=(0.88, 0.48),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0,0,0,0), background='', separator_height=0, title_size=0)

        def do_connect(*a):
            if connect_btn.disabled:
                return  # zaten bir baglanti denemesi suruyor
            new_ip = ip_input.text.strip()
            new_port_text = port_input.text.strip() or "8899"
            connect_btn.disabled = True
            connect_spinner = TextSpinner(connect_btn, "Baglaniliyor...")
            result_label.text = ""
            self._conn_check_gen += 1  # bu, artik EN YENI istek - eski kontroller onu ezemez
            my_gen = self._conn_check_gen

            def worker():
                got_lock = self._fetch_lock.acquire(timeout=12.0)
                if not got_lock:
                    status = "disconnected"
                else:
                    try:
                        status, _ = fetch_pi_data(new_ip, new_port_text, timeout=12.0)
                    finally:
                        self._fetch_lock.release()

                def update(dt):
                    connect_spinner.stop()
                    connect_btn.disabled = False
                    connect_btn.text = "Baglan"

                    if status in ("connected", "device_silent"):
                        # Pi'ye ulasiliyor -> bu ayarlari GERCEKTEN kaydet ve
                        # ust seritteki durumu ANINDA guncelle (eski kontroller ezmesin diye
                        # nesil sayacini da tekrar bu isteme sabitliyoruz)
                        self.pi_ip = new_ip
                        try:
                            self.pi_port = int(new_port_text)
                        except ValueError:
                            self.pi_port = 8899
                        self.save_session()
                        self._conn_check_gen = my_gen
                        self._apply_connection_status(status)

                    if status == "connected":
                        result_label.text = "Luksmetreye basariyla baglanildi!"
                        result_label.color = GREEN_TXT
                    elif status == "device_silent":
                        result_label.text = ("Pi'ye baglanildi ve kaydedildi,\n"
                                              "ama luksmetreden veri gelmiyor.\n"
                                              "USB baglantisini kontrol edin.")
                        result_label.color = (0.90, 0.60, 0.15, 1)
                    else:
                        result_label.text = "Baglanti basarisiz.\nIP/Port'u ve Wi-Fi'i kontrol edin."
                        result_label.color = RED_TXT
                Clock.schedule_once(update, 0)

            threading.Thread(target=worker, daemon=True).start()

        connect_btn = FlatButton(text="Baglan", bg_color=SUCCESS, font_size=sp(15), bold=True,
                                  size_hint_y=None, height=dp(50))
        connect_btn.bind(on_release=do_connect)
        content.add_widget(connect_btn)

        close_btn = FlatButton(text="Kapat", bg_color=CARD_LIGHT, font_size=sp(14),
                                size_hint_y=None, height=dp(46))
        close_btn.bind(on_release=lambda b: popup.dismiss())
        content.add_widget(close_btn)

        popup.open()


    def _open_standards(self):
        if self.on_open_standards:
            self.on_open_standards()

    def update_standard_badge(self, org, level):
        self.org = org
        self.level = level
        self.badge_label.text = f"{org} · {level}" if level else org
        self._update_ec_row_visibility()
        self._rebuild_table_header()
        if hasattr(self, "sequence") and self.sequence:
            self._update_active_label()
        self.save_session()

    def _update_ec_row_visibility(self):
        pass  # manuel EC girisi kaldirildi - EC artik ikinci bir Pi olcumuyle otomatik alinir

    # --- Izgara duzenleme penceresi ---
    def _open_grid_editor(self):
        content = PopupContent(padding=dp(18), spacing=dp(14))
        _popup_title_lbl = Label(text="Izgara Ayarlari", font_size=sp(16), bold=True, color=TEXT,
                                 size_hint_y=None, height=dp(30), halign="left")
        _popup_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(_popup_title_lbl)

        row_box = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        row_box.add_widget(Label(text="Satir", font_size=sp(14), color=TEXT_MUTED, size_hint_x=0.4))
        input_card1 = Card(bg_color=CARD_LIGHT, radius=10)
        rows_input = ThemedTextInput(text=str(self.rows_count_val), multiline=False,
                                      input_filter="int", font_size=sp(16), halign="center")
        input_card1.add_widget(rows_input)
        row_box.add_widget(input_card1)
        content.add_widget(row_box)

        col_box = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        col_box.add_widget(Label(text="Sutun", font_size=sp(14), color=TEXT_MUTED, size_hint_x=0.4))
        input_card2 = Card(bg_color=CARD_LIGHT, radius=10)
        cols_input = ThemedTextInput(text=str(self.cols_count_val), multiline=False,
                                      input_filter="int", font_size=sp(16), halign="center")
        input_card2.add_widget(cols_input)
        col_box.add_widget(input_card2)
        content.add_widget(col_box)

        warn = Label(text="", font_size=sp(12.5), color=RED_TXT, size_hint_y=None, height=dp(18))
        content.add_widget(warn)

        popup = Popup(title="", content=content, size_hint=(0.85, 0.52),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0,0,0,0), background='', separator_height=0, title_size=0)

        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        cancel_btn = FlatButton(text="Vazgec", bg_color=CARD_LIGHT, font_size=sp(14))
        cancel_btn.bind(on_release=lambda b: popup.dismiss())
        apply_btn = FlatButton(text="Uygula", bg_color=ACCENT, font_size=sp(14))

        def do_apply(*a):
            try:
                r = int(rows_input.text)
                c = int(cols_input.text)
            except ValueError:
                warn.text = "Gecerli bir sayi girin."
                return
            if r < 1 or c < 1:
                warn.text = "En az 1 olmali."
                return
            popup.dismiss()
            if self.measurements:
                self._confirm_grid_change(r, c)
            else:
                self.rows_count_val = r
                self.cols_count_val = c
                self.grid_value_label.text = f"{r} x {c}"
                self._recompute_sequence(start=True)
        apply_btn.bind(on_release=do_apply)

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(apply_btn)
        content.add_widget(btn_row)

        reset_btn = FlatButton(text="Tum Olcumleri Sifirla", bg_color=(0.20, 0.10, 0.11, 1),
                                color=(0.85, 0.55, 0.55, 1), font_size=sp(12.5),
                                size_hint_y=None, height=dp(38))
        reset_btn.bind(on_release=lambda b: (popup.dismiss(), self._confirm_reset()))
        content.add_widget(reset_btn)

        popup.open()

    def _confirm_grid_change(self, new_rows, new_cols):
        content = PopupContent(padding=dp(18), spacing=dp(16))
        _popup_title_lbl = Label(text="Izgara Boyutunu Degistir", font_size=sp(16), bold=True, color=TEXT,
                                 size_hint_y=None, height=dp(30), halign="left")
        _popup_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(_popup_title_lbl)
        content.add_widget(Label(
            text=f"Izgara boyutu {new_rows} x {new_cols} olarak degistirilecek.\n"
                 f"Mevcut {len(self.measurements)} olcum silinecek.\nEmin misiniz?",
            font_size=sp(14.5), color=TEXT, halign="center"))
        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        popup = Popup(title="", content=content, size_hint=(0.85, 0.44),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0,0,0,0), background='', separator_height=0, title_size=0)
        cancel_btn = FlatButton(text="Vazgec", bg_color=CARD_LIGHT, font_size=sp(14))
        confirm_btn = FlatButton(text="Evet, Degistir", bg_color=DANGER, font_size=sp(14))
        cancel_btn.bind(on_release=lambda b: popup.dismiss())

        def do_confirm(*a):
            popup.dismiss()
            self.rows_count_val = new_rows
            self.cols_count_val = new_cols
            self.grid_value_label.text = f"{new_rows} x {new_cols}"
            self._recompute_sequence(start=True)
            self.save_session()
        confirm_btn.bind(on_release=do_confirm)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        content.add_widget(btn_row)
        popup.open()

    def _confirm_reset(self):
        content = PopupContent(padding=dp(18), spacing=dp(16))
        _popup_title_lbl = Label(text="Sifirla", font_size=sp(16), bold=True, color=TEXT,
                                 size_hint_y=None, height=dp(30), halign="left")
        _popup_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(_popup_title_lbl)
        content.add_widget(Label(
            text="Tum olcum tablosu silinecek.\nBu islem geri alinamaz. Emin misiniz?",
            font_size=sp(15), color=TEXT, halign="center"))
        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        popup = Popup(title="", content=content, size_hint=(0.85, 0.4),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0,0,0,0), background='', separator_height=0, title_size=0)
        cancel_btn = FlatButton(text="Vazgec", bg_color=CARD_LIGHT, font_size=sp(14))
        confirm_btn = FlatButton(text="Evet, Sil", bg_color=DANGER, font_size=sp(14))
        cancel_btn.bind(on_release=lambda b: popup.dismiss())

        def do_confirm(*a):
            popup.dismiss()
            self._recompute_sequence(start=True, clear_table=True)
            self.save_session()
        confirm_btn.bind(on_release=do_confirm)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        content.add_widget(btn_row)
        popup.open()

    def _recompute_sequence(self, start, clear_table=True):
        self.sequence = build_measurement_sequence(self.rows_count_val, self.cols_count_val)
        self.current_index = 0
        self.frontier_index = 0
        self.fiba_round = 1
        self.fiba_step = 1
        self.fiba_r2_current_index = 0
        self.fiba_r2_frontier_index = 0
        if clear_table:
            self.measurements = {}
            self.ec_values = {}
            self.refresh_table()
        if start:
            self.measure_btn.disabled = False
            self._update_active_label()
        else:
            self.active_point_label.text = "Izgarayi baslatin"
            self.measure_btn.disabled = True

    def _fiba_round2_active(self):
        return self.org == "FIBA" and self.fiba_round == 2

    def _active_seq_index(self):
        return self.fiba_r2_current_index if self._fiba_round2_active() else self.current_index

    def _update_active_label(self):
        if self.org == "FIBA":
            if self.fiba_round == 1:
                editing = self.current_index != self.frontier_index
                if self.current_index >= len(self.sequence) and not editing:
                    self.active_point_label.text = "1. Tur tamamlandi - 2. Turu baslatin"
                    self.measure_btn.disabled = True
                    self.measure_btn.text = "OLCUM AL"
                    self._show_fiba_round2_button(True)
                    return
                self._show_fiba_round2_button(False)
                r, c = self.sequence[self.current_index]
                step = 1 if editing else self.fiba_step
                if editing:
                    self.active_point_label.text = f"Yeniden olculuyor: Grid No {self.current_index + 1}"
                elif step == 1:
                    self.active_point_label.text = (
                        f"1.Tur - 4 Dikey: Grid No {self.current_index + 1} "
                        f"({self.current_index + 1}/{len(self.sequence)})")
                else:
                    self.active_point_label.text = (
                        f"1.Tur - EC (270 probu kameraya cevrilmis): "
                        f"Grid No {self.current_index + 1}")
                self.measure_btn.text = "OLCUM AL (4 Dikey)" if step == 1 else "EC OLC (270->Kamera)"
                self.measure_btn.disabled = False
                return
            else:  # fiba_round == 2 (yatay/Eh turu)
                self._show_fiba_round2_button(False)
                self.measure_btn.text = "OLCUM AL"
                editing = self.fiba_r2_current_index != self.fiba_r2_frontier_index
                if self.fiba_r2_current_index >= len(self.sequence) and not editing:
                    self.active_point_label.text = "Tamamlandi (2 tur da bitti)"
                    self.measure_btn.disabled = True
                    return
                r, c = self.sequence[self.fiba_r2_current_index]
                if editing:
                    self.active_point_label.text = (
                        f"Yeniden olculuyor (Yatay): Grid No {self.fiba_r2_current_index + 1}")
                else:
                    self.active_point_label.text = (
                        f"2.Tur (Yatay): Grid No {self.fiba_r2_current_index + 1} "
                        f"({self.fiba_r2_current_index + 1}/{len(self.sequence)})")
                self.measure_btn.disabled = False
                return

        self.measure_btn.text = "OLCUM AL"
        editing = self.current_index != self.frontier_index
        if self.current_index >= len(self.sequence) and not editing:
            self.active_point_label.text = "Tamamlandi"
            self.measure_btn.disabled = True
            return
        r, c = self.sequence[self.current_index]
        if editing:
            self.active_point_label.text = f"Yeniden olculuyor: Grid No {self.current_index + 1}"
        else:
            self.active_point_label.text = f"Grid No {self.current_index + 1} ({self.current_index + 1}/{len(self.sequence)})"
        self.measure_btn.disabled = False

    def _show_fiba_round2_button(self, show):
        self.fiba_r2_btn.height = dp(52) if show else 0
        self.fiba_r2_btn.opacity = 1 if show else 0
        self.fiba_r2_btn.disabled = not show

    def _start_fiba_round2(self, *a):
        self.fiba_round = 2
        self.fiba_r2_current_index = 0
        self.fiba_r2_frontier_index = 0
        self._update_ec_row_visibility()
        self._update_active_label()
        self.save_session()

    def take_measurement(self, *a):
        if self._active_seq_index() >= len(self.sequence):
            return
        self.measure_btn.disabled = True
        self._measure_spinner = TextSpinner(self.measure_btn, "OLCUM ALINIYOR...")
        # Bu istegi EN YENI nesil olarak isaretle - boylece daha once baslamis
        # ama GEC biten bir arka plan baglanti kontrolu, bu olcumun dogru
        # sonucunu SONRADAN ezemez (bkz. _on_measurement_result).
        self._conn_check_gen += 1
        self._measurement_gen = self._conn_check_gen
        threading.Thread(target=self._do_measurement_fetch, daemon=True).start()

    def _do_measurement_fetch(self):
        # kilidi bekleyerek al (kisa bir arka plan kontroluyle CAKISMAYI onlemek icin) -
        # boylece iki istek AYNI ANDA Pi'nin USB portuna gitmez
        got_lock = self._fetch_lock.acquire(timeout=12.0)
        if not got_lock:
            Clock.schedule_once(lambda dt: self._on_measurement_result("disconnected", None), 0)
            return
        try:
            status, data = fetch_pi_data(self.pi_ip, self.pi_port, timeout=12.0)
        finally:
            self._fetch_lock.release()
        Clock.schedule_once(lambda dt: self._on_measurement_result(status, data), 0)

    def _on_measurement_result(self, status, data):
        if getattr(self, "_measure_spinner", None):
            self._measure_spinner.stop()
            self._measure_spinner = None
        # bu olcum sonucu, kendi baslattigi nesilden DAHA YENI bir kontrol
        # baslamadiysa gecerli - eger baslamissa (kullanici cok hizli baska
        # bir sey tetiklediyse) o daha yeni sonucu ezmeyelim
        my_gen = getattr(self, "_measurement_gen", None)
        if my_gen is None or my_gen >= self._conn_check_gen:
            self._conn_check_gen = my_gen if my_gen is not None else self._conn_check_gen
            self._apply_connection_status(status)
        self.measure_btn.text = "OLCUM AL"

        if status == "disconnected":
            self.measure_btn.disabled = False
            self._show_connection_error(
                "Pi'ye ulasilamiyor.\nWi-Fi baglantisini ve Pi'nin\nacik oldugunu kontrol edin.")
            return
        if status == "device_silent":
            self.measure_btn.disabled = False
            self._show_connection_error(
                "Pi'ye baglanildi ama cihazdan\nveri gelmiyor. T-10MA'nin USB\nbaglantisini kontrol edin.")
            return

        # Olculen degerler virgulden sonraki kismiyla karisik gorunuyordu -
        # bir sonraki tam sayiya (tavana) yuvarlayarak sade tam sayilar
        # olarak saklıyoruz. Bu, TEK bir noktada yapiliyor ki tablo, isi
        # haritasi ve tum hesaplamalar hep AYNI, tutarli degeri gorsun.
        if data:
            data = {k: (math.ceil(v) if isinstance(v, (int, float)) else v)
                     for k, v in data.items()}

        if self._fiba_round2_active():
            idx = self.fiba_r2_current_index
            if idx >= len(self.sequence):
                self.measure_btn.disabled = True
                return
            r, c = self.sequence[idx]
            existing = self.measurements.get(idx)
            existing_values = dict(existing["values"]) if existing and existing["values"] else {
                "Eh": None, "Ev0": None, "Ev90": None, "Ev180": None, "Ev270": None}
            existing_values["Eh"] = data.get("Eh")  # SADECE yatay guncellenir - 1. turun dikey/EC verisi korunur
            is_new = idx == self.fiba_r2_frontier_index
            self.measurements[idx] = {"r": r, "c": c, "values": existing_values}
            if is_new:
                self.fiba_r2_frontier_index += 1
            self.fiba_r2_current_index = self.fiba_r2_frontier_index
            self._render_row(idx)
            self._update_active_label()
            self.save_session()
            return

        if self.org == "FIBA" and self.fiba_round == 1:
            idx = self.current_index
            if idx >= len(self.sequence):
                self.measure_btn.disabled = True
                return
            r, c = self.sequence[idx]
            editing = idx != self.frontier_index
            if self.fiba_step == 1:
                # ADIM 1: SADECE 4 dikey yon (Ev0/90/180/270). Eh BOS birakilir -
                # gercek yatay deger sadece 2. Turda (zemin seviyesinde) olculur.
                values = {
                    "Eh": None, "Ev0": data.get("Ev0"), "Ev90": data.get("Ev90"),
                    "Ev180": data.get("Ev180"), "Ev270": data.get("Ev270"),
                }
                if idx in self.ec_values:
                    values["EC"] = self.ec_values[idx]  # onceden girilmis EC'yi KORU
                self.measurements[idx] = {"r": r, "c": c, "values": values}
                if not editing:
                    self.fiba_step = 2  # ayni noktada simdi EC (270->kamera) bekleniyor
            else:
                # ADIM 2: 270 probu KAMERAYA cevrilmis - bu ayri fetch'teki Ev270
                # degeri EC'yi temsil eder (1. adimin Ev270 dikey degerine DOKUNULMAZ)
                ec_val = data.get("Ev270")
                self.ec_values[idx] = ec_val
                self.measurements[idx]["values"]["EC"] = ec_val  # tablo/isi haritasi icin ayna
                self.fiba_step = 1
                if not editing and idx == self.frontier_index:
                    self.frontier_index += 1
                self.current_index = self.frontier_index
            self._render_row(idx)
            self._update_active_label()
            self.save_session()
            return

        idx = self.current_index
        if idx >= len(self.sequence):
            self.measure_btn.disabled = True
            return
        r, c = self.sequence[idx]
        values = {
            "Eh": data.get("Eh"), "Ev0": data.get("Ev0"), "Ev90": data.get("Ev90"),
            "Ev180": data.get("Ev180"), "Ev270": data.get("Ev270"),
        }

        is_new = (idx not in self.measurements) or (self.measurements[idx]["values"] is None)
        self.measurements[idx] = {"r": r, "c": c, "values": values}
        if is_new and idx == self.frontier_index:
            self.frontier_index += 1
        self.current_index = self.frontier_index

        self._render_row(idx)
        self._update_active_label()
        self.save_session()

    def _show_connection_error(self, message):
        content = PopupContent(padding=dp(18), spacing=dp(14))
        _popup_title_lbl = Label(text="Baglanti Sorunu", font_size=sp(16), bold=True, color=TEXT,
                                 size_hint_y=None, height=dp(30), halign="left")
        _popup_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(_popup_title_lbl)
        content.add_widget(Label(text=message, font_size=sp(14), color=TEXT, halign="center"))
        popup = Popup(title="", content=content, size_hint=(0.85, 0.42),
                       auto_dismiss=True, separator_color=BORDER, title_color=TEXT,
                       background_color=(0,0,0,0), background='', separator_height=0, title_size=0)
        close_btn = FlatButton(text="Tamam", bg_color=ACCENT, font_size=sp(14),
                                size_hint_y=None, height=dp(46))
        close_btn.bind(on_release=lambda b: popup.dismiss())
        content.add_widget(close_btn)
        popup.open()

    def refresh_table(self):
        """Sadece TAM sifirlamada kullanilir - tabloyu bosaltir."""
        self.table_body.clear_widgets()
        self.row_widgets = {}

    def _current_data_columns(self):
        """FIFA/UEFA'da 5 sabit prob; FIBA'da ayrica EC (Kafa No.0, kameraya
        cevrilmis) sutunu da eklenir."""
        cols = [t for t, _ in PROBES]
        if self.org == "FIBA":
            cols = cols + ["EC"]
        return cols

    def _rebuild_table_header(self):
        self.header_row.clear_widgets()
        self.header_row.cell_labels = []
        for h in ["Grid No"] + self._current_data_columns():
            self.header_row.add_cell(h, color=TEXT_MUTED, bold=True)

    def _render_row(self, idx):
        """Tek bir noktanin satirini olusturur veya (varsa) yerinde gunceller. O(1)."""
        data = self.measurements[idx]
        cols = self._current_data_columns()
        if idx in self.row_widgets:
            row = self.row_widgets[idx]
            if data["values"] is None:
                for i in range(1, len(cols) + 1):
                    row.update_cell(i, "--", color=TEXT_MUTED)
            else:
                for i, title in enumerate(cols, start=1):
                    val = data["values"].get(title)
                    row.update_cell(i, str(val) if val is not None else "--", color=TEXT)
            return

        pos = len(self.row_widgets)
        row_bg = ROW_A if pos % 2 == 0 else ROW_B
        row = TableRow(row_bg, point_index=idx, on_tap=self._row_tapped)
        row.add_cell(str(idx + 1), color=TEXT_MUTED)
        if data["values"] is None:
            for _ in cols:
                row.add_cell("--", color=TEXT_MUTED)
        else:
            for title in cols:
                val = data["values"].get(title)
                row.add_cell(str(val) if val is not None else "--", color=TEXT, bold=True)
        self.table_body.add_widget(row)
        self.row_widgets[idx] = row

    def _row_tapped(self, point_index):
        data = self.measurements.get(point_index)
        if not data:
            return

        content = PopupContent(padding=dp(18), spacing=dp(12))
        _popup_title_lbl = Label(text="Nokta Islemleri", font_size=sp(16), bold=True, color=TEXT,
                                 size_hint_y=None, height=dp(30), halign="left")
        _popup_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(_popup_title_lbl)
        content.add_widget(Label(
            text=f"Grid No {point_index + 1}",
            font_size=sp(16), bold=True, color=TEXT, size_hint_y=None, height=dp(28)))

        popup = Popup(title="", content=content, size_hint=(0.85, 0.46),
                       auto_dismiss=True, separator_color=BORDER, title_color=TEXT,
                       background_color=(0,0,0,0), background='', separator_height=0, title_size=0)

        remeasure_btn = FlatButton(text="Bu Noktayi Yeniden Olc", bg_color=ACCENT,
                                    font_size=sp(14.5), size_hint_y=None, height=dp(50))

        def do_remeasure(*a):
            popup.dismiss()
            if self._fiba_round2_active():
                self.fiba_r2_current_index = point_index
            else:
                self.current_index = point_index
                if self.org == "FIBA":
                    self.fiba_step = 1
            self._update_active_label()
        remeasure_btn.bind(on_release=do_remeasure)
        content.add_widget(remeasure_btn)

        reset_point_btn = FlatButton(text="Bu Noktayi Sifirla", bg_color=(0.20, 0.10, 0.11, 1),
                                      color=(0.85, 0.55, 0.55, 1), font_size=sp(14.5),
                                      size_hint_y=None, height=dp(50))

        def ask_reset_point(*a):
            popup.dismiss()
            self._confirm_reset_point(point_index)
        reset_point_btn.bind(on_release=ask_reset_point)
        content.add_widget(reset_point_btn)

        cancel_btn = FlatButton(text="Vazgec", bg_color=CARD_LIGHT, font_size=sp(14),
                                 size_hint_y=None, height=dp(46))
        cancel_btn.bind(on_release=lambda b: popup.dismiss())
        content.add_widget(cancel_btn)

        popup.open()

    def _confirm_reset_point(self, point_index):
        content = PopupContent(padding=dp(18), spacing=dp(16))
        _popup_title_lbl = Label(text="Noktayi Sifirla", font_size=sp(16), bold=True, color=TEXT,
                                 size_hint_y=None, height=dp(30), halign="left")
        _popup_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(_popup_title_lbl)
        content.add_widget(Label(
            text=f"Grid No {point_index + 1} noktasinin olcumu sifirlanacak.\nEmin misiniz?",
            font_size=sp(15), color=TEXT, halign="center"))
        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        popup = Popup(title="", content=content, size_hint=(0.85, 0.4),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0,0,0,0), background='', separator_height=0, title_size=0)
        cancel_btn = FlatButton(text="Vazgec", bg_color=CARD_LIGHT, font_size=sp(14))
        confirm_btn = FlatButton(text="Evet, Sifirla", bg_color=DANGER, font_size=sp(14))
        cancel_btn.bind(on_release=lambda b: popup.dismiss())

        def do_confirm(*a):
            popup.dismiss()
            data = self.measurements.get(point_index)
            if data:
                data["values"] = None
            if point_index == self.frontier_index - 1:
                self.frontier_index = point_index
            self.current_index = self.frontier_index
            self._render_row(point_index)
            self._update_active_label()
            self.save_session()
        confirm_btn.bind(on_release=do_confirm)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        content.add_widget(btn_row)
        popup.open()


class SelectDot(Widget):
    """Secili durumunu gosteren basit bir nokta - font/glyph sorunlarindan bagimsiz."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(16), dp(16))
        self.selected = False
        with self.canvas:
            self.color_instr = Color(0, 0, 0, 0)
            self.circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *a):
        self.circle.pos = self.pos
        self.circle.size = self.size

    def set_selected(self, selected):
        self.selected = selected
        self.color_instr.rgba = ACCENT if selected else (0, 0, 0, 0)


class LevelCard(BoxLayout):
    """FIFA/UEFA seviyesi karti - dokununca onizleme icin secilir (hemen uygulanmaz)."""
    def __init__(self, org, level, values, on_tap, **kwargs):
        super().__init__(orientation="vertical", padding=[dp(14), dp(10), dp(14), dp(10)],
                          spacing=dp(2), size_hint_y=None, **kwargs)
        self.org = org
        self.level = level
        self.on_tap = on_tap
        self.selected = False
        with self.canvas.before:
            self.bg_instr = Color(*CARD)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
            self.border_instr = Color(0, 0, 0, 0)
            self.border_line = Line(width=1.6)
        self.bind(pos=self._update, size=self._update)

        top_row = BoxLayout(size_hint_y=None, height=dp(24))
        top_row.add_widget(Label(text=level, font_size=sp(15.5), bold=True, color=TEXT,
                                  halign="left", text_size=(dp(200), None)))
        self.check_dot = SelectDot(pos_hint={"center_y": 0.5})
        dot_wrap = BoxLayout(size_hint_x=None, width=dp(24))
        dot_wrap.add_widget(self.check_dot)
        top_row.add_widget(dot_wrap)
        self.add_widget(top_row)

        is_training_grade = "Ev_avg" not in values  # Grade 1/2/3: yon-bazli, simetrik degil

        eh_min_v = values.get("Eh_min")
        if eh_min_v is not None:
            eh_line = f"1. Eh (yatay):  min {eh_min_v} lx / ort {values['Eh_avg']} lx"
        else:
            eh_line = f"1. Eh (yatay):  ort >= {values['Eh_avg']} lx"
        uh_line = f"    Duzgunluk: U1h >= {values['u1h']}   U2h >= {values['u2h']}"

        if is_training_grade:
            dir_lines = []
            for d_title in ["Ev0", "Ev90", "Ev180", "Ev270"]:
                d_avg = values.get(f"{d_title}_avg")
                if d_avg is None:
                    dir_lines.append(f"    {d_title}: gereksinim yok")
                else:
                    d_min = values.get(f"{d_title}_min")
                    dir_lines.append(f"    {d_title}: min {d_min} lx / ort {d_avg} lx  "
                                      f"(U1>={values.get(f'{d_title}_u1')} U2>={values.get(f'{d_title}_u2')})")
            ev_line = "2. Ev (yon-bazli, asagida):"
            uv_line = "\n".join(dir_lines)
        else:
            ev_line = f"2. Ev (0/90/180/270 - hepsi ayni):  min {values['Ev_min']} lx / ort {values['Ev_avg']} lx"
            if values['u1v'] is not None:
                uv_line = f"    Duzgunluk: U1v >= {values['u1v']}   U2v >= {values['u2v']}"
            else:
                uv_line = "    Duzgunluk: belirtilmemis"

        maur_line = f"3. Komsu Nokta Duzgunluk Orani (MAUR):  {values['maur']}"
        cct_line = f"4. Renk sicakligi (Tc):  {values['cct']}"
        ra_line = f"5. Renk gosterimi (Ra):  >= {values['ra']}"
        grid_line = f"6. Referans izgara:  {values['reference_grid']}" if is_training_grade else None

        line_list = [eh_line, uh_line, ev_line, uv_line, maur_line, cct_line, ra_line]
        if grid_line:
            line_list.append(grid_line)
        primary_text = "\n".join(line_list)

        self.primary = Label(text=primary_text, font_size=sp(11.5), color=TEXT_MUTED,
                              halign="left", valign="top",
                              text_size=(dp(288), None), size_hint_y=None)
        self.primary.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        self.add_widget(self.primary)

        # --- Daha az sik kullanilan alanlar: dokununca acilir/kapanir ---
        mcm_line = f"Mac Sureklilik Modu (MCM):  {values.get('mcm', 'belirtilmemis')}"
        ff_line = f"Titresim Faktoru (FF):  {values['ff']}"
        rg_line = f"Kamasma orani (RG):  {values['rg']}"
        mf_line = f"Bakim faktoru (MF):  {values['mf']}"
        self.extra_text = "\n".join([mcm_line, ff_line, rg_line, mf_line])

        self.expanded = False
        self.toggle_label = Label(text="Tum Detaylar (Bakim, Kamasma, Titresim..)  v",
                                   font_size=sp(11.5), color=ACCENT, bold=True,
                                   halign="left", valign="middle",
                                   text_size=(dp(288), dp(26)),
                                   size_hint_y=None, height=dp(26))
        self.add_widget(self.toggle_label)

        self.extra_label = Label(text="", font_size=sp(11.5), color=TEXT_MUTED,
                                  halign="left", valign="top",
                                  text_size=(dp(288), None), size_hint_y=None, height=0)
        self.extra_label.bind(texture_size=self._on_extra_texture)
        self.add_widget(self.extra_label)

        self.bind(minimum_height=self.setter("height"))

    def _on_extra_texture(self, instance, value):
        if self.expanded:
            instance.height = value[1]

    def _toggle_expand(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.toggle_label.text = "Tum Detaylar (Bakim, Kamasma, Titresim..)  ^"
            self.extra_label.text = self.extra_text
        else:
            self.toggle_label.text = "Tum Detaylar (Bakim, Kamasma, Titresim..)  v"
            self.extra_label.text = ""
            self.extra_label.height = 0

    def _update(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, 14)

    def set_selected(self, selected):
        self.selected = selected
        self.border_instr.rgba = ACCENT if selected else (0, 0, 0, 0)
        self.check_dot.set_selected(selected)

    def on_touch_down(self, touch):
        if self.toggle_label.collide_point(*touch.pos):
            self._toggle_expand()
            return True
        if self.collide_point(*touch.pos):
            original = self.bg_instr.rgba[:]
            self.bg_instr.rgba = lighten(original, 0.08)
            Clock.schedule_once(lambda dt: setattr(self.bg_instr, 'rgba', original), 0.15)
            self.on_tap(self.org, self.level)
            return True
        return super().on_touch_down(touch)


class StandardsScreen(Screen):
    def __init__(self, measure_screen, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BG)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.measure_screen = measure_screen
        self.browse_org = measure_screen.org
        self.preview_level = measure_screen.level

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))

        root.add_widget(Label(text="Standartlar", font_size=sp(20), bold=True, color=TEXT,
                               size_hint_y=None, height=dp(32)))

        # --- Aktif standart karti ---
        self.active_card = Card(bg_color=SUCCESS_TINT, radius=14, border_color=SUCCESS,
                                 size_hint_y=None, height=dp(54), padding=[dp(16), 0, dp(16), 0])
        active_row = BoxLayout()
        active_row.add_widget(Label(text="Aktif standart", font_size=sp(13),
                                     color=SUCCESS, size_hint_x=0.5))
        self.active_label = Label(text=f"{measure_screen.org} · {measure_screen.level}",
                                   font_size=sp(15), bold=True, color=TEXT)
        active_row.add_widget(self.active_label)
        self.active_card.add_widget(active_row)
        root.add_widget(self.active_card)

        # --- Organizasyon secici ---
        org_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.org_buttons = {}
        for org_name in list(STANDARDS.keys()) + ["FIBA"]:
            btn = FlatButton(text=org_name, bg_color=CARD_LIGHT, font_size=sp(15))
            btn.bind(on_release=lambda b, o=org_name: self.set_browse_org(o))
            org_row.add_widget(btn)
            self.org_buttons[org_name] = btn
        root.add_widget(org_row)

        # --- Seviye listesi ---
        scroll = ScrollView(size_hint=(1, 1))
        self.level_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        self.level_list.bind(minimum_height=self.level_list.setter("height"))
        scroll.add_widget(self.level_list)
        root.add_widget(scroll)

        # --- Uygula butonu ---
        self.apply_btn = FlatButton(text="Bu Standardi Kullan", bg_color=ACCENT, radius=14,
                                     font_size=sp(16), bold=True,
                                     size_hint_y=None, height=dp(56))
        self.apply_btn.bind(on_release=self.apply_standard)
        root.add_widget(self.apply_btn)

        self.add_widget(root)
        self.set_browse_org(self.browse_org)

    def _update_bg(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def set_browse_org(self, org_name):
        self.browse_org = org_name
        for name, btn in self.org_buttons.items():
            new_bg = ACCENT if name == org_name else CARD_LIGHT
            btn.bg_instr.rgba = new_bg
            btn._base_color = new_bg
            btn.color = text_color_for_bg(new_bg)

        self.level_list.clear_widgets()
        self.level_cards = {}

        if org_name == "FIBA":
            self.preview_level = ""
            self._build_fiba_info_card()
            self._refresh_selection_marks()
            return

        for level_name, values in STANDARDS[org_name].items():
            card = LevelCard(org_name, level_name, values, on_tap=self.preview_select)
            self.level_list.add_widget(card)
            self.level_cards[level_name] = card

        # eger aktif standart bu organizasyondaysa, onu onizlemede isaretli goster
        if self.measure_screen.org == org_name and self.measure_screen.level in self.level_cards:
            self.preview_level = self.measure_screen.level
        else:
            self.preview_level = None
        self._refresh_selection_marks()

    def _build_fiba_info_card(self):
        ms = self.measure_screen
        card = Card(bg_color=CARD, radius=14, orientation="vertical", size_hint_y=None,
                    padding=[dp(16), dp(14), dp(16), dp(14)], spacing=dp(8))
        card.add_widget(Label(text="FIBA Resmi Basketbol Aydinlatma Standardi", font_size=sp(14),
                               bold=True, color=TEXT, size_hint_y=None, height=dp(24),
                               halign="left", text_size=(dp(300), None)))

        ppa = FIBA_STANDARDS["PPA"]
        tpa = FIBA_STANDARDS["TPA"]
        info_text = (
            f"PPA - Ana Oyun Alani (19x32m):\n"
            f"1. EC (Kamera):  ort > {ppa['ec_avg']} lx\n"
            f"    Duzgunluk: U1 >= {ppa['ec_u1']:.2f}   U2 >= {ppa['ec_u2']:.2f}\n"
            f"2. EV (0/90/180/270 - her biri ayri):  ort > {ppa['ev_avg']} lx\n"
            f"    Duzgunluk: U1 >= {ppa['ev_u1']:.2f}   U2 >= {ppa['ev_u2']:.2f}\n"
            f"    Yon Dengesi (min/maks): >= {ppa['ev_dir_ratio']:.2f}\n"
            f"3. EH (Yatay):  ort {ppa['eh_avg_min']}-{ppa['eh_avg_max']} lx arasi\n"
            f"    Duzgunluk: U1 >= {ppa['eh_u1']:.2f}   U2 >= {ppa['eh_u2']:.2f}\n\n"
            f"TPA - Toplam Oyun Alani (22x35m):  ayni degerler, sadece Duzgunluk\n"
            f"esikleri biraz daha toleransli (U1 >= {tpa['ec_u1']:.2f}, U2 >= {tpa['ec_u2']:.2f})\n\n"
            f"Isik kaynagi:  Titresim <= %1   Renk gosterimi >= 80   "
            f"Renk sicakligi 4000-6000K\n\n"
            f"Izgara:  secilince otomatik 17 x 11 olur. En distaki nokta "
            f"halkasi TPA, ic kisim hem PPA hem TPA sayilir."
        )
        info_lbl = Label(text=info_text, font_size=sp(12), color=TEXT_MUTED,
                          size_hint_y=None, halign="left", valign="top")
        info_lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        info_lbl.bind(texture_size=lambda i, ts: setattr(i, "height", ts[1]))
        card.add_widget(info_lbl)

        ec_note = Label(text="EC degeri: Olcum ekraninda, her nokta icin Alici Kafa "
                              "No.0 kameraya cevrilerek AYRI bir olcum olarak alinir.",
                         font_size=sp(11.5), color=TEXT_MUTED, size_hint_y=None,
                         halign="left", valign="top")
        ec_note.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        ec_note.bind(texture_size=lambda i, ts: setattr(i, "height", ts[1]))
        card.add_widget(ec_note)

        card.bind(minimum_height=card.setter("height"))
        self.level_list.add_widget(card)

    def preview_select(self, org, level):
        self.browse_org = org
        self.preview_level = level
        self._refresh_selection_marks()

    def _refresh_selection_marks(self):
        for name, card in self.level_cards.items():
            card.set_selected(name == self.preview_level)

    def apply_standard(self, *a):
        if self.preview_level is None:
            return
        content = PopupContent(padding=dp(18), spacing=dp(16))
        _popup_title_lbl = Label(text="Standardi Uygula", font_size=sp(16), bold=True, color=TEXT,
                                 size_hint_y=None, height=dp(30), halign="left")
        _popup_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(_popup_title_lbl)
        standard_label = f"{self.browse_org} · {self.preview_level}" if self.preview_level else self.browse_org

        ms_ref = self.measure_screen
        entering_fiba = self.browse_org == "FIBA"
        leaving_fiba = ms_ref.org == "FIBA" and self.browse_org != "FIBA"
        has_data = len(ms_ref.measurements) > 0

        if entering_fiba:
            msg = (f"Aktif standart\n{standard_label}\n"
                   "olarak degistirilecek.\n\nIzgara otomatik olarak 17 x 11 "
                   "yapilacak ve mevcut olcumler sifirlanacak.\n\nEmin misiniz?")
        elif leaving_fiba:
            msg = (f"Aktif standart\n{standard_label}\n"
                   "olarak degistirilecek.\n\nFIBA'ya ozel EC verisi baska "
                   "standartlarla uyumlu olmadigindan, mevcut olcumler "
                   "sifirlanacak.\n\nEmin misiniz?")
        elif has_data:
            msg = (f"Aktif standart\n{standard_label}\n"
                   "olarak degistirilecek.\n\nMevcut olcumleriniz KORUNACAK - "
                   "izgara ve veriler aynen kalacak, sadece karsilastirilan "
                   "standart degisecek.\n\nEmin misiniz?")
        else:
            level_values = STANDARDS.get(self.browse_org, {}).get(self.preview_level, {})
            auto_rows, auto_cols = level_values.get("auto_grid", (12, 8))
            grid_desc = level_values.get("reference_grid", "resmi 96 nokta duzeni")
            msg = (f"Aktif standart\n{standard_label}\n"
                   f"olarak degistirilecek.\n\nIzgara otomatik olarak {auto_rows} x {auto_cols} "
                   f"({grid_desc}) yapilacak.\n\nEmin misiniz?")
        msg_lbl = Label(text=msg, font_size=sp(15), color=TEXT, halign="center", valign="middle")
        msg_lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        content.add_widget(msg_lbl)
        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        popup = Popup(title="", content=content,
                       size_hint=(0.85, 0.5),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0,0,0,0), background='', separator_height=0, title_size=0)
        cancel_btn = FlatButton(text="Vazgec", bg_color=CARD_LIGHT, font_size=sp(14))
        confirm_btn = FlatButton(text="Evet, Uygula", bg_color=ACCENT, font_size=sp(14))
        cancel_btn.bind(on_release=lambda b: popup.dismiss())

        def do_confirm(*a):
            popup.dismiss()
            ms = self.measure_screen
            ms.update_standard_badge(self.browse_org, self.preview_level)
            if entering_fiba:
                ms.fiba_ppa_margin = 1  # en dis nokta halkasi haric hepsi PPA
                ms.rows_count_val = 17
                ms.cols_count_val = 11
                ms.grid_value_label.text = "17 x 11"
                ms._recompute_sequence(start=True)
                ms.save_session()
            elif leaving_fiba:
                # FIBA'dan CIKILIYOR: EC sutunu/verisi baska standartlarla
                # uyumsuz - izgarayi ve olcumleri temizleyerek karisikligi onle
                ms._recompute_sequence(start=True)
                ms.save_session()
            elif has_data:
                # AYNI AILE icinde (FIFA<->FIFA/UEFA) gecis YAPILIYOR ve
                # zaten olcum VAR - izgaraya ve olcumlere HIC DOKUNMA, sadece
                # karsilastirilan esik profilini (org/level) degistir. Boylece
                # yanlislikla secilen bir standart, alinan olcumleri silmez.
                ms._rebuild_table_header()
                ms.save_session()
            else:
                # veri yok, resmi izgarayi rahatlikla uygulayabiliriz
                level_values = STANDARDS.get(self.browse_org, {}).get(self.preview_level, {})
                auto_rows, auto_cols = level_values.get("auto_grid", (12, 8))
                ms.rows_count_val = auto_rows
                ms.cols_count_val = auto_cols
                ms.grid_value_label.text = f"{auto_rows} x {auto_cols}"
                ms._recompute_sequence(start=True)
                ms.save_session()
            self.active_label.text = standard_label
        confirm_btn.bind(on_release=do_confirm)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        content.add_widget(btn_row)
        popup.open()

    def on_pre_enter(self, *a):
        # sekmeye her girildiginde aktif standardi tekrar yansit
        ms = self.measure_screen
        self.active_label.text = f"{ms.org} · {ms.level}" if ms.level else ms.org


def compute_maur_failures(by_pos, threshold):
    """Izgaradaki her nokta ile SAG ve ASAGI komsusu arasindaki orani kontrol eder.
    (Her komsu ciftini bu sekilde tam bir kez kontrol etmis oluruz.)
    Donen: [((r1,c1),(r2,c2), deger1, deger2, oran), ...] - basarisiz olanlar."""
    failures = []
    for (r, c), v in by_pos.items():
        for dr, dc in [(1, 0), (0, 1)]:
            neighbor = (r + dr, c + dc)
            if neighbor in by_pos:
                v2 = by_pos[neighbor]
                biggest = max(v, v2)
                ratio = (min(v, v2) / biggest) if biggest > 0 else 1.0
                if ratio < threshold:
                    failures.append(((r, c), neighbor, v, v2, ratio))
    return failures


def lux_color(value, vmin, vmax):
    """'False color' - dusuk deger sari, orta yesil, yuksek deger kirmizi."""
    if vmax <= vmin:
        t = 0.5
    else:
        t = (value - vmin) / (vmax - vmin)
    t = max(0.0, min(1.0, t))
    stops = [
        (0.90, 0.85, 0.20, 1),   # sari (dusuk)
        (0.30, 0.75, 0.30, 1),   # yesil (orta)
        (0.85, 0.20, 0.20, 1),   # kirmizi (yuksek)
    ]
    n = len(stops) - 1
    scaled = t * n
    idx = min(int(scaled), n - 1)
    frac = scaled - idx
    c0, c1 = stops[idx], stops[idx + 1]
    return tuple(c0[i] + (c1[i] - c0[i]) * frac for i in range(4))


def text_color_for_bg(bg):
    """Arka plan parlakligina gore okunakli metin rengi (siyah/beyaz) secer."""
    luminance = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
    return (0.05, 0.05, 0.05, 1) if luminance > 0.6 else (1, 1, 1, 1)


class TextureView(Widget):
    """Programatik olusturulan dokuyu (texture) guvenilir sekilde cizer -
    kivy.uix.image.Image bazen custom texture atamalarini kendi ic mantigiyla sifirlayabiliyor."""
    def __init__(self, texture, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(texture=texture, pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ActivePointCell(FloatLayout):
    """Su an olculecek AKTIF noktayi gosterir - henuz olculmemis olsa bile,
    YANIP SONen bir cerceveyle dikkat ceker."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.fill_instr = Color(*ACCENT)
            self.fill_instr.a = 0.22
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
            self.border_instr = Color(*ACCENT)
            self.border = Line(width=2.2)
        self.bind(pos=self._update, size=self._update)
        lbl = Label(text="-", font_size=sp(16), bold=True, color=ACCENT)
        self.add_widget(lbl)
        self.anim = Animation(a=0.15, duration=0.55) + Animation(a=0.85, duration=0.55)
        self.anim.repeat = True
        self.anim.start(self.border_instr)

    def _update(self, *a):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 6)

    def stop(self):
        Animation.cancel_all(self.border_instr)


class UnmeasuredCell(Label):
    """Henuz olculmemis (ve su an aktif OLMAYAN) noktalar icin sabit, sonuk sembol."""
    def __init__(self, **kwargs):
        super().__init__(text="-", font_size=sp(15), bold=False, color=TEXT_MUTED, **kwargs)


class ExtremeCell(BoxLayout):
    """En yuksek/en dusuk 3 degeri vurgulamak icin - kalin cerceve + kontrastli zemin."""
    def __init__(self, text, border_color, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 0.60)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
            Color(*border_color)
            self.border = Line(width=1.8)
        self.bind(pos=self._update, size=self._update)
        self.add_widget(Label(text=text, font_size=sp(11.5), bold=True, color=(1, 1, 1, 1)))

    def _update(self, *a):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, 6)


class CornerFlagCell(Widget):
    """En yuksek/en dusuk 3 degeri SADE bir sekilde vurgular: kutu/cerceve YOK,
    sadece kose ucgeni (kontur ile HER zeminde net gorunur) + normal renkte sayi."""
    def __init__(self, text, cell_bg, accent_color, font_size=11.5, **kwargs):
        super().__init__(**kwargs)
        self.accent_color = accent_color
        self.text_color = text_color_for_bg(cell_bg)
        with self.canvas:
            self.contour_instr = Color(*self.text_color)
            self.contour_tri = Triangle()
            self.flag_instr = Color(*accent_color)
            self.flag_tri = Triangle()
        self.bind(pos=self._update, size=self._update)
        self.lbl = Label(text=text, font_size=sp(font_size), bold=True, color=self.text_color)
        self.add_widget(self.lbl)

    def _update(self, *a):
        x, y, w, h = self.x, self.y, self.width, self.height
        fs = w * 0.26
        halo = fs * 1.35
        self.contour_tri.points = [x + w - halo, y + h, x + w, y + h, x + w, y + h - halo]
        self.flag_tri.points = [x + w - fs, y + h, x + w, y + h, x + w, y + h - fs]
        self.lbl.pos = (x, y)
        self.lbl.size = (w, h)


class HeatCell(BoxLayout):
    """Isi haritasindaki tek bir hucre - renkli kutu + deger."""
    def __init__(self, text, bg_color, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.color_instr = Color(*bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)
        self.label = Label(text=text, font_size=sp(10), bold=True,
                            color=text_color_for_bg(bg_color))
        self.add_widget(self.label)

    def _update(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size



class ControlScreen(Screen):
    """Kontrol Paneli - DIALux/Relux tarzi pseudo-color isi haritasi."""

    DATASETS = ["Eh", "Ev0", "Ev90", "Ev180", "Ev270", "EC"]

    def __init__(self, measure_screen, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BG)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.measure_screen = measure_screen
        self.current_dataset = "Eh"
        self.zoom = 1.0
        self.base_cell_size = dp(42)
        self.label_font_size = 12.5

        self.root_box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        self.root_box.add_widget(Label(text="Sonuc", font_size=sp(20), bold=True,
                                        color=TEXT, size_hint_y=None, height=dp(32)))

        # --- Veri seti secici (Eh / Ev0 / Ev90 / Ev180 / Ev270) ---
        selector_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(4))
        self.dataset_buttons = {}
        for name in self.DATASETS:
            display_text = "Kamera" if name == "EC" else name
            btn = FlatButton(text=display_text, bg_color=CARD_LIGHT, font_size=sp(12.5))
            btn.bind(on_release=lambda b, n=name: self.set_dataset(n))
            if name == "EC":
                btn.size_hint_x = 0
                btn.opacity = 0
                btn.disabled = True
            selector_row.add_widget(btn)
            self.dataset_buttons[name] = btn
        self.root_box.add_widget(selector_row)

        # --- Yakinlastirma kontrolleri ---
        # --- MAUR gorunumu acma/kapama ---
        self.maur_mode = False
        self.maur_btn = FlatButton(text="MAUR Gorunumu: Kapali", bg_color=CARD_LIGHT,
                                    font_size=sp(13), size_hint_y=None, height=dp(40))
        self.maur_btn.bind(on_release=lambda b: self.toggle_maur())
        self.root_box.add_widget(self.maur_btn)

        zoom_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        zoom_out_btn = FlatButton(text="-", bg_color=CARD_LIGHT, font_size=sp(18), bold=True,
                                   size_hint_x=0.2)
        zoom_out_btn.bind(on_release=lambda b: self.change_zoom(-0.2))
        self.zoom_label = FlatButton(text="100%", bg_color=CARD, font_size=sp(13),
                                      color=TEXT_MUTED, size_hint_x=0.6)
        self.zoom_label.bind(on_release=lambda b: self.reset_zoom())
        zoom_in_btn = FlatButton(text="+", bg_color=CARD_LIGHT, font_size=sp(18), bold=True,
                                  size_hint_x=0.2)
        zoom_in_btn.bind(on_release=lambda b: self.change_zoom(0.2))
        zoom_row.add_widget(zoom_out_btn)
        zoom_row.add_widget(self.zoom_label)
        zoom_row.add_widget(zoom_in_btn)
        # Parmakla (pinch) yakinlastirma KALDIRILDI (gercek cihazda ciddi
        # goruntu bozulmalarina yol acti ve bu ortamda guvenle
        # duzeltilemedi) - +/- butonlari artik TEK ve GUVENILIR
        # yakinlastirma yontemi, bu yuzden ekranda GORUNUR olmali.
        self.root_box.add_widget(zoom_row)

        # --- Icerik alani (her sekmeye girildiginde yeniden kurulur) ---
        self.content_area = BoxLayout(orientation="vertical", spacing=dp(10),
                                       size_hint_y=None)
        self.content_area.bind(minimum_height=self.content_area.setter("height"))
        page_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True,
                                  bar_width=dp(6))
        page_scroll.add_widget(self.content_area)
        self.root_box.add_widget(page_scroll)

        self.add_widget(self.root_box)
        self._update_button_colors()

    def _update_bg(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def change_zoom(self, delta):
        self.zoom = max(0.5, min(2.6, round(self.zoom + delta, 2)))
        self.zoom_label.text = f"{int(self.zoom * 100)}%"
        self._build_heatmap()

    def toggle_maur(self):
        self.maur_mode = not self.maur_mode
        new_bg = ACCENT if self.maur_mode else CARD_LIGHT
        self.maur_btn.bg_instr.rgba = new_bg
        self.maur_btn._base_color = new_bg
        self.maur_btn.color = text_color_for_bg(new_bg)
        self.maur_btn.text = f"MAUR Gorunumu: {'Acik' if self.maur_mode else 'Kapali'}"
        self._build_heatmap()

    def reset_zoom(self):
        self.zoom = 1.0
        self.zoom_label.text = "100%"
        self._build_heatmap()

    def set_dataset(self, name):
        self.current_dataset = name
        self._update_button_colors()
        self._build_heatmap()

    def _update_button_colors(self):
        for name, btn in self.dataset_buttons.items():
            active = name == self.current_dataset
            new_bg = ACCENT if active else CARD_LIGHT
            btn.bg_instr.rgba = new_bg
            btn._base_color = new_bg
            btn.color = text_color_for_bg(new_bg)

    def on_pre_enter(self, *a):
        ms = self.measure_screen
        is_fiba = (ms.org == "FIBA")
        if is_fiba and self.maur_mode:
            self.maur_mode = False  # FIBA'da MAUR kavrami yok - zorla kapat
        self.maur_btn.height = 0 if is_fiba else dp(40)
        self.maur_btn.opacity = 0 if is_fiba else 1
        self.maur_btn.disabled = is_fiba

        ec_btn = self.dataset_buttons["EC"]
        ec_btn.size_hint_x = 1 if is_fiba else 0
        ec_btn.opacity = 1 if is_fiba else 0
        ec_btn.disabled = not is_fiba
        if not is_fiba and self.current_dataset == "EC":
            self.current_dataset = "Eh"
        self._update_button_colors()
        self._build_heatmap()

    def on_leave(self, *a):
        if getattr(self, "_active_cell", None):
            self._active_cell.stop()

    def _build_heatmap(self):
        if getattr(self, "_active_cell", None):
            self._active_cell.stop()
        self._active_cell = None
        # GORUNUMUN TAM ORTASININ, izgara icindeki (0-1) GORECELI konumunu
        # hatirla - boylece yakinlastirinca/uzaklastirinca o nokta hep
        # merkezde kalir (basit oransal kaydirma, ic buyuklukler cok
        # degistiginde koseye sacma bir kaymaya yol aciyordu).
        center_frac_x, center_frac_y = 0.5, 0.5
        had_previous_scroll = False
        old_scroll = getattr(self, "_heatmap_scroll", None)
        old_size = getattr(self, "_last_display_size", None)
        if old_scroll and old_size and old_scroll.width > 0:
            had_previous_scroll = True
            old_w, old_h = old_size
            vp_w, vp_h = old_scroll.width, old_scroll.height
            scrollable_w = max(old_w - vp_w, 0.001)
            scrollable_h = max(old_h - vp_h, 0.001)
            center_x_px = old_scroll.scroll_x * scrollable_w + vp_w / 2
            center_y_px = old_scroll.scroll_y * scrollable_h + vp_h / 2
            center_frac_x = max(0.0, min(1.0, center_x_px / old_w))
            center_frac_y = max(0.0, min(1.0, center_y_px / old_h))
        self.content_area.clear_widgets()
        ms = self.measure_screen
        satir_n, sutun_n = ms.rows_count_val, ms.cols_count_val

        by_pos = {}
        if self.current_dataset == "EC":
            for idx, data in ms.measurements.items():
                if idx in ms.ec_values:
                    by_pos[(data["r"], data["c"])] = ms.ec_values[idx]
        else:
            for data in ms.measurements.values():
                if data["values"] is not None and data["values"].get(self.current_dataset) is not None:
                    by_pos[(data["r"], data["c"])] = data["values"][self.current_dataset]

        if not by_pos:
            msg = Label(text="Henuz olcum yok.\nOlcum Verisi sekmesinden\nizgarayi baslatip olcum alin.",
                        font_size=sp(15), color=TEXT_MUTED, halign="center")
            msg.bind(size=lambda i, v: setattr(i, "text_size", v))
            self.content_area.add_widget(msg)
            return

        vmin, vmax = min(by_pos.values()), max(by_pos.values())
        thresholds = STANDARDS.get(ms.org, {}).get(ms.level, {})

        # --- KRITIK EKSEN KURALI ---
        # Ekranda: SUTUN sayisi DIKEY (yukaridan asagi), SATIR sayisi YATAY (soldan saga).
        # "r" = satir indeksi (0..satir_n-1) -> YATAY eksende (sutun_idx = r)
        # "c" = sutun indeksi (0..sutun_n-1) -> DIKEY eksende (satir_idx = c)
        disp_cols = satir_n   # ekranda yatayda kac hucre (az sayida olur)
        disp_rows = sutun_n   # ekranda dikeyde kac hucre (cok sayida olur)

        cell_h = self.base_cell_size * self.zoom
        cell_w = cell_h * 1.4  # dikdortgen hucreler - kare degil
        display_w, display_h = cell_w * disp_cols, cell_h * disp_rows

        # --- Yumuşak gradyanli doku (texture) olustur ---
        texture = Texture.create(size=(disp_cols, disp_rows), colorfmt="rgba")
        texture.mag_filter = "linear"
        texture.min_filter = "linear"

        buf = bytearray(disp_cols * disp_rows * 4)
        for tex_row in range(disp_rows):
            # KRITIK: Grid No 1 (satir r=0, sutun c=0) SOL UST kosede olmali.
            # Dikey eksen = sutun indeksi (c). c=0 EN USTTE gorunmeli.
            disp_r = disp_rows - 1 - tex_row
            c = disp_r  # dikey konum = sutun indeksi
            for tex_col in range(disp_cols):
                r = tex_col  # yatay konum = satir indeksi (r=0 SOLDA)
                val = by_pos.get((r, c))
                color = lux_color(val, vmin, vmax) if val is not None else CARD_LIGHT
                idx = (tex_row * disp_cols + tex_col) * 4
                buf[idx:idx + 4] = bytes(int(max(0.0, min(1.0, ch)) * 255) for ch in color)
        texture.blit_buffer(bytes(buf), colorfmt="rgba", bufferfmt="ubyte")

        heat_container = FloatLayout(size=(display_w, display_h), size_hint=(None, None))
        img = TextureView(texture=texture, size=(display_w, display_h), pos=(0, 0),
                           size_hint=(None, None))
        heat_container.add_widget(img)

        # --- YENI: ince izgara cizgileri - hangi sayinin hangi hucreye ait
        #     oldugunu net gostermek icin (canvas.after -> her seyin USTUNDE cizilir) ---
        with heat_container.canvas.after:
            Color(*BORDER)
            for gi in range(disp_cols + 1):
                gx = gi * cell_w
                Line(points=[gx, 0, gx, display_h], width=1.3)
            for gj in range(disp_rows + 1):
                gy = gj * cell_h
                Line(points=[0, gy, display_w, gy], width=1.3)

            # --- FIBA aktifse: PPA sinirini kalin, renkli bir cerceveyle goster ---
            if ms.org == "FIBA":
                margin = ms.fiba_ppa_margin
                ppa_x0 = margin * cell_w
                ppa_y0 = margin * cell_h
                ppa_w = display_w - 2 * margin * cell_w
                ppa_h = display_h - 2 * margin * cell_h
                if ppa_w > 0 and ppa_h > 0:
                    Color(*ACCENT)
                    Line(rectangle=(ppa_x0, ppa_y0, ppa_w, ppa_h), width=2.4)

        def cell_pos(r, c):
            """Bir (satir, sutun) noktasinin ekran pikseli - yukaridaki ile ayni mantik."""
            x = r * cell_w
            y = (disp_rows - 1 - c) * cell_h
            return (x, y)

        # --- MAUR hesaplamasi (hucre vurgulamasindan ONCE yapilmali) ---
        maur_failures = []
        maur_threshold = thresholds.get("maur_ratio")
        maur_max_fail = thresholds.get("maur_max_fail")
        maur_failing_points = set()
        if self.maur_mode and maur_threshold is not None:
            maur_failures = compute_maur_failures(by_pos, maur_threshold)
            for (r1, c1), (r2, c2), v1, v2, ratio in maur_failures:
                maur_failing_points.add((r1, c1))
                maur_failing_points.add((r2, c2))

        # --- Sayilari resmin ustune bindir ---
        # MAUR modu ACIKKEN: min/maks vurgusu YOK, sadece MAUR hatasi olan noktalar isaretlenir.
        # MAUR modu KAPALIYKEN: normal en yuksek/dusuk 3 deger vurgusu.
        MIN_COLOR = (0.30, 0.55, 0.95, 1)   # mavi - en dusuk degerler (sadece normal modda)
        MAX_COLOR = (0.90, 0.25, 0.25, 1)   # kirmizi - en yuksek degerler (sadece normal modda)
        MAUR_FAIL_COLOR = (1, 0.60, 0.0, 1)  # turuncu - MAUR hatali nokta

        if self.maur_mode:
            lowest_keys = set()
            highest_keys = set()
        else:
            sorted_items = sorted(by_pos.items(), key=lambda kv: kv[1])
            n_extreme = min(3, len(sorted_items))
            lowest_keys = {k for k, v in sorted_items[:n_extreme]}
            highest_keys = {k for k, v in sorted_items[-n_extreme:]}

        for (r, c), val in by_pos.items():
            pos = cell_pos(r, c)
            if self.maur_mode and (r, c) in maur_failing_points:
                cell = ExtremeCell(str(val), MAUR_FAIL_COLOR,
                                    size_hint=(None, None), size=(cell_w, cell_h))
                cell.pos = pos
                heat_container.add_widget(cell)
            elif (r, c) in lowest_keys:
                cell_bg = lux_color(val, vmin, vmax)
                cell = CornerFlagCell(str(val), cell_bg, MIN_COLOR, font_size=self.label_font_size,
                                       size_hint=(None, None), size=(cell_w, cell_h))
                cell.pos = pos
                heat_container.add_widget(cell)
            elif (r, c) in highest_keys:
                cell_bg = lux_color(val, vmin, vmax)
                cell = CornerFlagCell(str(val), cell_bg, MAX_COLOR, font_size=self.label_font_size,
                                       size_hint=(None, None), size=(cell_w, cell_h))
                cell.pos = pos
                heat_container.add_widget(cell)
            else:
                cell_bg = lux_color(val, vmin, vmax)
                lbl = Label(text=str(val), font_size=sp(self.label_font_size), bold=True,
                            color=text_color_for_bg(cell_bg),
                            size_hint=(None, None), size=(cell_w, cell_h))
                lbl.pos = pos
                heat_container.add_widget(lbl)

        # --- YENI: aktif (siradaki) nokta YANIP SONsun, digerleri sonuk sembol gostersin ---
        active_pos = None
        if ms.current_index < len(ms.sequence):
            ap_r, ap_c = ms.sequence[ms.current_index]
            if (ap_r, ap_c) not in by_pos:
                active_pos = (ap_r, ap_c)

        for r in range(satir_n):
            for c in range(sutun_n):
                if (r, c) in by_pos:
                    continue  # zaten yukarida cizildi
                pos = cell_pos(r, c)
                if (r, c) == active_pos:
                    cell = ActivePointCell(size_hint=(None, None), size=(cell_w, cell_h))
                    self._active_cell = cell
                else:
                    cell = UnmeasuredCell(size_hint=(None, None), size=(cell_w, cell_h))
                cell.pos = pos
                heat_container.add_widget(cell)

        # --- MAUR gorunumu: hatali komsuluklari BAGLANTI CIZGISIYLE de isaretle ---
        if self.maur_mode and maur_threshold is not None:
            for (r1, c1), (r2, c2), v1, v2, ratio in maur_failures:
                p1 = cell_pos(r1, c1)
                marker = Widget(size_hint=(None, None), size=(1, 1))
                with marker.canvas:
                    Color(0.88, 0.28, 0.25, 1)
                    if c1 == c2:  # r farkli -> ekranda YATAY komsuluk -> dikey bar
                        bar_w = dp(4)
                        Rectangle(pos=(p1[0] + cell_w - bar_w / 2, p1[1]),
                                  size=(bar_w, cell_h))
                    else:  # c farkli -> ekranda DIKEY komsuluk -> yatay bar
                        bar_h = dp(4)
                        Rectangle(pos=(p1[0], p1[1] - bar_h / 2), size=(cell_w, bar_h))
                heat_container.add_widget(marker)

        # --- YENI: her hucrenin icinde, dokunmaya GEREK KALMADAN her zaman
        #     gorunen KUCUK ve SONUK bir "Grid No X" etiketi ---
        pos_to_gridno = {rc: idx + 1 for idx, rc in enumerate(ms.sequence)}
        gridno_font_size = max(7, self.label_font_size * 0.6)
        for r in range(satir_n):
            for c in range(sutun_n):
                grid_no = pos_to_gridno.get((r, c))
                if grid_no is None:
                    continue
                val = by_pos.get((r, c))
                tag_bg = lux_color(val, vmin, vmax) if val is not None else CARD_LIGHT
                base_color = text_color_for_bg(tag_bg)
                tag_color = (base_color[0], base_color[1], base_color[2], 0.55)
                pos = cell_pos(r, c)
                tag = Label(text=str(grid_no), font_size=sp(gridno_font_size), bold=False,
                            color=tag_color, size_hint=(None, None), size=(cell_w, cell_h),
                            halign="left", valign="top",
                            text_size=(cell_w - dp(4), cell_h - dp(2)))
                tag.pos = pos
                heat_container.add_widget(tag)

        # --- Yakinlastirma SADECE asagidaki +/- butonlariyla yapilir.
        #     Parmakla pinch-zoom (Kivy'nin Scatter widget'i) KALDIRILDI:
        #     gercek cihazda tekrar eden ciddi goruntu bozulmalarina
        #     (kaymalar, eski haline donmeme) yol acti ve bu ortamda gercek
        #     coklu-dokunus jestleriyle test edilemedigi icin guvenle
        #     duzeltilemedi. +/- butonlari ayni zoom mekanizmasini kullanir
        #     ve tam test edilmis, guvenilir sekilde calisir. ---
        heat_wrapper = BoxLayout(size=(display_w, display_h), size_hint=(None, None))
        heat_wrapper.add_widget(heat_container)
        self._active_scatter = None

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=True,
                             bar_width=dp(6))
        scroll.add_widget(heat_wrapper)
        self._heatmap_scroll = scroll
        self._last_display_size = (display_w, display_h)

        def _restore_scroll(dt):
            if not had_previous_scroll:
                return  # ilk acilista Kivy'nin dogal varsayilanini (ust-sol) koru
            vp_w, vp_h = scroll.width, scroll.height
            scrollable_w = max(display_w - vp_w, 0.001)
            scrollable_h = max(display_h - vp_h, 0.001)
            target_x_px = center_frac_x * display_w
            target_y_px = center_frac_y * display_h
            scroll.scroll_x = max(0.0, min(1.0, (target_x_px - vp_w / 2) / scrollable_w))
            scroll.scroll_y = max(0.0, min(1.0, (target_y_px - vp_h / 2) / scrollable_h))
        Clock.schedule_once(_restore_scroll, 0)

        # --- Yon etiketleri (UEFA/FIFA yon tanimlamasi: Grid No 1 sol-ustte,
        #     ust=270, sag=0, alt=90, sol=180) ---
        VIEWPORT_H = dp(300)  # SABIT - yakinlastirma sadece ic icerigi buyutur, bu alan degismez
        DIR_LABEL_SIZE = dp(22)

        dir_style = dict(font_size=sp(12), bold=True, color=ACCENT)

        top_label = Label(text="270°", size_hint_y=None, height=DIR_LABEL_SIZE, **dir_style)
        bottom_label = Label(text="90°", size_hint_y=None, height=DIR_LABEL_SIZE, **dir_style)
        left_label = Label(text="180°", size_hint_x=None, width=DIR_LABEL_SIZE, **dir_style)
        right_label = Label(text="0°", size_hint_x=None, width=DIR_LABEL_SIZE, **dir_style)

        middle_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=VIEWPORT_H)
        middle_row.add_widget(left_label)
        middle_row.add_widget(scroll)
        middle_row.add_widget(right_label)

        grid_frame = BoxLayout(orientation="vertical", size_hint_y=None,
                                height=VIEWPORT_H + DIR_LABEL_SIZE * 2)
        grid_frame.add_widget(top_label)
        grid_frame.add_widget(middle_row)
        grid_frame.add_widget(bottom_label)

        grid_card = Card(bg_color=CARD, radius=14, padding=dp(6),
                          size_hint_y=None,
                          height=VIEWPORT_H + DIR_LABEL_SIZE * 2 + dp(12))
        grid_card.add_widget(grid_frame)
        self.content_area.add_widget(grid_card)

        if ms.org == "FIBA":
            ppa_note = Card(bg_color=CARD, radius=10, size_hint_y=None, height=dp(36),
                             padding=[dp(12), 0, dp(12), 0])
            note_row = BoxLayout(spacing=dp(8))
            swatch = Widget(size_hint_x=None, width=dp(18))
            with swatch.canvas:
                Color(*ACCENT)
                Line(rectangle=(2, 2, 14, 14), width=2)
            note_row.add_widget(swatch)
            note_row.add_widget(Label(text="Mavi cerceve = PPA siniri (disi = TPA)",
                                       font_size=sp(11.5), color=TEXT_MUTED, halign="left"))
            ppa_note.add_widget(note_row)
            self.content_area.add_widget(ppa_note)

        # --- MAUR hata listesi + genel dogrulama karti ---
        if self.maur_mode:
            if maur_threshold is None:
                info_card = Card(bg_color=CARD, radius=14, size_hint_y=None, height=dp(50),
                                  padding=[dp(16), 0, dp(16), 0])
                info_card.add_widget(Label(text="Bu standart seviyesi icin MAUR belirtilmemis.",
                                            font_size=sp(12.5), color=TEXT_MUTED))
                self.content_area.add_widget(info_card)
            else:
                point_no = {}
                for idx, d in ms.measurements.items():
                    if d["values"] is not None:
                        point_no[(d["r"], d["c"])] = idx + 1

                if maur_failures:
                    list_card = Card(bg_color=CARD, radius=14, orientation="vertical",
                                      padding=[dp(14), dp(10), dp(14), dp(10)], spacing=dp(6),
                                      size_hint_y=None)
                    list_card.add_widget(Label(text=f"MAUR hata listesi ({self.current_dataset})",
                                                font_size=sp(13), bold=True, color=TEXT,
                                                size_hint_y=None, height=dp(20), halign="left",
                                                text_size=(dp(300), None)))
                    for (r1, c1), (r2, c2), v1, v2, ratio in maur_failures:
                        n1 = point_no.get((r1, c1), "?")
                        n2 = point_no.get((r2, c2), "?")
                        line = Label(text=f"Grid No {n1} <-> {n2}    {v1} / {v2} lx    oran {ratio:.2f}",
                                     font_size=sp(12), color=(0.88, 0.6, 0.58, 1),
                                     size_hint_y=None, height=dp(18), halign="left",
                                     text_size=(dp(300), None))
                        list_card.add_widget(line)
                    list_card.bind(minimum_height=list_card.setter("height"))
                    self.content_area.add_widget(list_card)

                fail_count = len(maur_failures)
                maur_ok = fail_count <= maur_max_fail
                verdict_card = Card(bg_color=SUCCESS_TINT if maur_ok else DANGER_TINT,
                                     radius=14, border_color=SUCCESS if maur_ok else DANGER,
                                     size_hint_y=None, height=dp(50),
                                     padding=[dp(16), 0, dp(16), 0])
                verdict_row = BoxLayout()
                verdict_row.add_widget(Label(
                    text=f"Toplam hata: {fail_count} / izin verilen {maur_max_fail}",
                    font_size=sp(13), color=TEXT_MUTED, halign="left"))
                verdict_row.add_widget(Label(
                    text="UYGUN" if maur_ok else "UYGUN DEGIL",
                    font_size=sp(14), bold=True,
                    color=GREEN_TXT if maur_ok else RED_TXT))
                verdict_card.add_widget(verdict_row)
                self.content_area.add_widget(verdict_card)

        # --- Renk skalasi (legend) ---
        legend_card = Card(bg_color=CARD, radius=14, orientation="vertical",
                            size_hint_y=None, height=dp(64), padding=[dp(12), dp(8), dp(12), dp(8)],
                            spacing=dp(4))
        legend_card.add_widget(Label(text=f"{self.current_dataset}  [lx]", font_size=sp(11),
                                      color=TEXT_MUTED, size_hint_y=None, height=dp(16)))
        bar = BoxLayout(size_hint_y=None, height=dp(18), spacing=0)
        steps = 20
        for i in range(steps):
            t = i / (steps - 1)
            val = vmin + t * (vmax - vmin)
            swatch = Widget()
            with swatch.canvas:
                Color(*lux_color(val, vmin, vmax))
                swatch._rect = Rectangle(pos=swatch.pos, size=swatch.size)
            swatch.bind(pos=lambda inst, v, s=swatch: setattr(s._rect, "pos", v))
            swatch.bind(size=lambda inst, v, s=swatch: setattr(s._rect, "size", v))
            bar.add_widget(swatch)
        legend_card.add_widget(bar)
        minmax_row = BoxLayout(size_hint_y=None, height=dp(16))
        n_ticks = 5
        for i in range(n_ticks):
            t = i / (n_ticks - 1)
            tick_val = vmin + t * (vmax - vmin)
            if i == 0:
                halign = "left"
            elif i == n_ticks - 1:
                halign = "right"
            else:
                halign = "center"
            tick_lbl = Label(text=f"{tick_val:.0f}", font_size=sp(10.5), color=TEXT_MUTED,
                              halign=halign, valign="middle")
            tick_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
            minmax_row.add_widget(tick_lbl)
        legend_card.add_widget(minmax_row)
        self.content_area.add_widget(legend_card)

        # --- Ozet paneli (Relux/DIALux hesap sayfasi mantiginda) ---
        def summary_row(label, symbol, value_text):
            row = BoxLayout(size_hint_y=None, height=dp(24))
            row.add_widget(Label(text=label, font_size=sp(13), color=TEXT_MUTED,
                                  halign="left", valign="middle", size_hint_x=0.55))
            row.add_widget(Label(text=symbol, font_size=sp(13), color=TEXT_MUTED,
                                  halign="left", valign="middle", size_hint_x=0.25))
            row.add_widget(Label(text=value_text, font_size=sp(13.5), bold=True, color=TEXT,
                                  halign="right", valign="middle", size_hint_x=0.35))
            for lbl in row.children:
                lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
            return row

        def build_summary_card(title, pos_values):
            vals = list(pos_values)
            card = Card(bg_color=CARD, radius=14, orientation="vertical",
                        size_hint_y=None, padding=[dp(16), dp(12), dp(16), dp(12)],
                        spacing=dp(6))
            card.add_widget(Label(text=title, font_size=sp(16), bold=True, color=TEXT,
                                   size_hint_y=None, height=dp(24), halign="left",
                                   text_size=(dp(300), None)))
            if not vals:
                card.add_widget(Label(text="Bu bolgede henuz olcum yok.", font_size=sp(13),
                                       color=TEXT_MUTED, size_hint_y=None, height=dp(24),
                                       halign="left", text_size=(dp(300), None)))
                card.bind(minimum_height=card.setter("height"))
                return card
            avg = sum(vals) / len(vals)
            vmn = min(vals)
            vmx = max(vals)
            uo = vmn / avg if avg else 0
            ud = vmn / vmx if vmx else 0
            uo_ratio = (avg / vmn) if vmn else 0
            ud_ratio = (vmx / vmn) if vmn else 0
            card.add_widget(summary_row("Ortalama aydinlatma", "E\u0304m", f"{avg:.0f} lx"))
            card.add_widget(summary_row("Minimum aydinlatma", "Emin", f"{vmn:.0f} lx"))
            card.add_widget(summary_row("Maksimum aydinlatma", "Emax", f"{vmx:.0f} lx"))
            card.add_widget(summary_row("Duzgunluk Uo", "Emin/E\u0304m",
                                         f"1:{uo_ratio:.2f} ({uo:.2f})"))
            card.add_widget(summary_row("Cesitlilik Ud", "Emin/Emax",
                                         f"1:{ud_ratio:.2f} ({ud:.2f})"))
            card.bind(minimum_height=card.setter("height"))
            return card

        if ms.org == "FIBA":
            margin = ms.fiba_ppa_margin
            ppa_vals = [v for (r, c), v in by_pos.items()
                        if margin <= r < satir_n - margin and margin <= c < sutun_n - margin]
            tpa_vals = list(by_pos.values())
            ppa_card = build_summary_card("Ozet - PPA (Ana Oyun Alani)", ppa_vals)
            if ppa_card:
                self.content_area.add_widget(ppa_card)
            tpa_card = build_summary_card("Ozet - TPA (Toplam Oyun Alani)", tpa_vals)
            if tpa_card:
                self.content_area.add_widget(tpa_card)
            return

        summary_card = build_summary_card("Ozet", list(by_pos.values()))
        if summary_card:
            self.content_area.add_widget(summary_card)


class ReportScreen(Screen):
    """Rapor - secili FIFA/UEFA standardina gore olcum sonuclarinin karsilastirmasi."""

    def __init__(self, measure_screen, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BG)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)
        self.measure_screen = measure_screen

        self.root_box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        self.root_box.add_widget(Label(text="Rapor", font_size=sp(20), bold=True, color=TEXT,
                                        size_hint_y=None, height=dp(32)))

        self.content_area = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        self.content_area.bind(minimum_height=self.content_area.setter("height"))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.content_area)
        self.root_box.add_widget(scroll)

        self.add_widget(self.root_box)

    def _update_bg(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_pre_enter(self, *a):
        self._build_report()

    def _show_message_popup(self, title, message):
        # Uzun dosya yollari gibi BOSLUKSUZ metinler Kivy'nin kelime-bazli satir
        # sarma mantigini atlayip popup disina taşabiliyor. "/" karakterinden
        # sonra GORUNMEZ bir satir kirma firsati (zero-width space) ekleyerek
        # bunu onluyoruz - gorsel bosluk degismez, sadece sarma noktasi eklenir.
        message = message.replace("/", "/\u200b")
        content = PopupContent(padding=dp(18), spacing=dp(14))
        _popup_title_lbl = Label(text=title, font_size=sp(16), bold=True, color=TEXT,
                                 size_hint_y=None, height=dp(30), halign="left")
        _popup_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(_popup_title_lbl)
        msg_lbl = Label(text=message, font_size=sp(13.5), color=TEXT, halign="center",
                         valign="middle")
        msg_lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        content.add_widget(msg_lbl)
        popup = Popup(title="", content=content, size_hint=(0.85, 0.45),
                       auto_dismiss=True, separator_color=BORDER, title_color=TEXT,
                       background_color=(0,0,0,0), background='', separator_height=0, title_size=0)
        close_btn = FlatButton(text="Tamam", bg_color=ACCENT, font_size=sp(14),
                                size_hint_y=None, height=dp(46))
        close_btn.bind(on_release=lambda b: popup.dismiss())
        content.add_widget(close_btn)
        popup.open()

    def export_data_json(self):
        ms = self.measure_screen
        try:
            data = ms._build_session_dict()
            fname = f"aydinlatma_veri_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            fpath = os.path.join(self._export_dir(), fname)
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._save_file_with_picker(fpath, fname, "application/json", "Veri Kaydedildi")
        except Exception as e:
            self._show_message_popup("Disa Aktarma Hatasi", f"Bir sorun olustu:\n{e}")

    def _finish_import(self, data):
        ms = self.measure_screen
        try:
            ms._apply_session_dict(data)
            ms.save_session()
            self._build_report()
            self._show_message_popup("Ice Aktarildi", "Veriler basariyla yuklendi.")
        except Exception as e:
            self._show_message_popup("Ice Aktarma Hatasi", f"Veri islenemedi:\n{e}")

    def import_data_json(self):
        """Android'de yerlesik dosya secici ile bir .json yedegini geri yukler.
        Android disinda (masaustu test) basit bir dosya-yolu girisine duser."""
        try:
            from jnius import autoclass
            from android import activity as android_activity  # sadece APK icinde var
            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            REQUEST_CODE = 4242

            def on_activity_result(request_code, result_code, intent):
                if request_code != REQUEST_CODE:
                    return
                try:
                    if intent is None:
                        return
                    uri = intent.getData()
                    if uri is None:
                        return
                    resolver = activity.getContentResolver()
                    input_stream = resolver.openInputStream(uri)
                    BufferedReader = autoclass("java.io.BufferedReader")
                    InputStreamReader = autoclass("java.io.InputStreamReader")
                    reader = BufferedReader(InputStreamReader(input_stream))
                    lines = []
                    line = reader.readLine()
                    while line is not None:
                        lines.append(line)
                        line = reader.readLine()
                    reader.close()
                    content = "\n".join(lines)
                    data = json.loads(content)
                    Clock.schedule_once(lambda dt: self._finish_import(data), 0)
                except Exception as e:
                    Clock.schedule_once(lambda dt, e=e: self._show_message_popup(
                        "Ice Aktarma Hatasi", f"Dosya okunamadi:\n{e}"), 0)
                finally:
                    android_activity.unbind(on_activity_result=on_activity_result)

            android_activity.bind(on_activity_result=on_activity_result)

            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("application/json")
            activity.startActivityForResult(intent, REQUEST_CODE)
        except Exception:
            self._import_via_text_fallback()

    def _import_via_text_fallback(self):
        content = PopupContent(padding=dp(18), spacing=dp(12))
        title = Label(text="Dosyadan Ice Aktar", font_size=sp(16), bold=True, color=TEXT,
                      size_hint_y=None, height=dp(28))
        content.add_widget(title)
        info = Label(text="Dosya yolunu girin:", font_size=sp(12), color=TEXT_MUTED,
                     size_hint_y=None, height=dp(20), halign="left")
        info.bind(size=lambda i, v: setattr(i, "text_size", v))
        content.add_widget(info)
        fc = Card(bg_color=CARD_LIGHT, radius=8, size_hint_y=None, height=dp(40))
        ti = ThemedTextInput(text="", multiline=False, font_size=sp(12.5))
        fc.add_widget(ti)
        content.add_widget(fc)

        popup = Popup(title="", content=content, size_hint=(0.9, None), height=dp(220),
                       auto_dismiss=True, background_color=(0, 0, 0, 0), background='',
                       separator_height=0, title_size=0)

        def do_import(*a):
            path = ti.text.strip()
            popup.dismiss()
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._finish_import(data)
            except Exception as e:
                self._show_message_popup("Ice Aktarma Hatasi", f"Dosya okunamadi:\n{e}")

        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        cancel_btn = FlatButton(text="Vazgec", bg_color=CARD_LIGHT, font_size=sp(13))
        cancel_btn.bind(on_release=lambda b: popup.dismiss())
        ok_btn = FlatButton(text="Yukle", bg_color=SUCCESS, font_size=sp(13), bold=True)
        ok_btn.bind(on_release=do_import)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(ok_btn)
        content.add_widget(btn_row)
        popup.open()

    def _toggle_report_language(self):
        ms = self.measure_screen
        ms.report_language = "en" if ms.report_language == "tr" else "tr"
        self.lang_btn.text = "Turkce" if ms.report_language == "tr" else "English"
        ms.save_session()

    def _open_fifa_info_popup(self):
        ms = self.measure_screen
        content = PopupContent(padding=dp(16), spacing=dp(10))
        title = Label(text="Ek Rapor Bilgileri", font_size=sp(17), bold=True, color=TEXT,
                       size_hint_y=None, height=dp(28))
        content.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1))
        form = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(10),
                          padding=[0, dp(4), 0, dp(4)])
        form.bind(minimum_height=form.setter("height"))

        inputs = {}

        def section(text):
            lbl = Label(text=text, font_size=sp(12), bold=True, color=ACCENT,
                        size_hint_y=None, height=dp(24), halign="left", valign="middle")
            lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
            form.add_widget(lbl)

        def field(label_text, key):
            lbl = Label(text=label_text, font_size=sp(12), color=TEXT_MUTED,
                        size_hint_y=None, height=dp(18), halign="left", valign="bottom")
            lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
            form.add_widget(lbl)
            fc = Card(bg_color=CARD_LIGHT, radius=8, size_hint_y=None, height=dp(40))
            ti = ThemedTextInput(text=ms.fifa_info.get(key, ""), multiline=False, font_size=sp(13))
            inputs[key] = ti

            def on_focus(instance, is_focused, fc=fc):
                if is_focused:
                    self._focused_popup_field = fc
                    # klavye zaten aciksa (baska bir alandan gecildiyse) hemen kaydir;
                    # degilse asagidaki on_keyboard_height olayi acilinca kaydiracak
                    Clock.schedule_once(lambda dt: scroll.scroll_to(fc, padding=dp(24)), 0.05)

            ti.bind(focus=on_focus)
            fc.add_widget(ti)
            form.add_widget(fc)

        def readonly_row(label_text, value_text):
            lbl = Label(text=label_text, font_size=sp(12), color=TEXT_MUTED,
                        size_hint_y=None, height=dp(18), halign="left", valign="bottom")
            lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
            form.add_widget(lbl)
            val = Label(text=value_text, font_size=sp(12.5), color=TEXT, bold=True,
                        size_hint_y=None, halign="left", valign="top")
            val.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
            val.bind(texture_size=lambda i, ts: setattr(i, "height", ts[1] + dp(4)))
            form.add_widget(val)

        section("GENEL")
        field("Saha Genisligi (m)", "pitch_width")
        field("Saha Uzunlugu (m)", "pitch_length")

        section("LUMINAIRE")
        field("Uretici", "lum1_manufacturer")
        field("Model", "lum1_model")

        section("OLCUM CIHAZI")
        field("Cihaz", "meter_model")
        field("Seri No", "meter_serial")
        field("Alici Kafa No.0 Seri No", "probe_serial_eh")
        field("Alici Kafa No.1 Seri No", "probe_serial_ev0")
        field("Alici Kafa No.2 Seri No", "probe_serial_ev90")
        field("Alici Kafa No.3 Seri No", "probe_serial_ev180")
        field("Alici Kafa No.4 Seri No", "probe_serial_ev270")
        field("Kalibrasyon Tarihi", "cal_date")

        section("RENK OLCER (varsa)")
        field("Kullanilan Cihaz", "colour_meter")
        field("Seri No", "colour_meter_serial")
        field("Kalibrasyon Tarihi", "colour_meter_cal_date")

        section("KURULUS BILGILERI")
        field("Kurulus", "org_name")
        field("Adres", "org_address")
        field("Telefon / E-posta", "org_phone_email")
        field("Denetleyen", "inspector_name")

        section("EK OLCUMLER (varsa)")
        field("Ort. Flicker Faktoru", "flicker_avg")
        field("Maks. Flicker Faktoru", "flicker_max")
        field("Renk Sicakligi (Tc)", "colour_temp_tc")
        field("Renk Gosterimi (Ra)", "colour_rendering_ra")
        field("Kamasma Orani (Rg)", "glare_rating_rg")

        scroll.add_widget(form)
        content.add_widget(scroll)

        popup = Popup(title="", content=content, size_hint=(0.92, 0.85),
                       auto_dismiss=False, background_color=(0, 0, 0, 0), background='',
                       separator_height=0, title_size=0)

        from kivy.core.window import Window as _KbWin
        self._focused_popup_field = None

        def _on_keyboard_height(instance, height):
            # Klavye acilma/kapanma ANIMASYONU tam bittiginde bu kesin olarak
            # tetiklenir (sabit bir sure tahmin etmekten cok daha guvenilir) -
            # o anda odakli alani tekrar gorunur konuma kaydiralim.
            field = getattr(self, "_focused_popup_field", None)
            if field is not None and height > 0:
                Clock.schedule_once(lambda dt: scroll.scroll_to(field, padding=dp(24)), 0.02)

        _KbWin.bind(on_keyboard_height=_on_keyboard_height)

        def _cleanup_keyboard_binding(*a):
            _KbWin.unbind(on_keyboard_height=_on_keyboard_height)

        popup.bind(on_dismiss=_cleanup_keyboard_binding)

        def do_save(*a):
            for key, ti in inputs.items():
                ms.fifa_info[key] = ti.text.strip()
            ms.save_session()
            popup.dismiss()

        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        cancel_btn = FlatButton(text="Vazgec", bg_color=CARD_LIGHT, font_size=sp(13))
        cancel_btn.bind(on_release=lambda b: popup.dismiss())
        save_btn = FlatButton(text="Kaydet", bg_color=SUCCESS, font_size=sp(13), bold=True)
        save_btn.bind(on_release=do_save)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(save_btn)
        content.add_widget(btn_row)

        popup.open()

    def _export_dir(self):
        """Gecici (herkese acik olmayan) calisma klasoru - dosya once buraya
        yazilir, sonra _save_file_with_picker() ile kullanicinin sectigi konuma kaydedilir."""
        try:
            app = App.get_running_app()
            path = app.user_data_dir
        except Exception:
            path = "."
        return path

    def _save_file_with_picker(self, temp_path, filename, mime_type, success_title="Kaydedildi"):
        """Android'in yerlesik 'Farkli Kaydet' dosya secicisini acar - kullanici
        dosyayi telefonunda ISTEDIGI konuma (Indirilenler, Belgeler, Google
        Drive, SD kart vb.) kaydedebilir. Android disinda (masaustu/test
        ortaminda) dosya zaten _export_dir'de durur, sadece bilgi mesaji gosterilir."""
        try:
            from jnius import autoclass
            from android import activity as android_activity
            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity
            REQUEST_CODE = 4243

            def on_activity_result(request_code, result_code, intent):
                if request_code != REQUEST_CODE:
                    return
                try:
                    if intent is None:
                        return  # kullanici "Farkli Kaydet" penceresini iptal etti
                    uri = intent.getData()
                    if uri is None:
                        return
                    resolver = activity.getContentResolver()
                    out_stream = resolver.openOutputStream(uri)
                    with open(temp_path, "rb") as f:
                        file_bytes = f.read()
                    out_stream.write(file_bytes)
                    out_stream.close()
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
                    Clock.schedule_once(lambda dt: self._show_message_popup(
                        success_title, f"'{filename}' secilen konuma kaydedildi."), 0)
                except Exception as e:
                    Clock.schedule_once(lambda dt, e=e: self._show_message_popup(
                        "Kaydetme Hatasi", f"Dosya kaydedilemedi:\n{e}"), 0)
                finally:
                    android_activity.unbind(on_activity_result=on_activity_result)

            android_activity.bind(on_activity_result=on_activity_result)

            intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType(mime_type)
            intent.putExtra(Intent.EXTRA_TITLE, filename)
            activity.startActivityForResult(intent, REQUEST_CODE)
        except Exception:
            # Android disinda (masaustu/test ortami) - eski davranisa don,
            # dosya zaten calisma klasorunde duruyor
            self._show_message_popup(
                success_title,
                f"Dosya kaydedildi:\n{filename}\n(bilgisayar/test ortaminda - "
                "uygulamanin calisma klasorunde)")

    def _export_pdf_fiba(self):
        ms = self.measure_screen
        data = self._compute_fiba_report_data()
        if not data:
            self._show_message_popup("PDF", "Once olcum girin, sonra rapor disa aktarilabilir.")
            return
        try:
            from fpdf import FPDF
        except Exception as e:
            self._show_message_popup(
                "PDF Kutuphanesi Sorunu",
                f"'fpdf2' kutuphanesi yuklenemedi.\n\nTeknik detay:\n{type(e).__name__}: {e}")
            return

        BRAND = (41, 82, 130)
        BRAND_TINT = (219, 229, 241)
        GOOD = (20, 130, 60)
        BAD = (180, 30, 30)
        MUTED = (120, 120, 128)

        class BrandedPDF(FPDF):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                self.header_title = ""
                self.suppress_header = False
                self.base_font = "Helvetica"

            def header(self):
                if self.suppress_header:
                    return
                self.set_fill_color(*BRAND)
                self.rect(0, 0, self.w, 10, style="F")
                self.set_text_color(255, 255, 255)
                self.set_font(self.base_font, "B", 8.5)
                self.set_xy(10, 2.6)
                self.cell(0, 5, self.header_title, align="L")
                self.set_text_color(0, 0, 0)
                self.set_y(15)

            def footer(self):
                if self.page_no() == 1:
                    return
                self.set_y(-12)
                self.set_font(self.base_font, "", 8)
                self.set_text_color(*MUTED)
                self.cell(0, 8, f"Sayfa {self.page_no()}", align="C")
                self.set_text_color(0, 0, 0)

        try:
            pdf = BrandedPDF(orientation="P", unit="mm", format="A4")
            FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
            font_regular = os.path.join(FONT_DIR, "DejaVuSans.ttf")
            font_bold = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
            font_italic = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")
            try:
                if os.path.exists(font_regular) and os.path.exists(font_bold):
                    pdf.add_font("DejaVu", "", font_regular)
                    pdf.add_font("DejaVu", "B", font_bold)
                    pdf.add_font("DejaVu", "I", font_italic if os.path.exists(font_italic) else font_regular)
                    BASE_FONT = "DejaVu"
                else:
                    BASE_FONT = "Helvetica"
            except Exception:
                BASE_FONT = "Helvetica"
            pdf.base_font = BASE_FONT

            proj = data["project_info"]
            pdf.header_title = proj.get("name") or "Aydinlatma Olcum Raporu (FIBA)"

            # ============================================================
            # SAYFA 1: KAPAK SAYFASI
            # ============================================================
            pdf.suppress_header = True
            pdf.add_page()
            pdf.set_fill_color(*BRAND)
            pdf.rect(0, 0, pdf.w, 7, style="F")
            pdf.rect(0, pdf.h - 7, pdf.w, 7, style="F")
            try:
                pdf.image("/mnt/user-data/outputs/app_icon_print.png",
                          x=pdf.w / 2 - 18, y=30, w=36, h=36)
            except Exception:
                pass
            pdf.set_y(78)
            pdf.set_font(BASE_FONT, "B", 21)
            pdf.set_text_color(25, 28, 33)
            pdf.cell(0, 11, "AYDINLATMA OLCUM RAPORU", align="C", ln=True)
            pdf.set_font(BASE_FONT, "", 11)
            pdf.set_text_color(120, 120, 128)
            pdf.cell(0, 7, "FIBA Basketbol Sahasi Aydinlatma Standardi", align="C", ln=True)
            pdf.ln(10)
            pdf.set_draw_color(*BRAND)
            pdf.set_line_width(0.6)
            y_line = pdf.get_y()
            pdf.line(pdf.w / 2 - 30, y_line, pdf.w / 2 + 30, y_line)
            pdf.set_draw_color(0, 0, 0)
            pdf.ln(10)
            pdf.set_font(BASE_FONT, "B", 18)
            pdf.set_text_color(20, 22, 26)
            pdf.multi_cell(0, 9, proj.get("name") or "-", align="C")
            pdf.set_x(pdf.l_margin)
            pdf.set_font(BASE_FONT, "", 12)
            pdf.set_text_color(90, 90, 98)
            pdf.cell(0, 7, proj.get("location") or "-", align="C", ln=True)
            pdf.ln(6)
            pdf.set_font(BASE_FONT, "", 10.5)
            pdf.set_text_color(70, 70, 78)
            pdf.cell(0, 6, f"Olcum Tarihi: {proj.get('date') or '-'}", align="C", ln=True)
            pdf.cell(0, 6, "Karsilastirilan Standart: FIBA", align="C", ln=True)
            pdf.cell(0, 6, f"Hazirlayan: {proj.get('prepared_by') or '-'}", align="C", ln=True)
            pdf.set_y(-30)
            pdf.set_font(BASE_FONT, "", 9)
            pdf.set_text_color(*MUTED)
            pdf.cell(0, 5, data["fifa_info"].get("org_name", ORG_NAME), align="C", ln=True)
            pdf.cell(0, 5, f"Rapor olusturma tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                     align="C", ln=True)
            pdf.set_text_color(0, 0, 0)

            # ============================================================
            # SAYFA 2+: PPA / TPA SONUC TABLOLARI
            # ============================================================
            pdf.suppress_header = False
            pdf.add_page()
            pdf.set_font(BASE_FONT, "B", 16)
            pdf.set_text_color(*BRAND)
            pdf.cell(0, 10, "FIBA UYGUNLUK RAPORU", ln=True, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
            pdf.set_font(BASE_FONT, "", 10)
            pdf.cell(0, 6, f"Salon/Tesis: {proj.get('name') or '-'}", ln=True)
            pdf.cell(0, 6, f"Ulke / Sehir: {proj.get('location') or '-'}", ln=True)
            pdf.cell(0, 6, f"Olcum Tarihi: {proj.get('date') or '-'}", ln=True)
            pdf.cell(0, 6, f"Izgara: {data['rows_count']} x {data['cols_count']}   "
                           f"Olculen: {data['measured_count']}/{data['total_points']}", ln=True)
            pdf.ln(3)

            verdict_ok = data["all_pass"]
            pdf.set_fill_color(224, 242, 228) if verdict_ok else pdf.set_fill_color(250, 226, 226)
            pdf.set_draw_color(*(GOOD if verdict_ok else BAD))
            pdf.set_line_width(0.4)
            vy = pdf.get_y()
            pdf.rect(10, vy, pdf.w - 20, 10, style="DF")
            pdf.set_xy(10, vy + 1.5)
            pdf.set_font(BASE_FONT, "B", 12)
            pdf.set_text_color(*(GOOD if verdict_ok else BAD))
            pdf.cell(pdf.w - 20, 7, "KRITERLERI KARSILIYOR" if verdict_ok else "KRITERLERI KARSILAMIYOR",
                     align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.2)
            pdf.set_y(vy + 13)

            zone_titles = {"PPA": "PPA - Ana Oyun Alani (19 x 32m)",
                           "TPA": "TPA - Toplam Oyun Alani (22 x 35m)"}
            for zone_name in ["PPA", "TPA"]:
                zone = data["zones"].get(zone_name)
                if zone is None:
                    continue
                if pdf.get_y() > 220:
                    pdf.add_page()
                pdf.set_font(BASE_FONT, "B", 12)
                pdf.set_fill_color(*BRAND_TINT)
                pdf.set_text_color(*BRAND)
                zone_ok = zone["zone_ok"]
                pdf.cell(0, 8, f"{zone_titles[zone_name]}  -  "
                               f"{'UYGUN' if zone_ok else 'UYGUN DEGIL'}", border=1, fill=True, ln=True)
                pdf.set_text_color(0, 0, 0)

                col_w = [68, 32, 32, 40]
                pdf.set_font(BASE_FONT, "B", 9)
                pdf.set_fill_color(240, 240, 244)
                for w, h in zip(col_w, ["Kriter", "Referans", "Olculen", "Sonuc"]):
                    pdf.cell(w, 6, h, border=1, fill=True, align="C")
                pdf.ln()
                pdf.set_font(BASE_FONT, "", 9)

                th = FIBA_STANDARDS[zone_name]

                def crit_pdf_row(label, ref_str, val_str, ok):
                    if pdf.get_y() > 275:
                        pdf.add_page()
                    pdf.cell(col_w[0], 6, label, border=1)
                    pdf.cell(col_w[1], 6, ref_str, border=1, align="C")
                    pdf.cell(col_w[2], 6, val_str, border=1, align="C")
                    pdf.set_text_color(*GOOD) if ok else pdf.set_text_color(*BAD)
                    pdf.cell(col_w[3], 6, "UYGUN" if ok else "UYGUN DEGIL", border=1, align="C")
                    pdf.set_text_color(0, 0, 0)
                    pdf.ln()

                ec = zone["EC"]
                if ec["avg"] is not None:
                    crit_pdf_row("EC Ortalama >", f"{th['ec_avg']}", f"{ec['avg']:.0f}",
                                 ec["avg"] >= th["ec_avg"])
                    crit_pdf_row("EC Duzgunluk U1 >=", f"{th['ec_u1']:.2f}", f"{ec['u1']:.2f}",
                                 ec["u1"] >= th["ec_u1"])
                    crit_pdf_row("EC Duzgunluk U2 >=", f"{th['ec_u2']:.2f}", f"{ec['u2']:.2f}",
                                 ec["u2"] >= th["ec_u2"])
                else:
                    crit_pdf_row("EC", f">={th['ec_avg']}", f"Olculmedi (0/{ec['total_count']})", False)

                for d_name, d_res in zone["EV"]["per_direction"].items():
                    crit_pdf_row(f"EV {d_name} Ortalama >", f"{th['ev_avg']}", f"{d_res['avg']:.0f}",
                                 d_res["avg"] >= th["ev_avg"])
                    crit_pdf_row(f"EV {d_name} Duzgunluk U1 >=", f"{th['ev_u1']:.2f}",
                                 f"{d_res['u1']:.2f}", d_res["u1"] >= th["ev_u1"])
                    crit_pdf_row(f"EV {d_name} Duzgunluk U2 >=", f"{th['ev_u2']:.2f}",
                                 f"{d_res['u2']:.2f}", d_res["u2"] >= th["ev_u2"])
                crit_pdf_row("EV Yon Dengesi (min/maks) >=", f"{th['ev_dir_ratio']:.2f}",
                             f"{zone['EV']['dir_ratio']:.2f}", zone["EV"]["dir_ratio_ok"])

                eh = zone["EH"]
                if eh["avg"] is not None:
                    crit_pdf_row("EH Ortalama (aralik)", f"{th['eh_avg_min']}-{th['eh_avg_max']}",
                                 f"{eh['avg']:.0f}", eh["avg_ok"])
                    crit_pdf_row("EH Duzgunluk U1 >=", f"{th['eh_u1']:.2f}", f"{eh['u1']:.2f}",
                                 eh["u1"] >= th["eh_u1"])
                    crit_pdf_row("EH Duzgunluk U2 >=", f"{th['eh_u2']:.2f}", f"{eh['u2']:.2f}",
                                 eh["u2"] >= th["eh_u2"])
                else:
                    crit_pdf_row("EH", f"{th['eh_avg_min']}-{th['eh_avg_max']}",
                                 f"Olculmedi (0/{eh['total_count']})", False)
                pdf.ln(6)

            # ============================================================
            # ISIK KAYNAGI (Tablo 6): Flicker / CRI / Renk Sicakligi
            # ============================================================
            fifa = data["fifa_info"]
            if pdf.get_y() > 250:
                pdf.add_page()
            pdf.set_font(BASE_FONT, "B", 12)
            pdf.set_fill_color(*BRAND_TINT)
            pdf.set_text_color(*BRAND)
            pdf.cell(0, 8, "Isik Kaynagi (Tablo 6)", border=1, fill=True, ln=True)
            pdf.set_text_color(0, 0, 0)
            col_w_ls = [68, 32, 32, 40]
            pdf.set_font(BASE_FONT, "B", 9)
            pdf.set_fill_color(240, 240, 244)
            for w, h in zip(col_w_ls, ["Kriter", "Referans", "Girilen Deger", ""]):
                pdf.cell(w, 6, h, border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_font(BASE_FONT, "", 9)
            for label, ref, key in [("Flicker Faktoru", "<=%1", "flicker_avg"),
                                     ("Renk Gosterimi (CRI)", ">=80", "colour_rendering_ra"),
                                     ("Renk Sicakligi", "4000-6000K", "colour_temp_tc")]:
                pdf.cell(col_w_ls[0], 6, label, border=1)
                pdf.cell(col_w_ls[1], 6, ref, border=1, align="C")
                pdf.cell(col_w_ls[2], 6, fifa.get(key) or "-", border=1, align="C")
                pdf.cell(col_w_ls[3], 6, "", border=1)
                pdf.ln()
            pdf.ln(4)

            # ============================================================
            # HAM OLCUM VERILERI (EC dahil)
            # ============================================================
            raw_seq = data["raw_sequence"]
            raw_meas = data["raw_measurements"]
            pdf.add_page()
            pdf.set_font(BASE_FONT, "B", 14)
            pdf.set_text_color(*BRAND)
            pdf.cell(0, 10, "Ham Olcum Verileri", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
            fiba_cols = [t for t, _ in PROBES] + ["EC"]
            headers_raw = ["Grid No"] + fiba_cols
            col_w_raw = [18, 27, 27, 27, 27, 27, 27]

            def raw_header_row():
                pdf.set_font(BASE_FONT, "B", 8.5)
                pdf.set_fill_color(*BRAND)
                pdf.set_text_color(255, 255, 255)
                for w, h in zip(col_w_raw, headers_raw):
                    pdf.cell(w, 7, h, border=1, fill=True, align="C")
                pdf.ln()
                pdf.set_text_color(0, 0, 0)

            raw_header_row()
            pdf.set_font(BASE_FONT, "", 8.5)
            row_i = 0
            for idx in range(len(raw_seq)):
                d = raw_meas.get(idx)
                if d is None:
                    continue
                if pdf.get_y() > 270:
                    pdf.add_page()
                    raw_header_row()
                    pdf.set_font(BASE_FONT, "", 8.5)
                pdf.set_fill_color(*(BRAND_TINT if row_i % 2 == 0 else (255, 255, 255)))
                pdf.cell(col_w_raw[0], 6, str(idx + 1), border=1, align="C", fill=True)
                for w, title in zip(col_w_raw[1:], fiba_cols):
                    val = d["values"].get(title)
                    pdf.cell(w, 6, f"{val}" if val is not None else "-", border=1, align="C", fill=True)
                pdf.ln()
                row_i += 1

            # ============================================================
            # ISI HARITALARI (Eh, Ev0-270, EC - 6 sayfa)
            # ============================================================
            rows_n = data["rows_count"]
            cols_n = data["cols_count"]
            for title in fiba_cols:
                grid = self._dataset_grid(raw_meas, rows_n, cols_n, title)
                vals = [v for row_vals in grid for v in row_vals if v is not None]
                if not vals:
                    continue
                vmin_g, vmax_g = min(vals), max(vals)
                pdf.add_page()
                pdf.set_font(BASE_FONT, "B", 14)
                pdf.set_text_color(*BRAND)
                heat_title = "Kamera (EC)" if title == "EC" else title
                pdf.cell(0, 10, f"Isi Haritasi - {heat_title}", ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)

                avail_w = 190
                cell_w = min(avail_w / rows_n, 16)
                cell_h = min(200 / cols_n, 11)
                start_x = pdf.get_x()
                start_y = pdf.get_y()
                for c_idx, row_vals in enumerate(grid):
                    for r_idx, val in enumerate(row_vals):
                        x = start_x + r_idx * cell_w
                        y = start_y + c_idx * cell_h
                        if val is None:
                            pdf.set_fill_color(230, 230, 230)
                            pdf.set_draw_color(255, 255, 255)
                            pdf.rect(x, y, cell_w, cell_h, style="DF")
                            continue
                        rgba = lux_color(val, vmin_g, vmax_g)
                        pdf.set_fill_color(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255))
                        pdf.set_draw_color(255, 255, 255)
                        pdf.rect(x, y, cell_w, cell_h, style="DF")
                        txt_rgba = text_color_for_bg(rgba)
                        pdf.set_text_color(int(txt_rgba[0]*255), int(txt_rgba[1]*255), int(txt_rgba[2]*255))
                        pdf.set_xy(x, y + cell_h / 2 - 1.6)
                        pdf.set_font(BASE_FONT, "B", 5.5)
                        pdf.cell(cell_w, 3.2, f"{val:.0f}", align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.set_draw_color(0, 0, 0)

                # --- PPA sinirini kalin mavi cerceveyle goster (uygulamadaki ile ayni) ---
                margin = data["ppa_margin"]
                ppa_x0 = start_x + margin * cell_w
                ppa_y0 = start_y + margin * cell_h
                ppa_w = rows_n * cell_w - 2 * margin * cell_w
                ppa_h = cols_n * cell_h - 2 * margin * cell_h
                if ppa_w > 0 and ppa_h > 0:
                    pdf.set_draw_color(*BRAND)
                    pdf.set_line_width(0.9)
                    pdf.rect(ppa_x0, ppa_y0, ppa_w, ppa_h, style="D")
                    pdf.set_draw_color(0, 0, 0)
                    pdf.set_line_width(0.2)
                pdf.set_font(BASE_FONT, "I", 8)
                pdf.set_text_color(*MUTED)
                pdf.set_xy(start_x, start_y + cols_n * cell_h + 1)
                pdf.cell(0, 4, "Mavi cerceve = PPA siniri (disi = TPA)", align="L")
                pdf.set_text_color(0, 0, 0)

                legend_y = start_y + cols_n * cell_h + 11
                legend_w = min(avail_w, rows_n * cell_w)
                steps = 50
                seg_w = legend_w / steps
                for i in range(steps):
                    tt = i / (steps - 1)
                    color = lux_color(vmin_g + tt * (vmax_g - vmin_g), vmin_g, vmax_g)
                    pdf.set_fill_color(int(color[0]*255), int(color[1]*255), int(color[2]*255))
                    pdf.rect(start_x + i * seg_w, legend_y, seg_w + 0.4, 5, style="F")
                pdf.set_draw_color(180, 180, 180)
                pdf.rect(start_x, legend_y, legend_w, 5, style="D")
                pdf.set_draw_color(0, 0, 0)
                pdf.set_font(BASE_FONT, "", 8)
                pdf.set_text_color(100, 100, 105)
                for i in range(5):
                    tt = i / 4
                    val_tick = vmin_g + tt * (vmax_g - vmin_g)
                    tx = start_x + tt * legend_w
                    pdf.set_xy(tx - 10, legend_y + 6)
                    align = "L" if i == 0 else ("R" if i == 4 else "C")
                    pdf.cell(20, 5, f"{val_tick:.0f}", align=align)
                pdf.set_text_color(0, 0, 0)

                # --- PPA / TPA icin ayri ayri Ortalama/Min/Maks/Duzgunluk ozeti ---
                def stats_for(zone_name, dataset_title):
                    zone = data["zones"].get(zone_name)
                    if zone is None:
                        return None
                    if dataset_title == "Eh":
                        s = zone["EH"]
                    elif dataset_title == "EC":
                        s = zone["EC"]
                    else:
                        s = zone["EV"]["per_direction"].get(dataset_title)
                    if s is None or s.get("avg") is None:
                        return None
                    return s

                table_y = legend_y + 14
                pdf.set_xy(start_x, table_y)
                col_w_s = [22, 32, 26, 26, 26, 26]
                pdf.set_font(BASE_FONT, "B", 9)
                pdf.set_fill_color(*BRAND_TINT)
                for w, h in zip(col_w_s, ["Bolge", "Ortalama", "Minimum", "Maksimum", "U1", "U2"]):
                    pdf.cell(w, 7, h, border=1, fill=True, align="C")
                pdf.ln()
                pdf.set_font(BASE_FONT, "", 9)
                for zone_name, zone_label in [("PPA", "PPA"), ("TPA", "TPA")]:
                    pdf.set_x(start_x)
                    s = stats_for(zone_name, title)
                    pdf.set_font(BASE_FONT, "B", 9)
                    pdf.cell(col_w_s[0], 7, zone_label, border=1, align="C")
                    pdf.set_font(BASE_FONT, "", 9)
                    if s is None:
                        pdf.cell(sum(col_w_s[1:]), 7, "Olculmedi", border=1, align="C")
                    else:
                        pdf.cell(col_w_s[1], 7, f"{s['avg']:.0f}", border=1, align="C")
                        pdf.cell(col_w_s[2], 7, f"{s['min']:.0f}", border=1, align="C")
                        pdf.cell(col_w_s[3], 7, f"{s['max']:.0f}", border=1, align="C")
                        pdf.cell(col_w_s[4], 7, f"{s['u1']:.2f}", border=1, align="C")
                        pdf.cell(col_w_s[5], 7, f"{s['u2']:.2f}", border=1, align="C")
                    pdf.ln()

            fname = f"aydinlatma_raporu_FIBA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            fpath = os.path.join(self._export_dir(), fname)
            pdf.output(fpath)
            self._save_file_with_picker(fpath, fname, "application/pdf", "PDF Kaydedildi")
        except Exception as e:
            self._show_message_popup("PDF Hatasi", f"PDF olusturulurken bir sorun olustu:\n{e}")

    def export_pdf(self):
        ms = self.measure_screen
        if ms.org == "FIBA":
            self._export_pdf_fiba()
            return
        data = self._compute_report_data()
        if not data:
            self._show_message_popup("PDF", "Once olcum girin, sonra rapor disa aktarilabilir.")
            return
        try:
            from fpdf import FPDF
        except Exception as e:
            self._show_message_popup(
                "PDF Kutuphanesi Sorunu",
                f"'fpdf2' kutuphanesi yuklenemedi.\n\nTeknik detay:\n{type(e).__name__}: {e}")
            return

        lang = self.measure_screen.report_language if hasattr(self.measure_screen, "report_language") else "tr"

        TXT = {
            "cover_title": ("AYDINLATMA \u00d6L\u00c7\u00dcM RAPORU", "ILLUMINANCE MEASUREMENT REPORT"),
            "cover_subtitle": ("Ayd\u0131nlatma \u00d6l\u00e7\u00fcm Raporu", "Illuminance Measurement Report"),
            "date_label": ("\u00d6l\u00e7\u00fcm Tarihi", "Measurement Date"),
            "standard_label": ("Kar\u015f\u0131la\u015ft\u0131r\u0131lan Standart", "Standard Compared"),
            "prepared_by_label": ("Haz\u0131rlayan", "Prepared By"),
            "report_created": ("Rapor olu\u015fturma tarihi", "Report generated on"),
            "fifa_cover_title": ("Aydınlatma Test Raporu", "Lighting Test Report"),
            "fifa_summary_title": ("Lighting - Sonu\u00e7 \u00d6zeti", "Lighting - Summary of Results"),
            "name_of_stadium": ("Stadyum Ad\u0131", "Name of Stadium"),
            "city_location": ("\u015eehir / Konum", "City / Location"),
            "date_of_inspection": ("Denetim Tarihi", "Date of Inspection"),
            "luminaire": ("Ayd\u0131nlatma Armat\u00fcr\u00fc", "Luminaire"),
            "manufacturer": ("\u00dcretici", "Manufacturer"),
            "model_product_type": ("Model / \u00dcr\u00fcn Tipi", "Model / Product Type"),
            "illuminance_meter_used": ("Kullan\u0131lan Ayd\u0131nl\u0131k \u015eiddeti \u00d6l\u00e7er", "Illuminance Meter Used"),
            "serial_illuminance_meter": ("\u00d6l\u00e7er Seri No", "Serial Number of Illuminance Meter"),
            "calibration_date": ("Kalibrasyon Tarihi", "Calibration Date"),
            "probe_serial": ("Al\u0131c\u0131 Kafa No.{n} Seri No", "Probe Head No.{n} Serial No"),
            "colour_meter_used": ("Kullan\u0131lan Renk \u00d6l\u00e7er", "Colour Meter Used"),
            "serial_colour_meter": ("Renk \u00d6l\u00e7er Seri No", "Serial Number of Colour Meter"),
            "pitch_measurements": ("Saha \u00d6l\u00e7\u00fcleri", "Pitch Measurements"),
            "width": ("(geni\u015flik)", "(width)"),
            "length": ("(uzunluk)", "(length)"),
            "organisation_inspecting": ("Denetleyen Kurulu\u015f", "Organisation Inspecting"),
            "address": ("Adres", "Address"),
            "telephone_email": ("Telefon Numaras\u0131 ve E-posta Adresi", "Telephone Number & Email Address"),
            "inspection_by": ("Denetleyen (Ad)", "Inspection By (Name)"),
            "signature": ("\u0130mza", "Signature"),
            "stadium_name_location": ("Stadyum Ad\u0131 ve Konumu", "Stadium Name & Location"),
            "test_date": ("Test Tarihi", "Test Date"),
            "vertical_plane": ("Dikey Referans D\u00fczlemi", "Vertical Reference Plane"),
            "horizontal_plane": ("Yatay D\u00fczlem", "Horizontal Plane"),
            "ev_min": ("Ev min", "Ev min"),
            "ev_max": ("Ev maks", "Ev max"),
            "ev_ave": ("Ev ort", "Ev ave"),
            "uniformity_u1v": ("D\u00fczg\u00fcnl\u00fck U1v", "Uniformity U1v"),
            "uniformity_u2v": ("D\u00fczg\u00fcnl\u00fck U2v", "Uniformity U2v"),
            "maur_fails": ("MAUR hata say\u0131s\u0131", "MAUR fails"),
            "eh_min": ("Eh min", "Eh min"),
            "eh_max": ("Eh maks", "Eh max"),
            "eh_ave": ("Eh ort", "Eh ave"),
            "uniformity_u1h": ("D\u00fczg\u00fcnl\u00fck U1h", "Uniformity U1h"),
            "uniformity_u2h": ("D\u00fczg\u00fcnl\u00fck U2h", "Uniformity U2h"),
            "maur_horizontal_fails": ("MAUR yatay hata say\u0131s\u0131", "MAUR horizontal fails"),
            "other_measurements": ("Di\u011fer \u00d6l\u00e7\u00fcmler", "Other Measurements"),
            "avg_flicker": ("Ortalama Flicker Fakt\u00f6r\u00fc", "Average Flicker Factor"),
            "max_flicker": ("Maksimum Flicker Fakt\u00f6r\u00fc", "Maximum Flicker Factor"),
            "colour_temp": ("Renk S\u0131cakl\u0131\u011f\u0131 (Tc)", "Colour Temperature (Tc)"),
            "colour_rendering": ("Renk G\u00f6sterimi (Ra)", "Colour Rendering (Ra)"),
            "glare_rating": ("Kama\u015fma Oran\u0131 (Rg)", "Glare Rating (Rg)"),
            "detailed_report_title": ("DETAYLI UYGUNLUK RAPORU", "DETAILED COMPLIANCE REPORT"),
            "facility": ("Stadyum/Tesis", "Stadium/Facility"),
            "country_city": ("\u00dclke / \u015eehir", "Country / City"),
            "grid": ("Izgara", "Grid"),
            "measured": ("\u00d6l\u00e7\u00fclen", "Measured"),
            "meets_criteria": ("KR\u0130TERLER\u0130 KAR\u015eILIYOR", "MEETS CRITERIA"),
            "fails_criteria": ("KR\u0130TERLER\u0130 KAR\u015eILAMIYOR", "DOES NOT MEET CRITERIA"),
            "criterion": ("Kriter", "Criterion"),
            "reference": ("Referans", "Reference"),
            "measured_col": ("\u00d6l\u00e7\u00fclen", "Measured"),
            "result": ("Sonu\u00e7", "Result"),
            "compliant": ("UYGUN", "COMPLIANT"),
            "non_compliant": ("UYGUN DE\u011e\u0130L", "NON-COMPLIANT"),
            "avg_gt": ("Ortalama >", "Average >"),
            "min_gt": ("Minimum >", "Minimum >"),
            "uniformity_u1": ("D\u00fczg\u00fcnl\u00fck U1", "Uniformity U1"),
            "uniformity_u2": ("D\u00fczg\u00fcnl\u00fck U2", "Uniformity U2"),
            "horizontal_eh": ("Yatay (Eh)", "Horizontal (Eh)"),
            "vertical_deg": ("Dikey {deg}", "Vertical {deg}"),
            "maur_title": ("MAUR - Kom\u015fu Nokta D\u00fczg\u00fcnl\u00fc\u011f\u00fc", "MAUR - Adjacent Point Uniformity"),
            "maur_not_specified": ("Bu standart seviyesi i\u00e7in MAUR belirtilmemi\u015f.",
                                   "MAUR is not specified for this standard level."),
            "threshold_ratio": ("E\u015fik oran", "Threshold ratio"),
            "total_fails": ("Toplam hata (5 d\u00fczlem)", "Total fails (5 planes)"),
            "allowed": ("izin verilen", "allowed"),
            "no_maur_fails": ("Hi\u00e7bir d\u00fczlemde MAUR e\u015fi\u011fini a\u015fan kom\u015fu nokta \u00e7ifti bulunamad\u0131.",
                              "No adjacent point pairs exceeding the MAUR threshold were found in any plane."),
            "faulty_pairs": ("hatal\u0131 \u00e7ift", "faulty pairs"),
            "point_pair": ("Nokta \u00c7ifti", "Point Pair"),
            "value1": ("De\u011fer 1 (lx)", "Value 1 (lx)"),
            "value2": ("De\u011fer 2 (lx)", "Value 2 (lx)"),
            "ratio": ("Oran", "Ratio"),
            "raw_data_title": ("Ham \u00d6l\u00e7\u00fcm Verileri", "Raw Measurement Data"),
            "grid_no": ("Grid No", "Grid No"),
            "heatmap_title": ("Is\u0131 Haritas\u0131", "Heat Map"),
            "average": ("Ortalama", "Average"),
            "minimum": ("Minimum", "Minimum"),
            "maximum": ("Maksimum", "Maximum"),
            "uniformity_u1_short": ("D\u00fczg\u00fcnl\u00fck U1", "Uniformity U1"),
            "uniformity_u2_short": ("D\u00fczg\u00fcnl\u00fck U2", "Uniformity U2"),
            "page": ("Sayfa", "Page"),
            "pdf_saved": ("PDF Kaydedildi", "PDF Saved"),
            "file_saved": ("Dosya kaydedildi", "File saved"),
            "pdf_error": ("PDF Hatas\u0131", "PDF Error"),
            "pdf_error_msg": ("PDF olu\u015fturulurken bir sorun olu\u015ftu", "An error occurred while creating the PDF"),
        }

        def t(key, **kwargs):
            val = TXT[key][0] if lang == "tr" else TXT[key][1]
            return val.format(**kwargs) if kwargs else val

        BRAND = (41, 82, 130)       # ana marka mavisi (kurumsal)
        BRAND_TINT = (219, 229, 241)  # acik mavi zemin tonu (tablo basliklari)
        GOOD = (20, 130, 60)
        BAD = (180, 30, 30)
        MUTED = (120, 120, 128)
        MIN_MARK = (60, 130, 220)   # isi haritasinda en dusuk 3 deger - mavi kose
        MAX_MARK = (210, 60, 55)    # isi haritasinda en yuksek 3 deger - kirmizi kose

        # Bizim ic verimizdeki (uygulama arayuzuyle ORTAK) sabit Turkce etiketleri
        # PDF ciktisinda secilen dile cevirmek icin kucuk bir eslesme tablosu -
        # boylece uygulamanin kendi ekranlari (Rapor sekmesi) HIC etkilenmiyor,
        # sadece PDF ciktisi degisiyor.
        LABEL_MAP_EN = {
            "Ortalama >": "Average >", "Minimum >": "Minimum >",
            "Uniformity U1": "Uniformity U1", "Uniformity U2": "Uniformity U2",
            "Yatay (Eh)": "Horizontal (Eh)",
            "Dikey 0°": "Vertical 0°", "Dikey 90°": "Vertical 90°",
            "Dikey 180°": "Vertical 180°", "Dikey 270°": "Vertical 270°",
        }

        def tl(label):
            """plane_groups/criteria icindeki SABIT Turkce etiketi gerekirse cevirir."""
            if lang == "en":
                return LABEL_MAP_EN.get(label, label)
            return label

        class BrandedPDF(FPDF):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                self.header_title = ""
                self.suppress_header = False
                self.base_font = "Helvetica"

            def header(self):
                if self.suppress_header:
                    return
                self.set_fill_color(*BRAND)
                self.rect(0, 0, self.w, 10, style="F")
                self.set_text_color(255, 255, 255)
                self.set_font(self.base_font, "B", 8.5)
                self.set_xy(10, 2.6)
                self.cell(0, 5, self.header_title, align="L")
                self.set_text_color(0, 0, 0)
                self.set_y(15)

            def footer(self):
                if self.page_no() == 1:
                    return
                self.set_y(-12)
                self.set_font(self.base_font, "", 8)
                self.set_text_color(*MUTED)
                self.cell(0, 8, f"{t('page')} {self.page_no()}", align="C")
                self.set_text_color(0, 0, 0)

        try:
            pdf = BrandedPDF(orientation="P", unit="mm", format="A4")

            # --- Turkce karakterlerin (C, G, I, O, S, U) DOGRU gorunmesi icin
            #     gercek bir TTF font gomuyoruz - varsayilan Helvetica bunlari
            #     desteklemiyor. Font dosyasi yoksa (beklenmedik durum) Helvetica'ya
            #     geri donup uygulamanin cokmesini onluyoruz. ---
            FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
            font_regular = os.path.join(FONT_DIR, "DejaVuSans.ttf")
            font_bold = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
            font_italic = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")
            try:
                if os.path.exists(font_regular) and os.path.exists(font_bold):
                    pdf.add_font("DejaVu", "", font_regular)
                    pdf.add_font("DejaVu", "B", font_bold)
                    if os.path.exists(font_italic):
                        pdf.add_font("DejaVu", "I", font_italic)
                    else:
                        pdf.add_font("DejaVu", "I", font_regular)  # yedek
                    BASE_FONT = "DejaVu"
                else:
                    BASE_FONT = "Helvetica"
            except Exception:
                BASE_FONT = "Helvetica"
            pdf.base_font = BASE_FONT
            proj = data["project_info"]
            fifa = data["fifa_info"]
            pdf.header_title = f"{proj.get('name') or t('cover_subtitle')}"

            # ============================================================
            # SAYFA 1: KAPAK SAYFASI (kurumsal, musteriye sunulabilir)
            # ============================================================
            pdf.suppress_header = True
            pdf.add_page()
            pdf.set_fill_color(*BRAND)
            pdf.rect(0, 0, pdf.w, 7, style="F")
            pdf.rect(0, pdf.h - 7, pdf.w, 7, style="F")

            try:
                logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon_print.png")
                pdf.image(logo_path,
                          x=pdf.w / 2 - 18, y=30, w=36, h=36)
            except Exception:
                pass

            pdf.set_y(78)
            pdf.set_font(BASE_FONT, "B", 21)
            pdf.set_text_color(25, 28, 33)
            pdf.cell(0, 11, t("cover_title"), align="C", ln=True)
            pdf.set_font(BASE_FONT, "", 11)
            pdf.set_text_color(120, 120, 128)
            pdf.cell(0, 7, "Illuminance Measurement Report" if lang == "tr" else "", align="C", ln=True)

            pdf.ln(10)
            pdf.set_draw_color(*BRAND)
            pdf.set_line_width(0.6)
            y_line = pdf.get_y()
            pdf.line(pdf.w / 2 - 30, y_line, pdf.w / 2 + 30, y_line)
            pdf.set_draw_color(0, 0, 0)
            pdf.ln(10)

            pdf.set_font(BASE_FONT, "B", 18)
            pdf.set_text_color(20, 22, 26)
            pdf.multi_cell(0, 9, proj.get("name") or "-", align="C")
            pdf.set_x(pdf.l_margin)
            pdf.set_font(BASE_FONT, "", 12)
            pdf.set_text_color(90, 90, 98)
            pdf.cell(0, 7, proj.get("location") or "-", align="C", ln=True)

            pdf.ln(6)
            pdf.set_font(BASE_FONT, "", 10.5)
            pdf.set_text_color(70, 70, 78)
            pdf.cell(0, 6, f"{t('date_label')}: {proj.get('date') or '-'}", align="C", ln=True)
            pdf.cell(0, 6, f"{t('standard_label')}: {data['org']} - {data['level']}",
                     align="C", ln=True)
            pdf.cell(0, 6, f"{t('prepared_by_label')}: {proj.get('prepared_by') or '-'}", align="C", ln=True)

            pdf.set_y(-30)
            pdf.set_font(BASE_FONT, "", 9)
            pdf.set_text_color(*MUTED)
            pdf.cell(0, 5, data["fifa_info"].get("org_name", ORG_NAME), align="C", ln=True)
            pdf.cell(0, 5, f"{t('report_created')}: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                     align="C", ln=True)
            pdf.set_text_color(0, 0, 0)

            # ============================================================
            # SAYFA 2: "Cover Sheet" - resmi FIFA/UEFA formatiyla BIREBIR
            # ============================================================
            pdf.suppress_header = True
            pdf.add_page()

            def fifa_header(text):
                pdf.set_fill_color(*BRAND)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font(BASE_FONT, "B", 13)
                pdf.cell(0, 10, text, ln=True, fill=True, align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)

            def fifa_row(label, value):
                pdf.set_font(BASE_FONT, "", 10)
                pdf.set_fill_color(*BRAND_TINT)
                pdf.cell(75, 8, label, border=1, fill=True)
                pdf.cell(0, 8, str(value) if value else "-", border=1, ln=True)

            fifa_header(f"{data['org']} {t('fifa_cover_title')}")
            fifa_row(t("name_of_stadium"), proj.get("name"))
            fifa_row(t("city_location"), proj.get("location"))
            fifa_row(t("date_of_inspection"), proj.get("date"))

            pdf.ln(2)
            pdf.set_font(BASE_FONT, "B", 10)
            pdf.set_fill_color(*BRAND_TINT)
            pdf.cell(75, 8, "", border=0)
            pdf.cell(0, 8, t("luminaire"), border=1, align="C", fill=True, ln=True)

            def fifa_lum_row(label, suffix):
                pdf.set_font(BASE_FONT, "", 10)
                pdf.cell(75, 8, label, border=1)
                pdf.cell(0, 8, fifa.get(f"lum1_{suffix}") or "-", border=1, align="C", ln=True)

            fifa_lum_row(t("manufacturer"), "manufacturer")
            fifa_lum_row(t("model_product_type"), "model")

            pdf.ln(2)
            fifa_row(t("illuminance_meter_used"), fifa.get("meter_model", METER_MODEL))
            fifa_row(t("serial_illuminance_meter"), fifa.get("meter_serial", METER_SERIAL))
            fifa_row(t("calibration_date"), fifa.get("cal_date"))
            probe_labels = [
                (t("probe_serial", n=0), "probe_serial_eh", "Eh"),
                (t("probe_serial", n=1), "probe_serial_ev0", "Ev0"),
                (t("probe_serial", n=2), "probe_serial_ev90", "Ev90"),
                (t("probe_serial", n=3), "probe_serial_ev180", "Ev180"),
                (t("probe_serial", n=4), "probe_serial_ev270", "Ev270"),
            ]
            for label, fifa_key, probe_key in probe_labels:
                fifa_row(label, fifa.get(fifa_key, PROBE_SERIALS[probe_key]))

            pdf.ln(2)
            fifa_row(t("colour_meter_used"), fifa.get("colour_meter"))
            fifa_row(t("serial_colour_meter"), fifa.get("colour_meter_serial"))
            fifa_row(t("calibration_date"), fifa.get("colour_meter_cal_date"))

            pdf.ln(2)
            pdf.set_font(BASE_FONT, "B", 10)
            pdf.set_fill_color(*BRAND_TINT)
            pdf.cell(75, 8, t("pitch_measurements"), border=0)
            pdf.cell(55, 8, t("width"), border=1, align="C", fill=True)
            pdf.cell(0, 8, t("length"), border=1, align="C", fill=True, ln=True)
            pdf.set_font(BASE_FONT, "", 10)
            pdf.cell(75, 8, "", border=0)
            w_val = f"{fifa.get('pitch_width')} m" if fifa.get("pitch_width") else "-"
            l_val = f"{fifa.get('pitch_length')} m" if fifa.get("pitch_length") else "-"
            pdf.cell(55, 8, w_val, border=1, align="C")
            pdf.cell(0, 8, l_val, border=1, align="C", ln=True)

            pdf.ln(2)
            fifa_row(t("organisation_inspecting"), fifa.get("org_name", ORG_NAME))
            pdf.set_font(BASE_FONT, "", 10)
            pdf.set_fill_color(*BRAND_TINT)
            addr_y = pdf.get_y()
            pdf.multi_cell(75, 8, t("address"), border=1, fill=True)
            addr_h = pdf.get_y() - addr_y
            pdf.set_xy(75 + 10, addr_y)
            pdf.multi_cell(0, 8, fifa.get("org_address", ORG_ADDRESS), border=1)
            val_h = pdf.get_y() - addr_y
            pdf.set_y(addr_y + max(addr_h, val_h))
            fifa_row(t("telephone_email"), fifa.get("org_phone_email", ORG_PHONE_EMAIL))
            fifa_row(t("inspection_by"), fifa.get("inspector_name", INSPECTOR_NAME))
            fifa_row(t("signature"), "")

            # ============================================================
            # SAYFA 3: "Summary of Results" - resmi FIFA/UEFA formatiyla
            # ============================================================
            pdf.add_page()
            fifa_header(f"{data['org']} {t('fifa_summary_title')}")

            pdf.set_font(BASE_FONT, "", 10)
            pdf.set_fill_color(*BRAND_TINT)
            pdf.cell(90, 8, t("stadium_name_location"), border=1, fill=True)
            pdf.cell(0, 8, f"{proj.get('name') or '-'} / {proj.get('location') or '-'}",
                     border=1, ln=True)
            pdf.cell(90, 8, t("test_date"), border=1, fill=True)
            pdf.cell(0, 8, proj.get("date") or "-", border=1, ln=True)
            pdf.ln(3)

            fm = data["fifa_metrics"]

            def fifa_fmt(v, dec=0):
                return f"{v:.{dec}f}" if isinstance(v, (int, float)) else "-"

            def metric_row(label, value):
                pdf.set_font(BASE_FONT, "", 9.5)
                pdf.cell(130, 7, label, border=1)
                pdf.cell(0, 7, str(value), border=1, align="C", ln=True)

            for title, deg in [("Ev0", "0°"), ("Ev90", "90°"), ("Ev180", "180°"), ("Ev270", "270°")]:
                m = fm[title]
                pdf.set_font(BASE_FONT, "B", 10)
                pdf.set_fill_color(*BRAND_TINT)
                pdf.cell(0, 7, f"{t('vertical_plane')} - {deg}", border=1, fill=True, ln=True)
                metric_row(f"{t('ev_min')}-{deg}", fifa_fmt(m["min"]))
                metric_row(f"{t('ev_max')}-{deg}", fifa_fmt(m["max"]))
                metric_row(f"{t('ev_ave')}-{deg}", fifa_fmt(m["avg"]))
                metric_row(f"{t('uniformity_u1v')}-{deg}", fifa_fmt(m["u1"], 2))
                metric_row(f"{t('uniformity_u2v')}-{deg}", fifa_fmt(m["u2"], 2))
                metric_row(f"{t('maur_fails')} {deg}",
                           m["maur_fails"] if m["maur_fails"] is not None else "-")

            m = fm["Eh"]
            pdf.set_font(BASE_FONT, "B", 10)
            pdf.set_fill_color(*BRAND_TINT)
            pdf.cell(0, 7, t("horizontal_plane"), border=1, fill=True, ln=True)
            metric_row(t("eh_min"), fifa_fmt(m["min"]))
            metric_row(t("eh_max"), fifa_fmt(m["max"]))
            metric_row(t("eh_ave"), fifa_fmt(m["avg"]))
            metric_row(t("uniformity_u1h"), fifa_fmt(m["u1"], 2))
            metric_row(t("uniformity_u2h"), fifa_fmt(m["u2"], 2))
            metric_row(t("maur_horizontal_fails"), m["maur_fails"] if m["maur_fails"] is not None else "-")

            pdf.set_font(BASE_FONT, "B", 10)
            pdf.set_fill_color(*BRAND_TINT)
            pdf.cell(0, 7, t("other_measurements"), border=1, fill=True, ln=True)
            metric_row(t("avg_flicker"), fifa.get("flicker_avg") or "-")
            metric_row(t("max_flicker"), fifa.get("flicker_max") or "-")
            metric_row(t("colour_temp"), fifa.get("colour_temp_tc") or "-")
            metric_row(t("colour_rendering"), fifa.get("colour_rendering_ra") or "-")
            metric_row(t("glare_rating"), fifa.get("glare_rating_rg") or "-")

            # ============================================================
            # SAYFA 4+: Bizim kendi detayli ic raporumuz (marka renkleriyle)
            # ============================================================
            pdf.suppress_header = False
            pdf.add_page()
            pdf.set_font(BASE_FONT, "B", 16)
            pdf.set_text_color(*BRAND)
            pdf.cell(0, 10, t("detailed_report_title"), ln=True, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
            pdf.set_font(BASE_FONT, "", 10)
            pdf.cell(0, 6, f"{t('facility')}: {proj.get('name') or '-'}", ln=True)
            pdf.cell(0, 6, f"{t('country_city')}: {proj.get('location') or '-'}", ln=True)
            pdf.cell(0, 6, f"{t('date_label')}: {proj.get('date') or '-'}", ln=True)
            pdf.cell(0, 6, f"{t('prepared_by_label')}: {proj.get('prepared_by') or '-'}", ln=True)
            pdf.cell(0, 6, f"{t('standard_label')}: {data['org']} {data['level']}", ln=True)
            total_points = data["total_points"]
            measured_count = data["measured_count"]
            pdf.cell(0, 6, f"{t('grid')}: {data['rows_count']} x {data['cols_count']}   "
                           f"{t('measured')}: {measured_count}/{total_points}", ln=True)
            pdf.ln(3)

            verdict_ok = data["all_pass"]
            pdf.set_fill_color(224, 242, 228) if verdict_ok else pdf.set_fill_color(250, 226, 226)
            pdf.set_draw_color(*(GOOD if verdict_ok else BAD))
            pdf.set_line_width(0.4)
            vy = pdf.get_y()
            pdf.rect(10, vy, pdf.w - 20, 10, style="DF")
            pdf.set_xy(10, vy + 1.5)
            pdf.set_font(BASE_FONT, "B", 12)
            pdf.set_text_color(*(GOOD if verdict_ok else BAD))
            pdf.cell(pdf.w - 20, 7, t("meets_criteria") if verdict_ok else t("fails_criteria"),
                     align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.2)
            pdf.set_y(vy + 13)

            for group_title, criteria in data["plane_groups"]:
                pdf.set_font(BASE_FONT, "B", 11)
                pdf.set_fill_color(*BRAND_TINT)
                pdf.set_text_color(*BRAND)
                pdf.cell(0, 7, tl(group_title), border=1, fill=True, ln=True)
                pdf.set_text_color(0, 0, 0)
                col_w = [55, 35, 45, 45]
                pdf.set_font(BASE_FONT, "B", 9)
                pdf.set_fill_color(240, 240, 244)
                for w, h in zip(col_w, [t("criterion"), t("reference"), t("measured_col"), t("result")]):
                    pdf.cell(w, 6, h, border=1, fill=True)
                pdf.ln()
                pdf.set_font(BASE_FONT, "", 9)
                for label, ref, val, ok in criteria:
                    pdf.cell(col_w[0], 6, tl(label), border=1)
                    pdf.cell(col_w[1], 6, str(ref), border=1, align="C")
                    pdf.cell(col_w[2], 6, str(val), border=1, align="C")
                    pdf.set_text_color(*GOOD) if ok else pdf.set_text_color(*BAD)
                    pdf.cell(col_w[3], 6, t("compliant") if ok else t("non_compliant"), border=1)
                    pdf.set_text_color(0, 0, 0)
                    pdf.ln()
                pdf.ln(2)

            pdf.set_font(BASE_FONT, "B", 12)
            pdf.set_text_color(*BRAND)
            pdf.cell(0, 8, t("maur_title"), ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font(BASE_FONT, "", 10)
            if data["maur_ratio"] is None:
                pdf.cell(0, 7, t("maur_not_specified"), ln=True)
            else:
                pdf.cell(0, 7, f"{t('threshold_ratio')}: {data['maur_ratio']:.2f}   |   "
                               f"{t('total_fails')}: {data['maur_total_fail']} / "
                               f"{t('allowed')} {data['maur_max_fail']}", ln=True)
                pdf.set_font(BASE_FONT, "B", 11)
                pdf.set_text_color(*GOOD) if data["maur_ok"] else pdf.set_text_color(*BAD)
                pdf.cell(0, 7, t("compliant") if data["maur_ok"] else t("non_compliant"), ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)

                fm = data["fifa_metrics"]
                any_detail = any(fm[t2].get("maur_fail_details") for t2, _ in PROBES)
                if not any_detail:
                    pdf.set_font(BASE_FONT, "I", 9.5)
                    pdf.set_text_color(*GOOD)
                    pdf.cell(0, 6, t("no_maur_fails"), ln=True)
                    pdf.set_text_color(0, 0, 0)
                else:
                    for title, _ in PROBES:
                        details = fm[title].get("maur_fail_details") or []
                        if not details:
                            continue
                        if pdf.get_y() > 250:
                            pdf.add_page()
                        pdf.set_font(BASE_FONT, "B", 10)
                        pdf.set_fill_color(*BRAND_TINT)
                        pdf.cell(0, 6.5, f"{title} - {len(details)} {t('faulty_pairs')}", border=1,
                                 fill=True, ln=True)
                        pdf.set_font(BASE_FONT, "B", 9)
                        pdf.set_fill_color(240, 240, 244)
                        col_w = [55, 40, 40, 45]
                        detail_headers = [t("point_pair"), t("value1"), t("value2"), t("ratio")]
                        for w, h in zip(col_w, detail_headers):
                            pdf.cell(w, 6, h, border=1, fill=True, align="C")
                        pdf.ln()
                        pdf.set_font(BASE_FONT, "", 9)
                        for item in details:
                            if pdf.get_y() > 270:
                                pdf.add_page()
                                pdf.set_font(BASE_FONT, "B", 9)
                                pdf.set_fill_color(240, 240, 244)
                                for w, h in zip(col_w, detail_headers):
                                    pdf.cell(w, 6, h, border=1, fill=True, align="C")
                                pdf.ln()
                                pdf.set_font(BASE_FONT, "", 9)
                            pdf.cell(col_w[0], 6, f"{t('grid_no')} {item['grid1']} <-> {item['grid2']}",
                                     border=1, align="C")
                            pdf.cell(col_w[1], 6, f"{item['v1']}", border=1, align="C")
                            pdf.cell(col_w[2], 6, f"{item['v2']}", border=1, align="C")
                            pdf.set_text_color(*BAD)
                            pdf.cell(col_w[3], 6, f"{item['ratio']:.2f}", border=1, align="C")
                            pdf.set_text_color(0, 0, 0)
                            pdf.ln()
                        pdf.ln(2)

            # --- Ham Olcum Verileri sayfasi ---
            raw_seq = data["raw_sequence"]
            raw_meas = data["raw_measurements"]
            pdf.add_page()
            pdf.set_font(BASE_FONT, "B", 14)
            pdf.set_text_color(*BRAND)
            pdf.cell(0, 10, t("raw_data_title"), ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
            headers_raw = [t("grid_no")] + [title for title, _ in PROBES]
            col_w_raw = [22, 33, 33, 33, 33, 33]

            def raw_header_row():
                pdf.set_font(BASE_FONT, "B", 9)
                pdf.set_fill_color(*BRAND)
                pdf.set_text_color(255, 255, 255)
                for w, h in zip(col_w_raw, headers_raw):
                    pdf.cell(w, 7, h, border=1, fill=True, align="C")
                pdf.ln()
                pdf.set_text_color(0, 0, 0)

            raw_header_row()
            pdf.set_font(BASE_FONT, "", 9)
            row_i = 0
            for idx in range(len(raw_seq)):
                d = raw_meas.get(idx)
                if d is None:
                    continue
                if pdf.get_y() > 270:
                    pdf.add_page()
                    raw_header_row()
                    pdf.set_font(BASE_FONT, "", 9)
                pdf.set_fill_color(*(BRAND_TINT if row_i % 2 == 0 else (255, 255, 255)))
                pdf.cell(col_w_raw[0], 6, str(idx + 1), border=1, align="C", fill=True)
                for w, (title, _) in zip(col_w_raw[1:], PROBES):
                    val = d["values"].get(title)
                    pdf.cell(w, 6, f"{val}" if val is not None else "-", border=1, align="C", fill=True)
                pdf.ln()
                row_i += 1

            # --- Her veri seti icin renkli Isi Haritasi sayfasi ---
            rows_n = data["rows_count"]
            cols_n = data["cols_count"]
            pos_to_gridno_pdf = {rc: idx + 1 for idx, rc in enumerate(data["raw_sequence"])}
            for title, _ in PROBES:
                grid = self._dataset_grid(raw_meas, rows_n, cols_n, title)
                vals = [v for row_vals in grid for v in row_vals if v is not None]
                if not vals:
                    continue
                vmin_g, vmax_g = min(vals), max(vals)

                # uygulamadaki gibi en yuksek/dusuk 3 degeri isaretlemek icin
                indexed_vals = sorted(
                    [(v, ci, ri) for ci, row in enumerate(grid) for ri, v in enumerate(row) if v is not None]
                )
                n_extreme = min(3, len(indexed_vals))
                lowest_set = {(ci, ri) for v, ci, ri in indexed_vals[:n_extreme]}
                highest_set = {(ci, ri) for v, ci, ri in indexed_vals[-n_extreme:]}

                pdf.add_page()
                pdf.set_font(BASE_FONT, "B", 14)
                pdf.set_text_color(*BRAND)
                pdf.cell(0, 10, f"{t('heatmap_title')} - {title}", ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)

                dir_margin = 9  # 180deg/0deg etiketleri icin sol/sag bosluk
                avail_w = 190 - 2 * dir_margin
                avail_h = 190
                cell_w = min(avail_w / rows_n, 22)
                cell_h = min(avail_h / cols_n, 14)
                grid_w_total = rows_n * cell_w
                grid_h_total = cols_n * cell_h

                # --- 270deg etiketi (ustte, ortada) ---
                pdf.set_font(BASE_FONT, "B", 9)
                pdf.set_text_color(*BRAND)
                pdf.set_xy(pdf.l_margin + dir_margin, pdf.get_y())
                pdf.cell(grid_w_total, 5, "270°", align="C")
                pdf.ln(6)

                start_x = pdf.l_margin + dir_margin
                start_y = pdf.get_y()

                # --- 180deg (sol) ve 0deg (sag) etiketleri (dikey ortada) ---
                pdf.set_xy(pdf.l_margin, start_y + grid_h_total / 2 - 2.5)
                pdf.cell(dir_margin - 1, 5, "180°", align="C")
                pdf.set_xy(start_x + grid_w_total + 1, start_y + grid_h_total / 2 - 2.5)
                pdf.cell(dir_margin - 1, 5, "0°", align="C")
                pdf.set_text_color(0, 0, 0)

                for c_idx, row_vals in enumerate(grid):
                    for r_idx, val in enumerate(row_vals):
                        x = start_x + r_idx * cell_w
                        y = start_y + c_idx * cell_h
                        if val is None:
                            pdf.set_fill_color(230, 230, 230)
                            pdf.set_draw_color(255, 255, 255)
                            pdf.rect(x, y, cell_w, cell_h, style="DF")
                            continue
                        rgba = lux_color(val, vmin_g, vmax_g)
                        pdf.set_fill_color(int(rgba[0]*255), int(rgba[1]*255), int(rgba[2]*255))
                        pdf.set_draw_color(255, 255, 255)
                        pdf.rect(x, y, cell_w, cell_h, style="DF")
                        txt_rgba = text_color_for_bg(rgba)
                        pdf.set_text_color(int(txt_rgba[0]*255), int(txt_rgba[1]*255), int(txt_rgba[2]*255))
                        pdf.set_xy(x, y + cell_h / 2 - 2)
                        pdf.set_font(BASE_FONT, "B", 6.5)
                        pdf.cell(cell_w, 4, f"{val}", align="C")
                        # Grid No - hucrenin sol ust kosesinde, kucuk ve sonuk
                        grid_no_val = pos_to_gridno_pdf.get((r_idx, c_idx))
                        if grid_no_val is not None:
                            pdf.set_xy(x + 0.8, y + 0.6)
                            pdf.set_font(BASE_FONT, "", 5)
                            pdf.cell(cell_w - 1, 3, str(grid_no_val), align="L")
                        # kose isareti: min (mavi) / maks (kirmizi) - uygulamadaki bayrak gibi
                        # (once beyaz kontur, uzerine renkli isaret - HER zeminde gorunur)
                        if (c_idx, r_idx) in lowest_set or (c_idx, r_idx) in highest_set:
                            mark_color = MIN_MARK if (c_idx, r_idx) in lowest_set else MAX_MARK
                            pdf.set_fill_color(255, 255, 255)
                            pdf.rect(x + cell_w - 3.6, y, 3.6, 3.6, style="F")
                            pdf.set_fill_color(*mark_color)
                            pdf.rect(x + cell_w - 3, y + 0.3, 3, 3, style="F")
                pdf.set_text_color(0, 0, 0)
                pdf.set_draw_color(0, 0, 0)

                # --- 90deg etiketi (altta, ortada) ---
                pdf.set_font(BASE_FONT, "B", 9)
                pdf.set_text_color(*BRAND)
                pdf.set_xy(start_x, start_y + grid_h_total + 2)
                pdf.cell(grid_w_total, 5, "90°", align="C")
                pdf.set_text_color(0, 0, 0)

                # --- Renk skalasi (legend) - uygulamadaki Sonuc ekraniyla ayni ---
                legend_y = start_y + cols_n * cell_h + 15
                legend_x = start_x
                legend_w = min(avail_w, rows_n * cell_w)
                legend_h = 6
                steps = 50
                seg_w = legend_w / steps
                for i in range(steps):
                    t_frac = i / (steps - 1)
                    color = lux_color(vmin_g + t_frac * (vmax_g - vmin_g), vmin_g, vmax_g)
                    pdf.set_fill_color(int(color[0]*255), int(color[1]*255), int(color[2]*255))
                    pdf.rect(legend_x + i * seg_w, legend_y, seg_w + 0.4, legend_h, style="F")
                pdf.set_draw_color(180, 180, 180)
                pdf.rect(legend_x, legend_y, legend_w, legend_h, style="D")
                pdf.set_draw_color(0, 0, 0)

                pdf.set_font(BASE_FONT, "", 8)
                pdf.set_text_color(100, 100, 105)
                n_ticks = 5
                for i in range(n_ticks):
                    t_frac = i / (n_ticks - 1)
                    val_tick = vmin_g + t_frac * (vmax_g - vmin_g)
                    tx = legend_x + t_frac * legend_w
                    pdf.set_xy(tx - 10, legend_y + legend_h + 1)
                    align = "L" if i == 0 else ("R" if i == n_ticks - 1 else "C")
                    pdf.cell(20, 5, f"{val_tick:.0f}", align=align)
                pdf.set_text_color(0, 0, 0)

                # --- Bu duzleme ait Ortalama/Min/Maks/Duzgunluk ozeti ---
                stats = data["fifa_metrics"][title]
                stat_items = [
                    (t("average"), f"{stats['avg']:.0f}"),
                    (t("minimum"), f"{stats['min']:.0f}"),
                    (t("maximum"), f"{stats['max']:.0f}"),
                    (t("uniformity_u1_short"), f"{stats['u1']:.2f}"),
                    (t("uniformity_u2_short"), f"{stats['u2']:.2f}"),
                ]
                stats_y = legend_y + legend_h + 12
                stats_w = max(legend_w, 150)
                col_w_stat = stats_w / len(stat_items)
                pdf.set_xy(start_x, stats_y)
                pdf.set_font(BASE_FONT, "B", 9)
                pdf.set_fill_color(*BRAND_TINT)
                for label, _ in stat_items:
                    pdf.cell(col_w_stat, 7, label, border=1, fill=True, align="C")
                pdf.set_xy(start_x, stats_y + 7)
                pdf.set_font(BASE_FONT, "B", 11)
                pdf.set_fill_color(255, 255, 255)
                for _, val in stat_items:
                    pdf.cell(col_w_stat, 8, val, border=1, align="C")

            fname = f"aydinlatma_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            fpath = os.path.join(self._export_dir(), fname)
            pdf.output(fpath)
            self._save_file_with_picker(fpath, fname, "application/pdf", t("pdf_saved"))
        except Exception as e:
            self._show_message_popup(t("pdf_error"), f"{t('pdf_error_msg')}:\n{e}")

    def export_excel(self):
        ms = self.measure_screen
        if ms.org == "FIBA":
            self._show_message_popup(
                "Excel (FIBA)",
                "FIBA standardi icin Excel disa aktarma yakinda eklenecek.\n"
                "Sonuclari su an icin Rapor sekmesinde goruntuleyebilir\n"
                "veya 'Verileri Disa Aktar' ile ham veriyi yedekleyebilirsiniz.")
            return
        data = self._compute_report_data()
        if not data:
            self._show_message_popup("Excel", "Once olcum girin, sonra rapor disa aktarilabilir.")
            return
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill
        except Exception as e:
            self._show_message_popup(
                "Excel Kutuphanesi Sorunu",
                f"'openpyxl' kutuphanesi yuklenemedi.\n\nTeknik detay:\n{type(e).__name__}: {e}")
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Rapor"
            bold = Font(bold=True)
            green = Font(bold=True, color="148238")
            red = Font(bold=True, color="B41E1E")
            gray_fill = PatternFill("solid", fgColor="E6E6E6")

            row = 1
            ws.cell(row=row, column=1, value="SAHA AYDINLATMA UYGUNLUK RAPORU").font = Font(bold=True, size=14)
            row += 2

            proj = data["project_info"]
            for label, key in [("Stadyum/Tesis", "name"), ("Ulke / Sehir", "location"),
                                ("Olcum Tarihi", "date"), ("Raporu Hazirlayan", "prepared_by")]:
                ws.cell(row=row, column=1, value=label).font = bold
                ws.cell(row=row, column=2, value=proj.get(key, "") or "-")
                row += 1
            ws.cell(row=row, column=1, value="Karsilastirilan Standart").font = bold
            ws.cell(row=row, column=2, value=f"{data['org']} {data['level']}")
            row += 1
            ws.cell(row=row, column=1, value="Izgara").font = bold
            ws.cell(row=row, column=2, value=f"{data['rows']} x {data['cols']}")
            row += 1
            ws.cell(row=row, column=1, value="Olculen Nokta").font = bold
            ws.cell(row=row, column=2, value=f"{data['measured_count']}/{data['total_points']}")
            row += 2

            verdict = "KRITERLERI KARSILIYOR" if data["all_pass"] else "KRITERLERI KARSILAMIYOR"
            c = ws.cell(row=row, column=1, value=verdict)
            c.font = green if data["all_pass"] else red
            row += 2

            headers = ["Duzlem", "Kriter", "Referans", "Olculen", "Sonuc"]
            for col, h in enumerate(headers, start=1):
                cell = ws.cell(row=row, column=col, value=h)
                cell.font = bold
                cell.fill = gray_fill
            row += 1

            for plane_title, criteria in data["plane_groups"]:
                for kriter, referans, olculen, ok in criteria:
                    ws.cell(row=row, column=1, value=plane_title)
                    ws.cell(row=row, column=2, value=kriter)
                    ws.cell(row=row, column=3, value=referans)
                    ws.cell(row=row, column=4, value=olculen)
                    sonuc_cell = ws.cell(row=row, column=5, value="UYGUN" if ok else "UYGUN DEGIL")
                    sonuc_cell.font = green if ok else red
                    row += 1
            row += 1

            ws.cell(row=row, column=1, value="MAUR - Komsu Nokta Tekduzeligi").font = bold
            row += 1
            if data["maur_ratio"] is None:
                ws.cell(row=row, column=1, value="Bu standart seviyesi icin MAUR belirtilmemis.")
            else:
                ws.cell(row=row, column=1,
                        value=f"Toplam hata (5 duzlem): {data['maur_total_fail']} / "
                              f"izin verilen {data['maur_max_fail']}")
                row += 1
                mc = ws.cell(row=row, column=1, value="UYGUN" if data["maur_ok"] else "UYGUN DEGIL")
                mc.font = green if data["maur_ok"] else red

            for col_letter, width in zip("ABCDE", [22, 16, 12, 12, 14]):
                ws.column_dimensions[col_letter].width = width

            # --- YENI: Ham Olcum Verileri sayfasi (Olcum Verisi ekranindaki tablo) ---
            ws2 = wb.create_sheet("Olcum Verileri")
            headers2 = ["Grid No"] + [title for title, _ in PROBES]
            for col, h in enumerate(headers2, start=1):
                cell = ws2.cell(row=1, column=col, value=h)
                cell.font = bold
                cell.fill = gray_fill
            raw_seq = data["raw_sequence"]
            raw_meas = data["raw_measurements"]
            r_row = 2
            for idx in range(len(raw_seq)):
                d = raw_meas.get(idx)
                if d is None:
                    continue
                ws2.cell(row=r_row, column=1, value=idx + 1)
                for col, (title, _) in enumerate(PROBES, start=2):
                    ws2.cell(row=r_row, column=col, value=d["values"].get(title))
                r_row += 1
            for col_letter in "ABCDEF":
                ws2.column_dimensions[col_letter].width = 12

            # --- YENI: Her veri seti icin renkli Isi Haritasi sayfasi ---
            rows_n = data["rows_count"]
            cols_n = data["cols_count"]
            for title, _ in PROBES:
                grid = self._dataset_grid(raw_meas, rows_n, cols_n, title)
                vals = [v for row_vals in grid for v in row_vals if v is not None]
                if not vals:
                    continue
                vmin_g, vmax_g = min(vals), max(vals)
                ws3 = wb.create_sheet(f"Isi Haritasi - {title}")
                for c_idx, row_vals in enumerate(grid):
                    for r_idx, val in enumerate(row_vals):
                        cell = ws3.cell(row=c_idx + 1, column=r_idx + 1)
                        if val is None:
                            continue
                        cell.value = val
                        rgba = lux_color(val, vmin_g, vmax_g)
                        hexcolor = "".join(f"{int(max(0,min(1,ch))*255):02X}" for ch in rgba[:3])
                        cell.fill = PatternFill("solid", fgColor=hexcolor)
                        txt_rgba = text_color_for_bg(rgba)
                        txt_hex = "".join(f"{int(max(0,min(1,ch))*255):02X}" for ch in txt_rgba[:3])
                        cell.font = Font(bold=True, color=txt_hex)
                for col_idx in range(1, rows_n + 1):
                    ws3.column_dimensions[ws3.cell(row=1, column=col_idx).column_letter].width = 10

            fname = f"aydinlatma_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            fpath = os.path.join(self._export_dir(), fname)
            wb.save(fpath)
            self._save_file_with_picker(
                fpath, fname, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "Excel Kaydedildi")
        except Exception as e:
            self._show_message_popup("Excel Hatasi", f"Excel olusturulurken bir sorun olustu:\n{e}")

    def _build_fiba_report_section(self, measured, total_points):
        ms = self.measure_screen
        data = self._compute_fiba_report_data()
        if not data:
            return

        info_card = Card(bg_color=CARD, radius=14, orientation="vertical",
                          padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(4),
                          size_hint_y=None)
        standard_text = f"Standart: FIBA - {data['level']}" if data['level'] else "Standart: FIBA"
        info_card.add_widget(Label(text=standard_text, font_size=sp(14),
                                    bold=True, color=TEXT, size_hint_y=None, height=dp(22),
                                    halign="left", text_size=(dp(300), None)))
        is_incomplete = len(measured) < total_points
        count_color = RED_TXT if is_incomplete else GREEN_TXT
        count_label = Label(text=f"Izgara: {ms.rows_count_val} x {ms.cols_count_val}   |   "
                                  f"Olculen: {len(measured)}/{total_points} nokta"
                                  + ("  (EKSIK)" if is_incomplete else ""),
                             font_size=sp(12.5), color=count_color, bold=is_incomplete,
                             size_hint_y=None, height=dp(20), halign="left",
                             text_size=(dp(300), None))
        info_card.add_widget(count_label)
        cam_label = Label(text=f"PPA Kenar Payi: {data['ppa_margin']} halka   |   "
                                f"EC: Alici Kafa No.0 (ayri olcum)",
                           font_size=sp(11.5), color=TEXT_MUTED, size_hint_y=None,
                           height=dp(18), halign="left", text_size=(dp(300), None))
        info_card.add_widget(cam_label)
        info_card.bind(minimum_height=info_card.setter("height"))
        self.content_area.add_widget(info_card)

        verdict_ok = data["all_pass"]
        verdict_card = Card(bg_color=SUCCESS_TINT if verdict_ok else DANGER_TINT,
                             border_color=SUCCESS if verdict_ok else DANGER, radius=14,
                             size_hint_y=None, height=dp(46))
        verdict_lbl = Label(text="KRITERLERI KARSILIYOR" if verdict_ok else "KRITERLERI KARSILAMIYOR",
                             font_size=sp(15), bold=True,
                             color=GREEN_TXT if verdict_ok else RED_TXT)
        verdict_card.add_widget(verdict_lbl)
        self.content_area.add_widget(verdict_card)

        zone_titles = {"PPA": "PPA - Ana Oyun Alani", "TPA": "TPA - Toplam Oyun Alani"}
        COLW = [0.34, 0.20, 0.20, 0.26]

        def add_wide_row(container, text, bg):
            wrap = TableRow(bg)
            lbl = Label(text=text, font_size=sp(12.5), bold=True, color=TEXT)
            wrap.add_widget(lbl)
            container.add_widget(wrap)

        def add_crit_row(container, kriter, referans, olculen, ok, pos):
            row_bg = ROW_A if pos % 2 == 0 else ROW_B
            row = TableRow(row_bg)
            for i, (txt, col) in enumerate([
                (kriter, TEXT_MUTED), (referans, TEXT_MUTED),
                (olculen, GREEN_TXT if ok else RED_TXT),
                ("UYGUN" if ok else "UYGUN DEGIL", GREEN_TXT if ok else RED_TXT),
            ]):
                lbl = Label(text=txt, font_size=sp(11), bold=(i >= 2), color=col, size_hint_x=COLW[i])
                row.add_widget(lbl)
            container.add_widget(row)

        for zone_name in ["PPA", "TPA"]:
            zone = data["zones"].get(zone_name)
            if zone is None:
                continue
            zone_ok = zone["zone_ok"]
            zone_title_lbl = Label(
                text=f"{zone_titles[zone_name]}  ({'UYGUN' if zone_ok else 'UYGUN DEGIL'})",
                font_size=sp(14), bold=True, color=GREEN_TXT if zone_ok else RED_TXT,
                size_hint_y=None, height=dp(26), halign="left")
            zone_title_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
            self.content_area.add_widget(zone_title_lbl)

            table_card = Card(bg_color=CARD, radius=14, orientation="vertical", padding=0)
            header = TableRow(HEADER_BG)
            for i, h in enumerate(["Kriter", "Referans", "Olculen", "Sonuc"]):
                header.add_widget(Label(text=h, font_size=sp(11), bold=True, color=TEXT_MUTED,
                                         size_hint_x=COLW[i]))
            table_card.add_widget(header)

            th = FIBA_STANDARDS[zone_name]
            pos = 0

            add_wide_row(table_card, "EC (Ana Kamera)", HEADER_BG)
            ec = zone["EC"]
            if ec["avg"] is not None:
                add_crit_row(table_card, "Ortalama >", f"{th['ec_avg']}", f"{ec['avg']:.0f}",
                              ec["avg"] >= th["ec_avg"], pos); pos += 1
                add_crit_row(table_card, "Duzgunluk U1 >=", f"{th['ec_u1']:.2f}", f"{ec['u1']:.2f}",
                              ec["u1"] >= th["ec_u1"], pos); pos += 1
                add_crit_row(table_card, "Duzgunluk U2 >=", f"{th['ec_u2']:.2f}", f"{ec['u2']:.2f}",
                              ec["u2"] >= th["ec_u2"], pos); pos += 1
            else:
                add_crit_row(table_card, "Olculmedi", f">={th['ec_avg']}",
                              f"0/{ec['total_count']}", False, pos); pos += 1

            for d_name, d_res in zone["EV"]["per_direction"].items():
                deg = {"Ev0": "0°", "Ev90": "90°", "Ev180": "180°", "Ev270": "270°"}[d_name]
                add_wide_row(table_card, f"EV - Dikey {deg}", HEADER_BG)
                add_crit_row(table_card, "Ortalama >", f"{th['ev_avg']}", f"{d_res['avg']:.0f}",
                              d_res["avg"] >= th["ev_avg"], pos); pos += 1
                add_crit_row(table_card, "Duzgunluk U1 >=", f"{th['ev_u1']:.2f}", f"{d_res['u1']:.2f}",
                              d_res["u1"] >= th["ev_u1"], pos); pos += 1
                add_crit_row(table_card, "Duzgunluk U2 >=", f"{th['ev_u2']:.2f}", f"{d_res['u2']:.2f}",
                              d_res["u2"] >= th["ev_u2"], pos); pos += 1

            add_wide_row(table_card, "EV - Yonler Arasi Denge", HEADER_BG)
            add_crit_row(table_card, "Min/Maks >=", f"{th['ev_dir_ratio']:.2f}",
                          f"{zone['EV']['dir_ratio']:.2f}", zone["EV"]["dir_ratio_ok"], pos); pos += 1

            add_wide_row(table_card, "EH (Yatay)", HEADER_BG)
            eh = zone["EH"]
            if eh["avg"] is not None:
                add_crit_row(table_card, "Ortalama (aralik)", f"{th['eh_avg_min']}-{th['eh_avg_max']}",
                              f"{eh['avg']:.0f}", eh["avg_ok"], pos); pos += 1
                add_crit_row(table_card, "Duzgunluk U1 >=", f"{th['eh_u1']:.2f}", f"{eh['u1']:.2f}",
                              eh["u1"] >= th["eh_u1"], pos); pos += 1
                add_crit_row(table_card, "Duzgunluk U2 >=", f"{th['eh_u2']:.2f}", f"{eh['u2']:.2f}",
                              eh["u2"] >= th["eh_u2"], pos); pos += 1
            else:
                add_crit_row(table_card, "Olculmedi", f"{th['eh_avg_min']}-{th['eh_avg_max']}",
                              f"0/{eh['total_count']}", False, pos); pos += 1

            table_card.bind(minimum_height=table_card.setter("height"))
            self.content_area.add_widget(table_card)

        # --- Isik Kaynagi (Tablo 6): Flicker/CRI/Renk Sicakligi - TPA'nin her noktasi
        #     icin gecerli, elle girilen bilgiler (Ek Rapor Bilgilerini Duzenle'den) ---
        fifa = data["fifa_info"]
        ls_card = Card(bg_color=CARD, radius=14, orientation="vertical",
                        padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(4),
                        size_hint_y=None)
        ls_card.add_widget(Label(text="Isik Kaynagi (Tablo 6)", font_size=sp(14), bold=True,
                                  color=TEXT, size_hint_y=None, height=dp(22),
                                  halign="left", text_size=(dp(300), None)))

        def ls_row(label, ref_str, val_str):
            row = BoxLayout(size_hint_y=None, height=dp(20))
            row.add_widget(Label(text=label, font_size=sp(11.5), color=TEXT_MUTED,
                                  halign="left", valign="middle", size_hint_x=0.45))
            row.add_widget(Label(text=ref_str, font_size=sp(11), color=TEXT_MUTED,
                                  halign="center", valign="middle", size_hint_x=0.3))
            row.add_widget(Label(text=val_str, font_size=sp(11.5), bold=True, color=TEXT,
                                  halign="right", valign="middle", size_hint_x=0.25))
            for lbl in row.children:
                lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
            return row

        ls_card.add_widget(ls_row("Flicker Faktoru", "<=%1", fifa.get("flicker_avg") or "-"))
        ls_card.add_widget(ls_row("Renk Gosterimi (CRI)", ">=80", fifa.get("colour_rendering_ra") or "-"))
        ls_card.add_widget(ls_row("Renk Sicakligi", "4000-6000K", fifa.get("colour_temp_tc") or "-"))
        ls_card.bind(minimum_height=ls_card.setter("height"))
        self.content_area.add_widget(ls_card)

        # --- Disa aktarma butonlari (FIFA/UEFA'da zaten vardi - FIBA'da UNUTULMUSTU) ---
        export_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        pdf_btn = FlatButton(text="PDF Olarak Kaydet", bg_color=ACCENT, font_size=sp(13))
        pdf_btn.bind(on_release=lambda b: self.export_pdf())
        excel_btn = FlatButton(text="Excel Olarak Kaydet", bg_color=ACCENT, font_size=sp(13))
        excel_btn.bind(on_release=lambda b: self.export_excel())
        export_row.add_widget(pdf_btn)
        export_row.add_widget(excel_btn)
        self.content_area.add_widget(export_row)

    def _compute_report_data(self):
        """Rapor icin tum hesaplamalari yapar - hem ekran hem PDF/Excel disa aktarimi bunu kullanir."""
        ms = self.measure_screen
        measured = {idx: d for idx, d in ms.measurements.items() if d["values"] is not None}
        if not measured:
            return None

        thresholds = STANDARDS[ms.org][ms.level]
        PLANE_LABELS = {
            "Eh": "Yatay (Eh)", "Ev0": "Dikey 0°", "Ev90": "Dikey 90°",
            "Ev180": "Dikey 180°", "Ev270": "Dikey 270°",
        }

        all_pass = True
        plane_groups = []
        fifa_metrics = {}
        for title, kind in PROBES:
            vals = [d["values"][title] for d in measured.values()]
            avg = sum(vals) / len(vals)
            vmin = min(vals)
            vmax = max(vals)
            u1 = (vmin / vmax) if vmax else 0
            u2 = (vmin / avg) if avg else 0
            fifa_metrics[title] = {"min": vmin, "max": vmax, "avg": avg, "u1": u1, "u2": u2}

            # Bazi FIFA egitim sahasi standartlarinda (Grade 2/3) Ev0/Ev180 icin
            # HICBIR gereksinim yok - yon-bazli bir esik varsa onu, yoksa PROBE
            # TURUNE (Eh/Ev) gore ortak esigi kullan. Hicbiri yoksa bu yonu ATLA
            # (yine de fifa_metrics'te ham deger olarak gorunur, sadece kriter
            # tablosuna eklenmez ve genel sonucu etkilemez).
            req_avg = thresholds.get(f"{title}_avg", thresholds.get(f"{kind}_avg"))
            if req_avg is None:
                plane_groups.append((PLANE_LABELS[title],
                                      [("Bu yon icin gereksinim yok", "-", f"{avg:.0f}", True)]))
                continue

            req_min = thresholds.get(f"{title}_min", thresholds.get(f"{kind}_min"))
            req_u1 = thresholds.get(f"{title}_u1",
                                     thresholds["u1h"] if kind == "Eh" else thresholds.get("u1v"))
            req_u2 = thresholds.get(f"{title}_u2",
                                     thresholds["u2h"] if kind == "Eh" else thresholds.get("u2v"))

            criteria = []
            avg_ok = avg >= req_avg
            criteria.append(("Ortalama >", f"{req_avg:.0f}", f"{avg:.0f}", avg_ok))
            if req_min is not None:
                min_ok = vmin >= req_min
                criteria.append(("Minimum >", f"{req_min:.0f}", f"{vmin:.0f}", min_ok))
            else:
                min_ok = True
            if req_u1 is not None:
                u1_ok = u1 >= req_u1
                criteria.append(("Uniformity U1", f"{req_u1:.2f}", f"{u1:.2f}", u1_ok))
            else:
                u1_ok = True
            if req_u2 is not None:
                u2_ok = u2 >= req_u2
                criteria.append(("Uniformity U2", f"{req_u2:.2f}", f"{u2:.2f}", u2_ok))
            else:
                u2_ok = True

            if not (avg_ok and min_ok and u1_ok and u2_ok):
                all_pass = False
            plane_groups.append((PLANE_LABELS[title], criteria))

        pos_to_gridno = {rc: idx + 1 for idx, rc in enumerate(ms.sequence)}

        maur_ratio = thresholds.get("maur_ratio")
        maur_max_fail = thresholds.get("maur_max_fail")
        maur_total_fail = 0
        maur_ok = True
        if maur_ratio is not None:
            for title, kind in PROBES:
                plane_pos = {(d["r"], d["c"]): d["values"][title] for d in measured.values()}
                plane_failures = compute_maur_failures(plane_pos, maur_ratio)
                fifa_metrics[title]["maur_fails"] = len(plane_failures)
                fifa_metrics[title]["maur_fail_details"] = [
                    {
                        "grid1": pos_to_gridno.get((r1, c1), "?"),
                        "grid2": pos_to_gridno.get((r2, c2), "?"),
                        "v1": v1, "v2": v2, "ratio": ratio,
                    }
                    for (r1, c1), (r2, c2), v1, v2, ratio in plane_failures
                ]
                maur_total_fail += len(plane_failures)
            maur_ok = maur_total_fail <= maur_max_fail
            if not maur_ok:
                all_pass = False
        else:
            for title, kind in PROBES:
                fifa_metrics[title]["maur_fails"] = None
                fifa_metrics[title]["maur_fail_details"] = []

        return {
            "measured_count": len(measured), "total_points": len(ms.sequence),
            "org": ms.org, "level": ms.level,
            "rows": ms.rows_count_val, "cols": ms.cols_count_val,
            "plane_groups": plane_groups, "all_pass": all_pass,
            "maur_ratio": maur_ratio, "maur_max_fail": maur_max_fail,
            "maur_total_fail": maur_total_fail, "maur_ok": maur_ok,
            "project_info": dict(ms.project_info),
            "fifa_info": dict(ms.fifa_info),
            "fifa_metrics": fifa_metrics,
            "raw_sequence": list(ms.sequence),
            "raw_measurements": {idx: dict(d) for idx, d in measured.items()},
            "rows_count": ms.rows_count_val,
            "cols_count": ms.cols_count_val,
        }

    def _compute_fiba_report_data(self):
        """FIBA icin ayri bir hesaplama - PPA/TPA iki ic ice bolge, MAUR yok,
        EH bir ARALIK, EV icin 4-yon dengesi var. FIFA/UEFA modeliyle
        KARISTIRILMAMALI - yapisi gercekten farkli (bkz. FIBA Official
        Basketball Rules 2024, Bolum 12)."""
        ms = self.measure_screen
        measured = {idx: d for idx, d in ms.measurements.items() if d["values"] is not None}
        if not measured:
            return None

        rows_n, cols_n = ms.rows_count_val, ms.cols_count_val
        margin = max(0, min(ms.fiba_ppa_margin, (min(rows_n, cols_n) - 1) // 2))

        def in_ppa(r, c):
            return margin <= r < rows_n - margin and margin <= c < cols_n - margin

        zone_points = {
            "PPA": {idx: d for idx, d in measured.items() if in_ppa(d["r"], d["c"])},
            "TPA": measured,
        }

        ev_dirs = ["Ev0", "Ev90", "Ev180", "Ev270"]
        zones_result = {}
        all_pass = True
        for zone_name, pts in zone_points.items():
            if not pts:
                zones_result[zone_name] = None
                continue
            th = FIBA_STANDARDS[zone_name]
            zone_data = {}

            # --- EC: AYRI, elle girilen tek-prob olcumu (ms.ec_values) ---
            ec_vals = [ms.ec_values[idx] for idx in pts.keys() if idx in ms.ec_values]
            ec_measured_count = len(ec_vals)
            if ec_vals:
                ec_avg = sum(ec_vals) / len(ec_vals)
                ec_min, ec_max = min(ec_vals), max(ec_vals)
                ec_u1 = (ec_min / ec_max) if ec_max else 0
                ec_u2 = (ec_min / ec_avg) if ec_avg else 0
                ec_ok = ec_avg >= th["ec_avg"] and ec_u1 >= th["ec_u1"] and ec_u2 >= th["ec_u2"]
            else:
                ec_avg = ec_min = ec_max = ec_u1 = ec_u2 = None
                ec_ok = False
            zone_data["EC"] = {"avg": ec_avg, "min": ec_min, "max": ec_max,
                                "u1": ec_u1, "u2": ec_u2, "ok": ec_ok,
                                "measured_count": ec_measured_count, "total_count": len(pts)}

            # --- EV: 4 yonun HER BIRI icin ayri ayri + yonler arasi denge ---
            ev_dir_avgs = {}
            ev_per_dir = {}
            ev_all_ok = True
            for d_name in ev_dirs:
                vals = [d["values"][d_name] for d in pts.values()]
                avg = sum(vals) / len(vals)
                vmin, vmax = min(vals), max(vals)
                u1 = (vmin / vmax) if vmax else 0
                u2 = (vmin / avg) if avg else 0
                ok = avg >= th["ev_avg"] and u1 >= th["ev_u1"] and u2 >= th["ev_u2"]
                if not ok:
                    ev_all_ok = False
                ev_per_dir[d_name] = {"avg": avg, "min": vmin, "max": vmax,
                                       "u1": u1, "u2": u2, "ok": ok}
                ev_dir_avgs[d_name] = avg
            dir_ratio = min(ev_dir_avgs.values()) / max(ev_dir_avgs.values()) if max(ev_dir_avgs.values()) else 0
            dir_ratio_ok = dir_ratio >= th["ev_dir_ratio"]
            if not dir_ratio_ok:
                ev_all_ok = False
            zone_data["EV"] = {"per_direction": ev_per_dir, "dir_ratio": dir_ratio,
                                "dir_ratio_ok": dir_ratio_ok, "ok": ev_all_ok}

            # --- EH: ortalama bir ARALIK icinde olmali (tek bir minimum degil) ---
            eh_vals = [d["values"]["Eh"] for d in pts.values() if d["values"].get("Eh") is not None]
            eh_measured_count = len(eh_vals)
            if eh_vals:
                eh_avg = sum(eh_vals) / len(eh_vals)
                eh_min, eh_max = min(eh_vals), max(eh_vals)
                eh_u1 = (eh_min / eh_max) if eh_max else 0
                eh_u2 = (eh_min / eh_avg) if eh_avg else 0
                eh_avg_ok = th["eh_avg_min"] <= eh_avg <= th["eh_avg_max"]
                eh_ok = eh_avg_ok and eh_u1 >= th["eh_u1"] and eh_u2 >= th["eh_u2"]
            else:
                eh_avg = eh_min = eh_max = eh_u1 = eh_u2 = None
                eh_avg_ok = False
                eh_ok = False
            zone_data["EH"] = {"avg": eh_avg, "min": eh_min, "max": eh_max,
                                "u1": eh_u1, "u2": eh_u2, "avg_ok": eh_avg_ok, "ok": eh_ok,
                                "measured_count": eh_measured_count, "total_count": len(pts)}

            zone_ok = ec_ok and ev_all_ok and eh_ok
            zone_data["zone_ok"] = zone_ok
            if not zone_ok:
                all_pass = False
            zones_result[zone_name] = zone_data

        return {
            "project_info": dict(ms.project_info),
            "fifa_info": dict(ms.fifa_info),
            "org": "FIBA", "level": "",
            "ppa_margin": margin,
            "zones": zones_result,
            "all_pass": all_pass,
            "measured_count": len(measured), "total_points": len(ms.sequence),
            "rows_count": rows_n, "cols_count": cols_n,
            "raw_sequence": list(ms.sequence),
            "raw_measurements": {idx: dict(d) for idx, d in measured.items()},
        }

    def _dataset_grid(self, raw_measurements, rows_n, cols_n, dataset_key):
        """Kontrol Panelindeki gorsel duzenle BIREBIR eslesen 2D veri gridi olusturur.
        Donen: grid[sutun_index][satir_index] = deger (sutun=0 en ustte, satir=0 en solda)."""

        grid = [[None] * rows_n for _ in range(cols_n)]
        for idx, d in raw_measurements.items():
            r, c = d["r"], d["c"]
            if 0 <= r < rows_n and 0 <= c < cols_n:
                grid[c][r] = d["values"].get(dataset_key)
        return grid

    def _build_report(self):
        self.content_area.clear_widgets()
        ms = self.measure_screen

        # --- Proje Bilgileri (her zaman gorunur, olcum olmasa bile duzenlenebilir) ---
        proj_card = Card(bg_color=CARD, radius=14, orientation="vertical",
                          padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(8),
                          size_hint_y=None)
        proj_card.add_widget(Label(text="Proje Bilgileri", font_size=sp(14), bold=True, color=TEXT,
                                    size_hint_y=None, height=dp(22), halign="left",
                                    text_size=(dp(300), None)))

        def make_field(label_text, key):
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
            lbl = Label(text=label_text, font_size=sp(12), color=TEXT_MUTED,
                        size_hint_x=0.36, halign="left", valign="middle")
            lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
            row.add_widget(lbl)
            field_card = Card(bg_color=CARD_LIGHT, radius=8)
            ti = ThemedTextInput(text=ms.project_info.get(key, ""), multiline=False, font_size=sp(13))

            def on_focus(instance, value, k=key):
                if not value:
                    ms.project_info[k] = instance.text
                    ms.save_session()
            ti.bind(focus=on_focus)
            field_card.add_widget(ti)
            row.add_widget(field_card)
            return row

        proj_card.add_widget(make_field("Stadyum/Tesis", "name"))
        proj_card.add_widget(make_field("Ulke / Sehir", "location"))
        proj_card.add_widget(make_field("Olcum Tarihi", "date"))
        proj_card.add_widget(make_field("Hazirlayan", "prepared_by"))
        proj_card.bind(minimum_height=proj_card.setter("height"))
        self.content_area.add_widget(proj_card)

        fifa_btn = FlatButton(text="Ek Rapor Bilgilerini Duzenle", bg_color=ACCENT,
                               font_size=sp(13), bold=True, size_hint_y=None, height=dp(46))
        fifa_btn.bind(on_release=lambda b: self._open_fifa_info_popup())
        self.content_area.add_widget(fifa_btn)

        lang_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        lang_label = Label(text="Rapor Dili:", font_size=sp(13), color=TEXT_MUTED,
                            size_hint_x=0.35, halign="left", valign="middle")
        lang_label.bind(size=lambda i, v: setattr(i, "text_size", v))
        lang_row.add_widget(lang_label)
        self.lang_btn = FlatButton(
            text="Turkce" if ms.report_language == "tr" else "English",
            bg_color=CARD_LIGHT, font_size=sp(13), bold=True)
        self.lang_btn.bind(on_release=lambda b: self._toggle_report_language())
        lang_row.add_widget(self.lang_btn)
        self.content_area.add_widget(lang_row)

        measured = {idx: d for idx, d in ms.measurements.items() if d["values"] is not None}
        total_points = len(ms.sequence)

        if not measured:
            msg = Label(text="Henuz olcum yok.\nOlcum girildikce karsilastirma\nburada olusacak.",
                        font_size=sp(14), color=TEXT_MUTED, halign="center",
                        size_hint_y=None, height=dp(70))
            msg.bind(size=lambda i, v: setattr(i, "text_size", v))
            self.content_area.add_widget(msg)
            return

        if ms.org == "FIBA":
            self._build_fiba_report_section(measured, total_points)
            return

        thresholds = STANDARDS[ms.org][ms.level]

        # --- Bilgi karti (standart + izgara) ---
        info_card = Card(bg_color=CARD, radius=14, orientation="vertical",
                          padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(4),
                          size_hint_y=None)
        info_card.add_widget(Label(text=f"Standart: {ms.org} - {ms.level}", font_size=sp(14),
                                    bold=True, color=TEXT, size_hint_y=None, height=dp(22),
                                    halign="left", text_size=(dp(300), None)))
        is_incomplete = len(measured) < total_points
        count_color = RED_TXT if is_incomplete else GREEN_TXT
        count_label = Label(text=f"Izgara: {ms.rows_count_val} x {ms.cols_count_val}   |   "
                                  f"Olculen: {len(measured)}/{total_points} nokta"
                                  + ("  (EKSIK)" if is_incomplete else ""),
                             font_size=sp(12.5), color=count_color, bold=is_incomplete,
                             size_hint_y=None, height=dp(20), halign="left",
                             text_size=(dp(300), None))
        info_card.add_widget(count_label)
        info_card.bind(minimum_height=info_card.setter("height"))
        self.content_area.add_widget(info_card)

        data = self._compute_report_data()
        plane_groups = data["plane_groups"]
        all_pass = data["all_pass"]
        maur_ratio = data["maur_ratio"]
        maur_max_fail = data["maur_max_fail"]
        maur_total_fail = data["maur_total_fail"]
        maur_ok = data["maur_ok"]

        # --- Genel sonuc banner ---
        verdict_card = Card(bg_color=SUCCESS_TINT if all_pass else DANGER_TINT,
                             radius=14, border_color=SUCCESS if all_pass else DANGER,
                             size_hint_y=None, height=dp(56), padding=[dp(16), 0, dp(16), 0])
        verdict_text = ("KRITERLERI KARSILIYOR" if all_pass else "KRITERLERI KARSILAMIYOR")
        verdict_card.add_widget(Label(text=verdict_text, font_size=sp(16), bold=True,
                                       color=GREEN_TXT if all_pass else RED_TXT))
        self.content_area.add_widget(verdict_card)

        # --- Detay tablosu: her duzlem icin Kriter / Referans / Olculen / Sonuc ---
        table_card = Card(bg_color=CARD, radius=14, orientation="vertical", padding=0,
                           size_hint_y=None)
        COLW = [0.34, 0.20, 0.20, 0.26]

        def add_wide_row(container, text, bg):
            wrap = TableRow(bg)
            lbl = Label(text=text, font_size=sp(12.5), bold=True, color=TEXT)
            wrap.add_widget(lbl)
            container.add_widget(wrap)

        header = TableRow(HEADER_BG)
        header.cell_labels = []
        for i, h in enumerate(["Kriter", "Referans", "Olculen", "Sonuc"]):
            w = COLW[i]
            lbl = Label(text=h, font_size=sp(11.5), bold=True, color=TEXT_MUTED, size_hint_x=w)
            header.add_widget(lbl)
            header.cell_labels.append(lbl)
        table_card.add_widget(header)

        for plane_title, criteria in plane_groups:
            add_wide_row(table_card, plane_title, HEADER_BG)
            for pos, (kriter, referans, olculen, ok) in enumerate(criteria):
                row_bg = ROW_A if pos % 2 == 0 else ROW_B
                row = TableRow(row_bg)
                row.cell_labels = []
                for i, (txt, col) in enumerate([
                    (kriter, TEXT_MUTED), (referans, TEXT_MUTED),
                    (olculen, GREEN_TXT if ok else RED_TXT),
                    ("UYGUN" if ok else "UYGUN DEGIL", GREEN_TXT if ok else RED_TXT),
                ]):
                    lbl = Label(text=txt, font_size=sp(11.5), bold=(i >= 2), color=col,
                                size_hint_x=COLW[i])
                    row.add_widget(lbl)
                    row.cell_labels.append(lbl)
                table_card.add_widget(row)

        table_card.bind(minimum_height=table_card.setter("height"))
        self.content_area.add_widget(table_card)

        # --- MAUR karti ---
        maur_card = Card(bg_color=CARD, radius=14, orientation="vertical",
                          padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(6),
                          size_hint_y=None)
        maur_card.add_widget(Label(text="MAUR - Komsu Nokta Tekduzeligi", font_size=sp(13.5),
                                    bold=True, color=TEXT, size_hint_y=None, height=dp(20),
                                    halign="left", text_size=(dp(300), None)))
        if maur_ratio is None:
            maur_card.add_widget(Label(text="Bu standart seviyesi icin MAUR belirtilmemis.",
                                        font_size=sp(12.5), color=TEXT_MUTED, size_hint_y=None,
                                        height=dp(20), halign="left", text_size=(dp(300), None)))
        else:
            maur_card.add_widget(Label(
                text=f"Toplam hata (5 duzlem): {maur_total_fail}   /   izin verilen {maur_max_fail}",
                font_size=sp(12.5), color=TEXT_MUTED, halign="left",
                text_size=(dp(300), None), size_hint_y=None, height=dp(20)))
            maur_card.add_widget(Label(text="UYGUN" if maur_ok else "UYGUN DEGIL",
                                        font_size=sp(14), bold=True, halign="left",
                                        text_size=(dp(300), None), size_hint_y=None, height=dp(22),
                                        color=GREEN_TXT if maur_ok else RED_TXT))
        maur_card.bind(minimum_height=maur_card.setter("height"))
        self.content_area.add_widget(maur_card)

        # --- Disa aktarma butonlari ---
        export_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        pdf_btn = FlatButton(text="PDF Olarak Kaydet", bg_color=ACCENT, font_size=sp(13))
        pdf_btn.bind(on_release=lambda b: self.export_pdf())
        excel_btn = FlatButton(text="Excel Olarak Kaydet", bg_color=ACCENT, font_size=sp(13))
        excel_btn.bind(on_release=lambda b: self.export_excel())
        export_row.add_widget(pdf_btn)
        export_row.add_widget(excel_btn)
        self.content_area.add_widget(export_row)


class PlaceholderScreen(Screen):
    def __init__(self, message, **kwargs):
        super().__init__(**kwargs)
        box = BoxLayout(orientation="vertical", padding=dp(24))
        lbl = Label(text=message, font_size=sp(16), color=TEXT_MUTED, halign="center")
        lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        box.add_widget(lbl)
        self.add_widget(box)


# ---------------------------------------------------------
# ANA UYGULAMA + OZEL ALT NAVIGASYON
# ---------------------------------------------------------
class SettingsScreen(Screen):
    def __init__(self, measure_screen, **kwargs):
        super().__init__(**kwargs)
        self.measure_screen = measure_screen

        with self.canvas.before:
            Color(*BG)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)

        outer = BoxLayout(orientation="vertical", padding=[dp(16), dp(50), dp(16), dp(16)],
                           spacing=dp(14))

        title = Label(text="Ayarlar", font_size=sp(22), bold=True, color=TEXT,
                       size_hint_y=None, height=dp(36), halign="left")
        title.bind(size=lambda i, v: setattr(i, "text_size", v))
        outer.add_widget(title)

        # --- Gorunum bolumu ---
        section_lbl = Label(text="GORUNUM", font_size=sp(12), color=TEXT_MUTED, bold=True,
                             size_hint_y=None, height=dp(24), halign="left")
        section_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        outer.add_widget(section_lbl)

        theme_card = Card(bg_color=CARD, radius=12, size_hint_y=None, height=dp(64),
                           padding=[dp(16), dp(0), dp(12), dp(0)])
        theme_row = BoxLayout()
        theme_label_box = BoxLayout(orientation="vertical")
        theme_title = Label(text="Gece Modu" if CURRENT_THEME == "dark" else "Gunduz Modu",
                             font_size=sp(15), color=TEXT, halign="left", valign="middle")
        theme_title.bind(size=lambda i, v: setattr(i, "text_size", v))
        theme_sub = Label(text="Sahada gun isiginda okunabilirlik icin Gunduz Modu'nu secin",
                           font_size=sp(11.5), color=TEXT_MUTED, halign="left", valign="middle")
        theme_sub.bind(size=lambda i, v: setattr(i, "text_size", v))
        theme_label_box.add_widget(theme_title)
        theme_label_box.add_widget(theme_sub)
        theme_row.add_widget(theme_label_box)

        self.theme_toggle_btn = FlatButton(
            text="Gunduz" if CURRENT_THEME == "dark" else "Gece",
            bg_color=ACCENT, font_size=sp(13), bold=True,
            size_hint=(None, None), size=(dp(90), dp(40)))
        self.theme_toggle_btn.bind(on_release=self._on_toggle_theme)
        theme_btn_anchor = AnchorLayout(anchor_x="center", anchor_y="center",
                                         size_hint_x=None, width=dp(90))
        theme_btn_anchor.add_widget(self.theme_toggle_btn)
        theme_row.add_widget(theme_btn_anchor)
        theme_card.add_widget(theme_row)
        outer.add_widget(theme_card)

        # --- Uygulama Hakkinda bolumu ---
        about_section_lbl = Label(text="UYGULAMA", font_size=sp(12), color=TEXT_MUTED, bold=True,
                                   size_hint_y=None, height=dp(24), halign="left")
        about_section_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        outer.add_widget(about_section_lbl)

        about_card = Card(bg_color=CARD, radius=12, orientation="vertical", size_hint_y=None,
                           height=dp(96), padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(6))

        def about_row(label_text, value_text):
            row = BoxLayout(size_hint_y=None, height=dp(22))
            l = Label(text=label_text, font_size=sp(12.5), color=TEXT_MUTED, halign="left")
            l.bind(size=lambda i, v: setattr(i, "text_size", v))
            v = Label(text=value_text, font_size=sp(12.5), color=TEXT, halign="right", bold=True)
            v.bind(size=lambda i, v2: setattr(i, "text_size", v2))
            row.add_widget(l)
            row.add_widget(v)
            return row

        about_card.add_widget(about_row("Surum", "v45"))
        about_card.add_widget(about_row("Gelistiren", "Kerem Akgun"))
        about_card.add_widget(about_row("Cihaz", "Konica Minolta T-10MA"))
        outer.add_widget(about_card)

        # --- Veri Yonetimi: tum olcum verisini disa/ice aktar ---
        data_section_lbl = Label(text="VERI YONETIMI", font_size=sp(12), color=TEXT_MUTED, bold=True,
                                  size_hint_y=None, height=dp(24), halign="left")
        data_section_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        outer.add_widget(data_section_lbl)

        data_info_lbl = Label(text="Tum olcum verisini (proje, izgara, FIFA bilgileri dahil) "
                                    "yedekleyin veya daha once yedeklenmis bir dosyayi geri yukleyin.",
                               font_size=sp(11.5), color=TEXT_MUTED, size_hint_y=None, height=dp(36),
                               halign="left", valign="top")
        data_info_lbl.bind(size=lambda i, v: setattr(i, "text_size", (v[0], None)))
        outer.add_widget(data_info_lbl)

        def get_report_screen():
            return App.get_running_app().root.sm.get_screen("report")

        data_btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        export_data_btn = FlatButton(text="Verileri Disa Aktar", bg_color=CARD_LIGHT,
                                      font_size=sp(12.5), bold=True)
        export_data_btn.bind(on_release=lambda b: get_report_screen().export_data_json())
        import_data_btn = FlatButton(text="Verileri Ice Aktar", bg_color=CARD_LIGHT,
                                      font_size=sp(12.5), bold=True)
        import_data_btn.bind(on_release=lambda b: get_report_screen().import_data_json())
        data_btn_row.add_widget(export_data_btn)
        data_btn_row.add_widget(import_data_btn)
        outer.add_widget(data_btn_row)

        # --- Bilgi notu (ileride baska ayarlar buraya eklenecek) ---
        info_lbl = Label(text="Daha fazla ayar yakinda eklenecek.",
                          font_size=sp(12), color=TEXT_MUTED,
                          size_hint_y=None, height=dp(24), halign="left")
        info_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        outer.add_widget(info_lbl)

        outer.add_widget(Widget())  # kalan alani doldur
        self.add_widget(outer)

    def _update_bg(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _on_toggle_theme(self, *a):
        new_theme = "light" if CURRENT_THEME == "dark" else "dark"
        try:
            self.measure_screen.save_session()  # once mevcut veriyi kaydet
        except Exception:
            pass
        apply_palette(new_theme)
        try:
            self.measure_screen.save_session()  # yeni tema tercihini de kaydet
        except Exception:
            pass
        App.get_running_app().rebuild_ui()


class RootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        with self.canvas.before:
            Color(*BG)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.sm = ScreenManager(transition=NoTransition())
        self.measure_screen = MeasureScreen(name="measure",
                                             on_open_standards=lambda: self.switch_tab("standards"))
        self.sm.add_widget(self.measure_screen)
        self.sm.add_widget(StandardsScreen(measure_screen=self.measure_screen, name="standards"))
        self.sm.add_widget(ControlScreen(measure_screen=self.measure_screen, name="control"))
        self.sm.add_widget(ReportScreen(measure_screen=self.measure_screen, name="report"))
        self.sm.add_widget(SettingsScreen(measure_screen=self.measure_screen, name="settings"))
        self.add_widget(self.sm)

        nav_card = Card(bg_color=NAV_BG, radius=0, size_hint_y=None,
                         height=dp(66), padding=[dp(4), dp(6), dp(4), dp(6)])
        nav_row = BoxLayout(spacing=dp(2))
        nav_card.add_widget(nav_row)

        self.tabs = {}
        tab_defs = [
            ("measure", "measure", "Olcum"),
            ("control", "result", "Sonuc"),
            ("standards", "standards", "Standart"),
            ("report", "report", "Rapor"),
            ("settings", "settings", "Ayarlar"),
        ]
        for screen_name, icon_kind, label in tab_defs:
            btn = NavButton(icon_kind, label, on_press=lambda sn=screen_name: self.switch_tab(sn))
            nav_row.add_widget(btn)
            self.tabs[screen_name] = btn

        self.add_widget(nav_card)
        self.switch_tab("measure")

    def _update_bg(self, *a):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def switch_tab(self, name):
        self.sm.current = name
        for k, btn in self.tabs.items():
            btn.set_active(k == name)


class AydinlatmaApp(App):
    def build(self):
        # Klavye acilinca, o an odaklanilan alanin (TextInput) klavyenin
        # ARKASINDA KALMAMASI icin Kivy'nin otomatik ayarlamasini ac.
        # Varsayilan bos ('') modda Kivy hicbir ayarlama yapmaz - klavye
        # dogrudan icerigin ustune biner ve doldurulan alan gorunmez olurdu.
        from kivy.core.window import Window as _Win
        _Win.softinput_mode = "below_target"
        apply_palette(load_saved_theme())
        return RootLayout()

    def rebuild_ui(self):
        """Tema degistiginde TUM arayuzu (verileri kaybetmeden - oturum
        dosyasindan geri yukleyerek) yeniden insa eder."""
        from kivy.core.window import Window
        old_root = self.root
        new_root = RootLayout()
        self.root = new_root
        Window.remove_widget(old_root)
        Window.add_widget(new_root)


if __name__ == "__main__":
    AydinlatmaApp().run()
