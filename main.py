# Aydinlatma Olcum Paneli - v6
# Olcum ekrani: Konsept 2 (kartli ust bolum) + Konsept 4 (kompakt tablo) birlesimi.
# Standart secimi bu ekrandan kaldirildi -> ust rozete tasindi, dokunulunca
# Standartlar sekmesine gecer (secim islemi bir sonraki adimda o sekmede yapilacak).

import random
import json
import os
import socket
import threading
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
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
from kivy.graphics.texture import Texture
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse
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
ROW_A = (0.082, 0.082, 0.094, 1)
ROW_B = (0.102, 0.102, 0.122, 1)
HEADER_BG = (0.13, 0.13, 0.15, 1)

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


# ---------------------------------------------------------
# ORTAK GORSEL BILESENLER
# ---------------------------------------------------------
class Card(BoxLayout):
    def __init__(self, bg_color=CARD, radius=14, border_color=None, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        with self.canvas.before:
            self.bg_instr = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
            if border_color:
                Color(*border_color)
                self.border_line = Line(width=1.3)
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
        kwargs.setdefault('color', TEXT)
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
            elif self.kind == "control":
                for i, frac in enumerate([0.75, 0.5, 0.25]):
                    yy = y + h * frac
                    Line(points=[x + w * 0.1, yy, x + w * 0.9, yy], width=1.4)
                    knob_x = x + w * (0.3 + i * 0.2)
                    Ellipse(pos=(knob_x - dp(3), yy - dp(3)), size=(dp(6), dp(6)))
            elif self.kind == "report":
                Line(rounded_rectangle=(x + w * 0.18, y + h * 0.06, w * 0.64, h * 0.88, 3), width=1.6)
                for frac in [0.68, 0.52, 0.36]:
                    Line(points=[x + w * 0.3, y + h * frac, x + w * 0.7, y + h * frac], width=1.3)


class NavButton(BoxLayout):
    def __init__(self, kind, label, on_press, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.on_press_cb = on_press
        self.icon = TabIcon(kind)
        icon_wrap = BoxLayout(size_hint_y=0.6)
        icon_wrap.add_widget(Widget())
        icon_wrap.add_widget(self.icon)
        icon_wrap.add_widget(Widget())
        self.add_widget(icon_wrap)
        self.label = Label(text=label, font_size=sp(11.5), size_hint_y=0.4, color=TEXT_MUTED)
        self.add_widget(self.label)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.on_press_cb()
            return True
        return super().on_touch_down(touch)

    def set_active(self, active):
        self.icon.set_active(active)
        self.label.color = ACCENT if active else TEXT_MUTED


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


STATUS_BG = {
    "connected": (0.055, 0.11, 0.075, 1),
    "device_silent": (0.12, 0.09, 0.045, 1),
    "disconnected": (0.13, 0.065, 0.07, 1),
    "checking": (0.10, 0.10, 0.06, 1),
}


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
        self.label.text = STATUS_LABELS.get(status, status)
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
                                size_hint_y=None, height=dp(58), padding=[dp(16), 0, dp(16), 0])
        point_row = BoxLayout()
        point_row.add_widget(Label(text="Aktif nokta", font_size=sp(13), color=(0.6, 0.85, 0.7, 1),
                                    size_hint_x=0.45))
        self.active_point_label = Label(text="Izgarayi baslatin", font_size=sp(15), bold=True, color=TEXT)
        point_row.add_widget(self.active_point_label)
        self.point_card.add_widget(point_row)
        root.add_widget(self.point_card)

        # --- OLC butonu ---
        self.measure_btn = FlatButton(text="OLCUM AL", bg_color=SUCCESS, radius=14,
                                       font_size=sp(18), bold=True,
                                       size_hint_y=None, height=dp(58))
        self.measure_btn.bind(on_release=self.take_measurement)
        root.add_widget(self.measure_btn)

        # --- Tablo (Konsept 4 stili) ---
        table_card = Card(bg_color=CARD, radius=14, orientation="vertical", padding=0)
        self.header_row = TableRow(HEADER_BG)
        for h in COL_HEADERS:
            self.header_row.add_cell(h, color=TEXT_MUTED, bold=True)
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
        self.project_info = {"name": "", "location": "", "date": "", "prepared_by": ""}
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
    def _session_path(self):
        try:
            app = App.get_running_app()
            return os.path.join(app.user_data_dir, "aydinlatma_session.json")
        except Exception:
            return None

    def save_session(self):
        path = self._session_path()
        if not path:
            return
        try:
            data = {
                "org": self.org, "level": self.level,
                "rows": self.rows_count_val, "cols": self.cols_count_val,
                "frontier_index": self.frontier_index,
                "measurements": {str(k): v for k, v in self.measurements.items()},
                "project_info": self.project_info,
                "pi_ip": self.pi_ip,
                "pi_port": self.pi_port,
                "saved_at": datetime.now().isoformat(),
            }
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
            self.org = data.get("org", self.org)
            self.level = data.get("level", self.level)
            self.rows_count_val = data.get("rows", self.rows_count_val)
            self.cols_count_val = data.get("cols", self.cols_count_val)
            self.project_info.update(data.get("project_info", {}))
            self.pi_ip = data.get("pi_ip", self.pi_ip)
            self.pi_port = data.get("pi_port", self.pi_port)
            self.grid_value_label.text = f"{self.rows_count_val} x {self.cols_count_val}"
            self.badge_label.text = f"{self.org} \u00b7 {self.level}"
            raw_meas = data.get("measurements", {})
            if not raw_meas:
                return
            self.measurements = {int(k): v for k, v in raw_meas.items()}
            self.frontier_index = data.get("frontier_index", 0)
            self.sequence = build_measurement_sequence(self.rows_count_val, self.cols_count_val)
            self.current_index = self.frontier_index
            self.row_widgets = {}
            self.table_body.clear_widgets()
            for idx in sorted(self.measurements.keys()):
                self._render_row(idx)
            self.measure_btn.disabled = False
            self._update_active_label()
        except Exception:
            pass  # bozuk/eksik kayit dosyasi uygulamayi cokertmesin

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
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))

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

        popup = Popup(title="Baglanti Ayarlari", content=content, size_hint=(0.88, 0.48),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0.08, 0.08, 0.10, 1))

        def do_connect(*a):
            if connect_btn.disabled:
                return  # zaten bir baglanti denemesi suruyor
            new_ip = ip_input.text.strip()
            new_port_text = port_input.text.strip() or "8899"
            connect_btn.disabled = True
            connect_btn.text = "Baglaniliyor..."
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
        self.badge_label.text = f"{org} · {level}"
        self.save_session()

    # --- Izgara duzenleme penceresi ---
    def _open_grid_editor(self):
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(14))

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

        popup = Popup(title="Izgara Ayarlari", content=content, size_hint=(0.85, 0.52),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0.08, 0.08, 0.10, 1))

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
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(16))
        content.add_widget(Label(
            text=f"Izgara boyutu {new_rows} x {new_cols} olarak degistirilecek.\n"
                 f"Mevcut {len(self.measurements)} olcum silinecek.\nEmin misiniz?",
            font_size=sp(14.5), color=TEXT, halign="center"))
        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        popup = Popup(title="Izgara Boyutunu Degistir", content=content, size_hint=(0.85, 0.44),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0.08, 0.08, 0.10, 1))
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
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(16))
        content.add_widget(Label(
            text="Tum olcum tablosu silinecek.\nBu islem geri alinamaz. Emin misiniz?",
            font_size=sp(15), color=TEXT, halign="center"))
        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        popup = Popup(title="Sifirla", content=content, size_hint=(0.85, 0.4),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0.08, 0.08, 0.10, 1))
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
        if clear_table:
            self.measurements = {}
            self.refresh_table()
        if start:
            self.measure_btn.disabled = False
            self._update_active_label()
        else:
            self.active_point_label.text = "Izgarayi baslatin"
            self.measure_btn.disabled = True

    def _update_active_label(self):
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

    def take_measurement(self, *a):
        if self.current_index >= len(self.sequence):
            return
        self.measure_btn.disabled = True
        self.measure_btn.text = "OLCUM ALINIYOR..."
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
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(14))
        content.add_widget(Label(text=message, font_size=sp(14), color=TEXT, halign="center"))
        popup = Popup(title="Baglanti Sorunu", content=content, size_hint=(0.85, 0.42),
                       auto_dismiss=True, separator_color=BORDER, title_color=TEXT,
                       background_color=(0.08, 0.08, 0.10, 1))
        close_btn = FlatButton(text="Tamam", bg_color=ACCENT, font_size=sp(14),
                                size_hint_y=None, height=dp(46))
        close_btn.bind(on_release=lambda b: popup.dismiss())
        content.add_widget(close_btn)
        popup.open()

    def refresh_table(self):
        """Sadece TAM sifirlamada kullanilir - tabloyu bosaltir."""
        self.table_body.clear_widgets()
        self.row_widgets = {}

    def _render_row(self, idx):
        """Tek bir noktanin satirini olusturur veya (varsa) yerinde gunceller. O(1)."""
        data = self.measurements[idx]
        if idx in self.row_widgets:
            row = self.row_widgets[idx]
            if data["values"] is None:
                for i in range(1, 6):
                    row.update_cell(i, "--", color=TEXT_MUTED)
            else:
                for i, (title, kind) in enumerate(PROBES, start=1):
                    row.update_cell(i, str(data["values"][title]), color=TEXT)
            return

        pos = len(self.row_widgets)
        row_bg = ROW_A if pos % 2 == 0 else ROW_B
        row = TableRow(row_bg, point_index=idx, on_tap=self._row_tapped)
        row.add_cell(str(idx + 1), color=TEXT_MUTED)
        if data["values"] is None:
            for _ in PROBES:
                row.add_cell("--", color=TEXT_MUTED)
        else:
            for title, kind in PROBES:
                row.add_cell(str(data["values"][title]), color=TEXT, bold=True)
        self.table_body.add_widget(row)
        self.row_widgets[idx] = row

    def _row_tapped(self, point_index):
        data = self.measurements.get(point_index)
        if not data:
            return

        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        content.add_widget(Label(
            text=f"Grid No {point_index + 1}",
            font_size=sp(16), bold=True, color=TEXT, size_hint_y=None, height=dp(28)))

        popup = Popup(title="Nokta Islemleri", content=content, size_hint=(0.85, 0.46),
                       auto_dismiss=True, separator_color=BORDER, title_color=TEXT,
                       background_color=(0.08, 0.08, 0.10, 1))

        remeasure_btn = FlatButton(text="Bu Noktayi Yeniden Olc", bg_color=ACCENT,
                                    font_size=sp(14.5), size_hint_y=None, height=dp(50))

        def do_remeasure(*a):
            popup.dismiss()
            self.current_index = point_index
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
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(16))
        content.add_widget(Label(
            text=f"Grid No {point_index + 1} noktasinin olcumu sifirlanacak.\nEmin misiniz?",
            font_size=sp(15), color=TEXT, halign="center"))
        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        popup = Popup(title="Noktayi Sifirla", content=content, size_hint=(0.85, 0.4),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0.08, 0.08, 0.10, 1))
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

        if values["Eh_min"] is not None:
            eh_line = f"1. Eh (yatay):  min {values['Eh_min']} lx / ort {values['Eh_avg']} lx"
        else:
            eh_line = f"1. Eh (yatay):  ort >= {values['Eh_avg']} lx"
        uh_line = f"    Duzgunluk: U1h >= {values['u1h']}   U2h >= {values['u2h']}"

        ev_line = f"2. Ev (0/90/180/270 - hepsi ayni):  min {values['Ev_min']} lx / ort {values['Ev_avg']} lx"
        if values['u1v'] is not None:
            uv_line = f"    Duzgunluk: U1v >= {values['u1v']}   U2v >= {values['u2v']}"
        else:
            uv_line = "    Duzgunluk: belirtilmemis"

        maur_line = f"3. Komsu Nokta Duzgunluk Orani (MAUR):  {values['maur']}"
        cct_line = f"4. Renk sicakligi (Tc):  {values['cct']}"
        ra_line = f"5. Renk gosterimi (Ra):  >= {values['ra']}"

        primary_text = "\n".join([eh_line, uh_line, ev_line, uv_line, maur_line, cct_line, ra_line])

        self.primary = Label(text=primary_text, font_size=sp(11.5), color=TEXT_MUTED,
                              halign="left", valign="top",
                              text_size=(dp(288), None), size_hint_y=None)
        self.primary.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1]))
        self.add_widget(self.primary)

        # --- Daha az sik kullanilan alanlar: dokununca acilir/kapanir ---
        mcm_line = f"Mac Sureklilik Modu (MCM):  {values['mcm']}"
        ff_line = f"Titresim Faktoru (FF):  {values['ff']}"
        rg_line = f"Kamasma orani (RG):  {values['rg']}"
        mf_line = f"Bakim faktoru (MF):  {values['mf']}"
        self.extra_text = "\n".join([mcm_line, ff_line, rg_line, mf_line])

        self.expanded = False
        self.toggle_label = Label(text="Tum Detaylar (MCM, FF, RG, MF)  v",
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
            self.toggle_label.text = "Tum Detaylar (MCM, FF, RG, MF)  ^"
            self.extra_label.text = self.extra_text
        else:
            self.toggle_label.text = "Tum Detaylar (MCM, FF, RG, MF)  v"
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
                                     color=(0.6, 0.85, 0.7, 1), size_hint_x=0.5))
        self.active_label = Label(text=f"{measure_screen.org} · {measure_screen.level}",
                                   font_size=sp(15), bold=True, color=TEXT)
        active_row.add_widget(self.active_label)
        self.active_card.add_widget(active_row)
        root.add_widget(self.active_card)

        # --- Organizasyon secici ---
        org_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        self.org_buttons = {}
        for org_name in STANDARDS.keys():
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

    def set_browse_org(self, org_name):
        self.browse_org = org_name
        for name, btn in self.org_buttons.items():
            btn.bg_instr.rgba = ACCENT if name == org_name else CARD_LIGHT
            btn._base_color = ACCENT if name == org_name else CARD_LIGHT

        self.level_list.clear_widgets()
        self.level_cards = {}
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

    def preview_select(self, org, level):
        self.browse_org = org
        self.preview_level = level
        self._refresh_selection_marks()

    def _refresh_selection_marks(self):
        for name, card in self.level_cards.items():
            card.set_selected(name == self.preview_level)

    def apply_standard(self, *a):
        if not self.preview_level:
            return
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(16))
        content.add_widget(Label(
            text=f"Aktif standart\n{self.browse_org} - {self.preview_level}\nolarak degistirilecek. Emin misiniz?",
            font_size=sp(15), color=TEXT, halign="center"))
        btn_row = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        popup = Popup(title="Standardi Uygula", content=content, size_hint=(0.85, 0.42),
                       auto_dismiss=False, separator_color=BORDER, title_color=TEXT,
                       background_color=(0.08, 0.08, 0.10, 1))
        cancel_btn = FlatButton(text="Vazgec", bg_color=CARD_LIGHT, font_size=sp(14))
        confirm_btn = FlatButton(text="Evet, Uygula", bg_color=ACCENT, font_size=sp(14))
        cancel_btn.bind(on_release=lambda b: popup.dismiss())

        def do_confirm(*a):
            popup.dismiss()
            self.measure_screen.update_standard_badge(self.browse_org, self.preview_level)
            self.active_label.text = f"{self.browse_org} · {self.preview_level}"
        confirm_btn.bind(on_release=do_confirm)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        content.add_widget(btn_row)
        popup.open()

    def on_pre_enter(self, *a):
        # sekmeye her girildiginde aktif standardi tekrar yansit
        self.active_label.text = f"{self.measure_screen.org} · {self.measure_screen.level}"


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
    """DIALux/Relux tarzi 'false color' - dusuk deger mavi/mor, yuksek deger kirmizi/turuncu."""
    if vmax <= vmin:
        t = 0.5
    else:
        t = (value - vmin) / (vmax - vmin)
    t = max(0.0, min(1.0, t))
    stops = [
        (0.20, 0.20, 0.55, 1),   # koyu mor/lacivert (dusuk)
        (0.15, 0.45, 0.80, 1),   # mavi
        (0.20, 0.70, 0.65, 1),   # camgobegi
        (0.30, 0.75, 0.30, 1),   # yesil
        (0.90, 0.85, 0.20, 1),   # sari
        (0.90, 0.45, 0.15, 1),   # turuncu
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

    DATASETS = ["Eh", "Ev0", "Ev90", "Ev180", "Ev270"]

    def __init__(self, measure_screen, **kwargs):
        super().__init__(**kwargs)
        self.measure_screen = measure_screen
        self.current_dataset = "Eh"
        self.zoom = 1.0
        self.base_cell_size = dp(42)
        self.label_font_size = 12.5

        self.root_box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        self.root_box.add_widget(Label(text="Kontrol Paneli", font_size=sp(20), bold=True,
                                        color=TEXT, size_hint_y=None, height=dp(32)))

        # --- Veri seti secici (Eh / Ev0 / Ev90 / Ev180 / Ev270) ---
        selector_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(4))
        self.dataset_buttons = {}
        for name in self.DATASETS:
            btn = FlatButton(text=name, bg_color=CARD_LIGHT, font_size=sp(12.5))
            btn.bind(on_release=lambda b, n=name: self.set_dataset(n))
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

    def change_zoom(self, delta):
        self.zoom = max(0.5, min(2.6, round(self.zoom + delta, 2)))
        self.zoom_label.text = f"{int(self.zoom * 100)}%"
        self._build_heatmap()

    def toggle_maur(self):
        self.maur_mode = not self.maur_mode
        self.maur_btn.bg_instr.rgba = ACCENT if self.maur_mode else CARD_LIGHT
        self.maur_btn._base_color = ACCENT if self.maur_mode else CARD_LIGHT
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
            btn.bg_instr.rgba = ACCENT if active else CARD_LIGHT
            btn._base_color = ACCENT if active else CARD_LIGHT

    def on_pre_enter(self, *a):
        self._build_heatmap()

    def _build_heatmap(self):
        self.content_area.clear_widgets()
        ms = self.measure_screen
        satir_n, sutun_n = ms.rows_count_val, ms.cols_count_val

        by_pos = {}
        for data in ms.measurements.values():
            if data["values"] is not None:
                by_pos[(data["r"], data["c"])] = data["values"][self.current_dataset]

        if not by_pos:
            msg = Label(text="Henuz olcum yok.\nOlcum Verisi sekmesinden\nizgarayi baslatip olcum alin.",
                        font_size=sp(15), color=TEXT_MUTED, halign="center")
            msg.bind(size=lambda i, v: setattr(i, "text_size", v))
            self.content_area.add_widget(msg)
            return

        vmin, vmax = min(by_pos.values()), max(by_pos.values())
        thresholds = STANDARDS[ms.org][ms.level]

        # --- KRITIK EKSEN KURALI ---
        # Ekranda: SUTUN sayisi DIKEY (yukaridan asagi), SATIR sayisi YATAY (soldan saga).
        # "r" = satir indeksi (0..satir_n-1) -> YATAY eksende (sutun_idx = r)
        # "c" = sutun indeksi (0..sutun_n-1) -> DIKEY eksende (satir_idx = c)
        disp_cols = satir_n   # ekranda yatayda kac hucre (az sayida olur)
        disp_rows = sutun_n   # ekranda dikeyde kac hucre (cok sayida olur)

        cell_size = self.base_cell_size * self.zoom
        display_w, display_h = cell_size * disp_cols, cell_size * disp_rows

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
                color = lux_color(val, vmin, vmax) if val is not None else (0.16, 0.16, 0.18, 1)
                idx = (tex_row * disp_cols + tex_col) * 4
                buf[idx:idx + 4] = bytes(int(max(0.0, min(1.0, ch)) * 255) for ch in color)
        texture.blit_buffer(bytes(buf), colorfmt="rgba", bufferfmt="ubyte")

        heat_container = FloatLayout(size=(display_w, display_h), size_hint=(None, None))
        img = TextureView(texture=texture, size=(display_w, display_h), pos=(0, 0),
                           size_hint=(None, None))
        heat_container.add_widget(img)

        def cell_pos(r, c):
            """Bir (satir, sutun) noktasinin ekran pikseli - yukaridaki ile ayni mantik."""
            x = r * cell_size
            y = (disp_rows - 1 - c) * cell_size
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
        MIN_COLOR = (0.35, 0.65, 1, 1)     # mavi - en dusuk degerler (sadece normal modda)
        MAX_COLOR = (1, 0.35, 0.35, 1)     # kirmizi - en yuksek degerler (sadece normal modda)
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
                                    size_hint=(None, None), size=(cell_size, cell_size))
                cell.pos = pos
                heat_container.add_widget(cell)
            elif (r, c) in lowest_keys:
                cell = ExtremeCell(str(val), MIN_COLOR,
                                    size_hint=(None, None), size=(cell_size, cell_size))
                cell.pos = pos
                heat_container.add_widget(cell)
            elif (r, c) in highest_keys:
                cell = ExtremeCell(str(val), MAX_COLOR,
                                    size_hint=(None, None), size=(cell_size, cell_size))
                cell.pos = pos
                heat_container.add_widget(cell)
            else:
                lbl = Label(text=str(val), font_size=sp(self.label_font_size), bold=True,
                            color=(1, 1, 1, 1),
                            size_hint=(None, None), size=(cell_size, cell_size))
                lbl.pos = pos
                heat_container.add_widget(lbl)

        # --- MAUR gorunumu: hatali komsuluklari BAGLANTI CIZGISIYLE de isaretle ---
        if self.maur_mode and maur_threshold is not None:
            for (r1, c1), (r2, c2), v1, v2, ratio in maur_failures:
                p1 = cell_pos(r1, c1)
                marker = Widget(size_hint=(None, None), size=(1, 1))
                with marker.canvas:
                    Color(0.88, 0.28, 0.25, 1)
                    if c1 == c2:  # r farkli -> ekranda YATAY komsuluk -> dikey bar
                        bar_w = dp(4)
                        Rectangle(pos=(p1[0] + cell_size - bar_w / 2, p1[1]),
                                  size=(bar_w, cell_size))
                    else:  # c farkli -> ekranda DIKEY komsuluk -> yatay bar
                        bar_h = dp(4)
                        Rectangle(pos=(p1[0], p1[1] - bar_h / 2), size=(cell_size, bar_h))
                heat_container.add_widget(marker)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=True, do_scroll_y=True,
                             bar_width=dp(6))
        scroll.add_widget(heat_container)

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
                verdict_card = Card(bg_color=SUCCESS_TINT if maur_ok else (0.22, 0.09, 0.10, 1),
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
                    color=(0.6, 0.9, 0.7, 1) if maur_ok else (1, 0.6, 0.6, 1)))
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
        min_lbl = Label(text=f"{vmin:.0f}", font_size=sp(11), color=TEXT_MUTED,
                        halign="left", valign="middle")
        min_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        max_lbl = Label(text=f"{vmax:.0f}", font_size=sp(11), color=TEXT_MUTED,
                        halign="right", valign="middle")
        max_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        minmax_row.add_widget(min_lbl)
        minmax_row.add_widget(max_lbl)
        legend_card.add_widget(minmax_row)
        self.content_area.add_widget(legend_card)

        # --- Ozet paneli (Relux/DIALux hesap sayfasi mantiginda) ---
        values = list(by_pos.values())
        eavg = sum(values) / len(values)
        emin = min(values)
        emax = max(values)
        uo = emin / eavg if eavg else 0
        ud = emin / emax if emax else 0
        uo_ratio = (eavg / emin) if emin else 0
        ud_ratio = (emax / emin) if emin else 0

        summary_card = Card(bg_color=CARD, radius=14, orientation="vertical",
                             size_hint_y=None, padding=[dp(16), dp(12), dp(16), dp(12)],
                             spacing=dp(6))
        summary_card.add_widget(Label(text="Ozet", font_size=sp(16), bold=True, color=TEXT,
                                       size_hint_y=None, height=dp(24), halign="left",
                                       text_size=(dp(300), None)))

        def summary_row(label, symbol, value_text):
            row = BoxLayout(size_hint_y=None, height=dp(24))
            row.add_widget(Label(text=label, font_size=sp(13), color=TEXT_MUTED,
                                  halign="left", text_size=(dp(170), None), size_hint_x=0.55))
            row.add_widget(Label(text=symbol, font_size=sp(13), color=TEXT_MUTED,
                                  halign="left", text_size=(dp(90), None), size_hint_x=0.25))
            row.add_widget(Label(text=value_text, font_size=sp(13.5), bold=True, color=TEXT,
                                  halign="right", text_size=(dp(90), None), size_hint_x=0.35))
            return row

        summary_card.add_widget(summary_row("Ortalama aydinlatma", "E\u0304m", f"{eavg:.0f} lx"))
        summary_card.add_widget(summary_row("Minimum aydinlatma", "Emin", f"{emin:.0f} lx"))
        summary_card.add_widget(summary_row("Maksimum aydinlatma", "Emax", f"{emax:.0f} lx"))
        summary_card.add_widget(summary_row("Duzgunluk Uo", "Emin/E\u0304m",
                                             f"1:{uo_ratio:.2f} ({uo:.2f})"))
        summary_card.add_widget(summary_row("Cesitlilik Ud", "Emin/Emax",
                                             f"1:{ud_ratio:.2f} ({ud:.2f})"))

        summary_card.bind(minimum_height=summary_card.setter("height"))
        self.content_area.add_widget(summary_card)


class ReportScreen(Screen):
    """Rapor - secili FIFA/UEFA standardina gore olcum sonuclarinin karsilastirmasi."""

    def __init__(self, measure_screen, **kwargs):
        super().__init__(**kwargs)
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

    def on_pre_enter(self, *a):
        self._build_report()

    def _show_message_popup(self, title, message):
        content = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(14))
        content.add_widget(Label(text=message, font_size=sp(13.5), color=TEXT, halign="center"))
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.4),
                       auto_dismiss=True, separator_color=BORDER, title_color=TEXT,
                       background_color=(0.08, 0.08, 0.10, 1))
        close_btn = FlatButton(text="Tamam", bg_color=ACCENT, font_size=sp(14),
                                size_hint_y=None, height=dp(46))
        close_btn.bind(on_release=lambda b: popup.dismiss())
        content.add_widget(close_btn)
        popup.open()

    def _export_dir(self):
        try:
            app = App.get_running_app()
            path = app.user_data_dir
        except Exception:
            path = "."
        return path

    def export_pdf(self):
        data = self._compute_report_data()
        if not data:
            self._show_message_popup("PDF", "Once olcum girin, sonra rapor disa aktarilabilir.")
            return
        try:
            from fpdf import FPDF
        except ImportError:
            self._show_message_popup(
                "PDF Kutuphanesi Eksik",
                "PDF olusturmak icin 'fpdf2' kutuphanesi gerekiyor.\n"
                "Pydroid 3'te pip sekmesinden 'fpdf2' yazip kurun.")
            return

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "SAHA AYDINLATMA UYGUNLUK RAPORU", ln=True, align="C")
            pdf.ln(4)

            pdf.set_font("Helvetica", "", 11)
            proj = data["project_info"]
            for label, key in [("Stadyum/Tesis", "name"), ("Ulke / Sehir", "location"),
                                ("Olcum Tarihi", "date"), ("Raporu Hazirlayan", "prepared_by")]:
                pdf.cell(0, 7, f"{label}: {proj.get(key, '') or '-'}", ln=True)
            pdf.cell(0, 7, f"Karsilastirilan Standart: {data['org']} {data['level']}", ln=True)
            pdf.cell(0, 7, f"Izgara: {data['rows']} x {data['cols']}   "
                           f"Olculen: {data['measured_count']}/{data['total_points']} nokta", ln=True)
            pdf.ln(4)

            pdf.set_font("Helvetica", "B", 13)
            verdict = "KRITERLERI KARSILIYOR" if data["all_pass"] else "KRITERLERI KARSILAMIYOR"
            pdf.set_text_color(20, 130, 60) if data["all_pass"] else pdf.set_text_color(180, 30, 30)
            pdf.cell(0, 9, verdict, ln=True, align="C")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

            col_w = [55, 35, 35, 45]
            for plane_title, criteria in data["plane_groups"]:
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_fill_color(230, 230, 230)
                pdf.cell(sum(col_w), 7, plane_title, ln=True, fill=True)
                pdf.set_font("Helvetica", "", 10)
                headers = ["Kriter", "Referans", "Olculen", "Sonuc"]
                pdf.set_font("Helvetica", "B", 9)
                for w, h in zip(col_w, headers):
                    pdf.cell(w, 6, h, border=1)
                pdf.ln()
                pdf.set_font("Helvetica", "", 9)
                for kriter, referans, olculen, ok in criteria:
                    pdf.cell(col_w[0], 6, kriter, border=1)
                    pdf.cell(col_w[1], 6, referans, border=1)
                    pdf.cell(col_w[2], 6, olculen, border=1)
                    pdf.set_text_color(20, 130, 60) if ok else pdf.set_text_color(180, 30, 30)
                    pdf.cell(col_w[3], 6, "UYGUN" if ok else "UYGUN DEGIL", border=1)
                    pdf.set_text_color(0, 0, 0)
                    pdf.ln()
                pdf.ln(2)

            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "MAUR - Komsu Nokta Tekduzeligi", ln=True)
            pdf.set_font("Helvetica", "", 10)
            if data["maur_ratio"] is None:
                pdf.cell(0, 7, "Bu standart seviyesi icin MAUR belirtilmemis.", ln=True)
            else:
                pdf.cell(0, 7, f"Toplam hata (5 duzlem): {data['maur_total_fail']} / "
                               f"izin verilen {data['maur_max_fail']}", ln=True)
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(20, 130, 60) if data["maur_ok"] else pdf.set_text_color(180, 30, 30)
                pdf.cell(0, 7, "UYGUN" if data["maur_ok"] else "UYGUN DEGIL", ln=True)
                pdf.set_text_color(0, 0, 0)

            fname = f"aydinlatma_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            fpath = os.path.join(self._export_dir(), fname)
            pdf.output(fpath)
            self._show_message_popup("PDF Kaydedildi", f"Dosya kaydedildi:\n{fpath}")
        except Exception as e:
            self._show_message_popup("PDF Hatasi", f"PDF olusturulurken bir sorun olustu:\n{e}")

    def export_excel(self):
        data = self._compute_report_data()
        if not data:
            self._show_message_popup("Excel", "Once olcum girin, sonra rapor disa aktarilabilir.")
            return
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill
        except ImportError:
            self._show_message_popup(
                "Excel Kutuphanesi Eksik",
                "Excel olusturmak icin 'openpyxl' kutuphanesi gerekiyor.\n"
                "Pydroid 3'te pip sekmesinden 'openpyxl' yazip kurun.")
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

            fname = f"aydinlatma_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            fpath = os.path.join(self._export_dir(), fname)
            wb.save(fpath)
            self._show_message_popup("Excel Kaydedildi", f"Dosya kaydedildi:\n{fpath}")
        except Exception as e:
            self._show_message_popup("Excel Hatasi", f"Excel olusturulurken bir sorun olustu:\n{e}")

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
        for title, kind in PROBES:
            vals = [d["values"][title] for d in measured.values()]
            avg = sum(vals) / len(vals)
            vmin = min(vals)
            vmax = max(vals)
            u1 = (vmin / vmax) if vmax else 0
            u2 = (vmin / avg) if avg else 0

            req_avg = thresholds[f"{kind}_avg"]
            req_min = thresholds.get(f"{kind}_min")
            req_u1 = thresholds["u1h"] if kind == "Eh" else thresholds.get("u1v")
            req_u2 = thresholds["u2h"] if kind == "Eh" else thresholds.get("u2v")

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

        maur_ratio = thresholds.get("maur_ratio")
        maur_max_fail = thresholds.get("maur_max_fail")
        maur_total_fail = 0
        maur_ok = True
        if maur_ratio is not None:
            for title, kind in PROBES:
                plane_pos = {(d["r"], d["c"]): d["values"][title] for d in measured.values()}
                maur_total_fail += len(compute_maur_failures(plane_pos, maur_ratio))
            maur_ok = maur_total_fail <= maur_max_fail
            if not maur_ok:
                all_pass = False

        return {
            "measured_count": len(measured), "total_points": len(ms.sequence),
            "org": ms.org, "level": ms.level,
            "rows": ms.rows_count_val, "cols": ms.cols_count_val,
            "plane_groups": plane_groups, "all_pass": all_pass,
            "maur_ratio": maur_ratio, "maur_max_fail": maur_max_fail,
            "maur_total_fail": maur_total_fail, "maur_ok": maur_ok,
            "project_info": dict(ms.project_info),
        }

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
                        size_hint_x=0.36, halign="left", text_size=(dp(105), None))
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

        measured = {idx: d for idx, d in ms.measurements.items() if d["values"] is not None}
        total_points = len(ms.sequence)

        if not measured:
            msg = Label(text="Henuz olcum yok.\nOlcum girildikce karsilastirma\nburada olusacak.",
                        font_size=sp(14), color=TEXT_MUTED, halign="center",
                        size_hint_y=None, height=dp(70))
            msg.bind(size=lambda i, v: setattr(i, "text_size", v))
            self.content_area.add_widget(msg)
            return

        thresholds = STANDARDS[ms.org][ms.level]

        # --- Bilgi karti (standart + izgara) ---
        info_card = Card(bg_color=CARD, radius=14, orientation="vertical",
                          padding=[dp(16), dp(12), dp(16), dp(12)], spacing=dp(4),
                          size_hint_y=None)
        info_card.add_widget(Label(text=f"Standart: {ms.org} - {ms.level}", font_size=sp(14),
                                    bold=True, color=TEXT, size_hint_y=None, height=dp(22),
                                    halign="left", text_size=(dp(300), None)))
        info_card.add_widget(Label(text=f"Izgara: {ms.rows_count_val} x {ms.cols_count_val}   |   "
                                         f"Olculen: {len(measured)}/{total_points} nokta",
                                    font_size=sp(12.5), color=TEXT_MUTED, size_hint_y=None,
                                    height=dp(20), halign="left", text_size=(dp(300), None)))
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
        verdict_card = Card(bg_color=SUCCESS_TINT if all_pass else (0.22, 0.09, 0.10, 1),
                             radius=14, border_color=SUCCESS if all_pass else DANGER,
                             size_hint_y=None, height=dp(56), padding=[dp(16), 0, dp(16), 0])
        verdict_text = ("KRITERLERI KARSILIYOR" if all_pass else "KRITERLERI KARSILAMIYOR")
        verdict_card.add_widget(Label(text=verdict_text, font_size=sp(16), bold=True,
                                       color=(0.6, 0.9, 0.7, 1) if all_pass else (1, 0.6, 0.6, 1)))
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
        self.add_widget(self.sm)

        nav_card = Card(bg_color=(0.09, 0.09, 0.10, 1), radius=0, size_hint_y=None,
                         height=dp(66), padding=[dp(4), dp(6), dp(4), dp(6)])
        nav_row = BoxLayout(spacing=dp(2))
        nav_card.add_widget(nav_row)

        self.tabs = {}
        tab_defs = [
            ("measure", "measure", "Olcum"),
            ("control", "control", "Kontrol"),
            ("standards", "standards", "Standart"),
            ("report", "report", "Rapor"),
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
        return RootLayout()


if __name__ == "__main__":
    AydinlatmaApp().run()
