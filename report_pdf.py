# -*- coding: utf-8 -*-
"""Yeni kurumsal PDF rapor uretici (SAH kimligi) - FIFA / UEFA / FIBA.

ONEMLI: Bu modul HICBIR olcum hesabi YAPMAZ. Tum sayilar uygulamanin kendi
hesaplayicilarindan (ReportScreen._compute_report_data / _compute_fiba_report_data)
gelen `data` sozlugunden okunur - boylece ekrandaki Sonuc sekmesi ile PDF
HER ZAMAN ayni degerleri gosterir. (Sadece gosterim amacli iki ufak turetilmis
deger vardir: en dusuk komsu orani ve FIBA haritalarinin altindaki ozet kartlari;
bunlar testlerle uygulama hesabiyla karsilastirilir.)
Dil: "tr" veya "en".
"""
import os
from datetime import datetime
from fpdf import FPDF

YEL = (248, 224, 0); INK = (31, 35, 40); GRAY = (107, 114, 128); LINE = (229, 231, 235); CARD = (247, 247, 245)
BRAND = (64, 64, 65); OK_BG = (217, 242, 208); OK_TX = (27, 107, 46); BAD_BG = (252, 216, 216); BAD_TX = (170, 30, 30)
WARN_BG = (255, 244, 205); WARN_TX = (133, 100, 4)
LX, RX = 16, 194; CW = RX - LX
PROBES = [("Eh", "Eh"), ("Ev0", "Ev"), ("Ev90", "Ev"), ("Ev180", "Ev"), ("Ev270", "Ev")]

# ----------------------------------------------------------------- metinler
I = {
    "rep_title": ("AYDINLATMA ÖLÇÜM RAPORU", "ILLUMINANCE MEASUREMENT REPORT"),
    "rep_title_bb": ("BASKETBOL AYDINLATMA ÖLÇÜM RAPORU", "BASKETBALL ILLUMINANCE MEASUREMENT REPORT"),
    "date": ("TARİH", "DATE"), "location": ("KONUM", "LOCATION"), "measured_by": ("ÖLÇÜMÜ YAPAN", "MEASURED BY"),
    "page": ("Sayfa", "Page"),
    "cs_title": ("Test Raporu Kapak Sayfası", "Test Report Cover Sheet"),
    "cs_sub": ("Genel bilgiler, ekipman ve denetim bilgileri", "General information, equipment and inspection details"),
    "general": ("Genel", "General"), "inspection": ("Denetim", "Inspection"), "equipment": ("Ekipman", "Equipment"),
    "luminaires": ("Armatür", "Luminaire"),
    "stadium": ("Stadyum adı", "Name of stadium"), "venue": ("Salon adı", "Name of venue"), "club": ("Kulüp adı", "Name of club"),
    "city": ("Şehir / konum", "City / location"), "insp_date": ("Denetim tarihi", "Date of inspection"),
    "insp_time": ("Denetim saati", "Time of inspection"), "pitch": ("Saha (uzunluk x genişlik)", "Pitch (length x width)"),
    "areas": ("Oyun alanları", "Playing areas"),
    "weather": ("Hava durumu", "Weather conditions"), "std": ("Uygulanan standart", "Applied standard"),
    "method": ("Ölçüm yöntemi", "Measurement method"), "method_v": ("Manuel, referans ızgarası", "Manual, reference grid"),
    "grid": ("Izgara", "Grid"), "points": ("nokta", "points"),
    "org": ("Denetleyen kuruluş", "Organisation inspecting"), "addr": ("Adres", "Address"),
    "phone": ("Telefon / e-posta", "Phone / e-mail"), "insp_by": ("Denetleyen (ad)", "Inspection by (name)"),
    "signature": ("İmza", "Signature"),
    "item": ("Kalem", "Item"), "model": ("Model", "Model"), "serial": ("Seri no", "Serial no"), "cal": ("Kalibrasyon tarihi", "Calibration date"),
    "meter": ("Aydınlık şiddeti ölçer", "Illuminance meter"), "head": ("Alıcı kafa No.{n}", "Receptor head No.{n}"),
    "colour_meter": ("Renk ölçer", "Colour meter"),
    "cal_note": ("Kalibrasyon, test tarihinden en fazla 12 ay önce yapılmış olmalıdır (FIFA / UEFA aydınlatma kılavuzları).",
                 "Calibration must be within 12 months of the test date (FIFA / UEFA lighting guides)."),
    "manufacturer": ("Üretici", "Manufacturer"), "lum_model": ("Model / ürün tipi", "Model / product type"),
    "std_title": ("Aydınlatma Standardı Gereksinimleri", "Lighting Standard Requirements"),
    "std_sub": ("manuel aydınlık şiddeti ölçümü kapsamı", "manual illuminance measurement scope"),
    "average": ("Ortalama", "Average"), "minimum": ("Minimum", "Minimum"), "maximum": ("Maksimum", "Maximum"),
    "max_ref": ("Maksimum (bilgi)", "Maximum (reference)"),
    "u1": ("Düzgünlük U1", "Uniformity U1"), "u2": ("Düzgünlük U2", "Uniformity U2"),
    "u1m": ("Düzgünlük U1 (min/maks)", "Uniformity U1 (min/max)"), "u2m": ("Düzgünlük U2 (min/ort)", "Uniformity U2 (min/avg)"),
    "no_req": ("Bu yön için gereksinim yok", "No requirement for this direction"),
    "maur_card": ("MAUR (komşu noktalar)", "MAUR (adjacent points)"),
    "min_ratio": ("Min. oran", "Min. ratio"), "max_fail": ("En çok hata", "Max. failures"),
    "other_req": ("Diğer gereksinimler", "Other requirements"),
    "other_note": ("Renk sıcaklığı, renk geriverimi, titreşim (flicker), kamaşma ve maç sürekliliği T-10MA ile ölçülemez; "
                   "uygulamada girilen değerler 'Ek Veriler' sayfasında gösterilir.",
                   "Colour temperature, colour rendering, flicker, glare and match continuity cannot be measured with the T-10MA; "
                   "values entered in the app are shown on the 'Additional Data' page."),
    "mcm": ("Maç sürekliliği (MCM)", "Match continuity (MCM)"), "ff": ("Titreşim (flicker)", "Flicker factor"),
    "cct": ("Renk sıcaklığı (Tc)", "Colour temperature (Tc)"), "ra": ("Renk geriverimi (Ra)", "Colour rendering (Ra)"),
    "rg": ("Kamaşma (RG)", "Glare rating (RG)"), "mf": ("Bakım faktörü (MF)", "Maintenance factor (MF)"),
    "sum_title": ("Sonuç Özeti", "Summary of Results"),
    "sum_sub": ("{date}  ·  {n}/{t} nokta  ·  değerler ölçüldüğü gibidir",
                "{date}  ·  {n}/{t} points  ·  values as measured"),
    "complies": ("KRİTERLERİ KARŞILIYOR", "COMPLIES"), "not_complies": ("KRİTERLERİ KARŞILAMIYOR", "DOES NOT COMPLY"),
    "maur_line": ("MAUR hataları (tüm düzlemler): {f}  ·  izin verilen: {m}", "MAUR failures (all planes): {f}  ·  allowed: {m}"),
    "maur_na": ("MAUR bu standartta belirtilmemiştir", "MAUR is not specified for this standard"),
    "incomplete": ("EKSİK ÖLÇÜM: {n}/{t} nokta ölçüldü - sonuç yalnızca ölçülen noktaları kapsar",
                   "INCOMPLETE: {n}/{t} points measured - result covers measured points only"),
    "metric": ("Ölçüt", "Metric"), "req": ("Gereksinim", "Requirement"), "meas": ("Ölçülen", "Measured"), "status": ("Durum", "Status"),
    "pass": ("UYGUN", "PASS"), "fail": ("UYGUN DEĞİL", "FAIL"),
    "maur_fails": ("MAUR hataları", "MAUR failures"),
    "grid_title": ("Ölçüm Izgarası ve Sırası", "Measurement Grid & Order"),
    "grid_sub": ("Grid No 1 = sol üst köşe  ·  satırlar soldan sağa, sonra sağdan sola ilerler (yılan düzeni)",
                 "Grid No 1 = top-left corner  ·  rows run left to right, then right to left (snake)"),
    "start": ("BAŞLANGIÇ", "START"), "order": ("SIRA", "ORDER"), "end": ("BİTİŞ", "END"),
    "start_v": ("Grid No 1, sol üst köşe (sarı)", "Grid No 1, top-left corner (yellow)"),
    "order_v": ("Önce uzunluk boyunca, sonra bir satır aşağı", "Along the length, then one row down"),
    "end_v": ("Grid No {n}, {pos} (koyu)", "Grid No {n}, {pos} (dark)"),
    "pos_bl": ("sol alt", "bottom-left"), "pos_br": ("sağ alt", "bottom-right"),
    "spacing": ("{L} m ({a} aralık x {sa} m)   ·   {W} m ({b} aralık x {sb} m)", "{L} m ({a} spaces x {sa} m)   ·   {W} m ({b} spaces x {sb} m)"),
    "raw_title": ("Ham Ölçüm Verileri", "Raw Measurement Data"), "raw_sub": ("Ölçüm sırasına göre Grid No", "Grid No in measurement order"),
    "map_title": ("Aydınlatma Haritası", "Lighting Map"),
    "map_sub": ("Hücre değeri = lux  ·  küçük sayı = Grid No  ·  mavi / kırmızı köşe = en düşük / en yüksek 3 değer",
                "Cell value = lux  ·  small number = Grid No  ·  blue / red corner = 3 lowest / 3 highest"),
    "map_sub_fiba": ("Kesikli çerçeve = PPA  ·  mavi / kırmızı köşe = en düşük / en yüksek 3 değer",
                     "Dashed frame = PPA  ·  blue / red corner = 3 lowest / 3 highest"),
    "p_Eh": ("Yatay (Eh)", "Horizontal (Eh)"), "p_Ev0": ("Dikey 0°", "Vertical 0°"), "p_Ev90": ("Dikey 90°", "Vertical 90°"),
    "p_Ev180": ("Dikey 180°", "Vertical 180°"), "p_Ev270": ("Dikey 270°", "Vertical 270°"), "p_EC": ("Ana kamera (EC)", "Main camera (EC)"),
    "AVERAGE": ("ORTALAMA", "AVERAGE"), "MINIMUM": ("MİNİMUM", "MINIMUM"), "MAXIMUM": ("MAKSİMUM", "MAXIMUM"),
    "U1": ("U1 (min/maks)", "U1 (min/max)"), "U2": ("U2 (min/ort)", "U2 (min/avg)"), "reqk": ("gerek >", "req >"),
    "maur_title": ("MAUR - Komşu Nokta Düzgünlüğü", "MAUR - Adjacent Point Uniformity"),
    "maur_sub": ("Her nokta komşusuna kıyaslanır; komşu değer, noktanın değeri x oran değerinden küçükse hata sayılır",
                 "Each point is compared with its neighbours; a neighbour below point value x ratio counts as a failure"),
    "plane": ("Düzlem", "Plane"), "lowest": ("En düşük oran", "Lowest ratio"), "failures": ("Hata", "Failures"), "limit": ("Eşik oran", "Threshold ratio"),
    "total_f": ("Toplam hata: {f}   ·   izin verilen: {m}", "Total failures: {f}   ·   allowed: {m}"),
    "no_pairs": ("Eşiği aşan komşu nokta çifti yok.", "No adjacent point pairs exceed the threshold."),
    "pairs": ("hatalı çift", "faulty pairs"), "pair": ("Nokta çifti", "Point pair"), "v1": ("Değer 1 (lx)", "Value 1 (lx)"),
    "v2": ("Değer 2 (lx)", "Value 2 (lx)"), "ratio": ("Oran", "Ratio"),
    "add_title": ("Ek Veriler", "Additional Data"),
    "add_sub": ("Resmi rapor özetinin parçası; T-10MA ile ölçülemez, uygulamada elle girilir",
                "Part of the official report summary; not measurable with the T-10MA, entered manually in the app"),
    "param": ("Parametre", "Parameter"), "avg_flicker": ("Ortalama flicker faktörü", "Average flicker factor"),
    "max_flicker": ("Maksimum flicker faktörü", "Maximum flicker factor"),
    "not_entered": ("girilmedi", "not entered"),
    "notes_title": ("Notlar ve Onay", "Notes & Approval"), "notes": ("Notlar", "Notes"),
    "approved_by": ("ONAYLAYAN", "APPROVED BY"), "name_sig": ("Ad / imza / tarih", "Name / signature / date"),
    "fiba_std": ("FIBA Resmi Basketbol Kuralları 2024, Bölüm 12", "FIBA Official Basketball Rules 2024, Chapter 12"),
    "fiba_std_sub": ("Tablo 5 - aydınlık şiddeti gereksinimleri", "Table 5 - illuminance requirements"),
    "fiba_note": ("Titreşim, renk geriverimi, renk sıcaklığı, kamaşma ve görsel muayene (Kural 12.2.2 - 12.2.6) manuel aydınlık şiddeti ölçümünün dışındadır. "
                  "FIBA test yöntemi 'Handbook of Test Methods and Requirements' belgesinde tanımlıdır.",
                  "Flicker, colour rendering, colour temperature, glare and the visual inspection (Rules 12.2.2 - 12.2.6) are outside a manual illuminance measurement. "
                  "The FIBA test method is defined in the Handbook of Test Methods and Requirements."),
    "ec_avg": ("EC ortalama (ana kamera)", "EC average (main camera)"), "ec_u": ("EC U1 / U2", "EC U1 / U2"),
    "ev_avg": ("EV ortalama (her yön)", "EV average (each direction)"), "ev_u": ("EV U1 / U2", "EV U1 / U2"),
    "ev_ratio": ("EV yön oranı (min/maks)", "EV direction ratio (min/max)"), "eh_avg": ("EH ortalama (aralık)", "EH average (range)"),
    "eh_u": ("EH U1 / U2", "EH U1 / U2"),
    "fiba_sum_sub": ("{date}  ·  {n}/{t} nokta  ·  iki tur  ·  değerler ölçüldüğü gibidir", "{date}  ·  {n}/{t} points  ·  two rounds  ·  values as measured"),
    "ppa_t": ("PPA - Ana oyun alanı (19 x 32 m)", "PPA - Principal playing area (19 x 32 m)"),
    "tpa_t": ("TPA - Toplam oyun alanı (22 x 35 m)", "TPA - Total playing area (22 x 35 m)"),
    "ec_row": ("EC ortalama", "EC average"), "ecu1": ("EC düzgünlük U1", "EC uniformity U1"), "ecu2": ("EC düzgünlük U2", "EC uniformity U2"),
    "evd_avg": ("EV {d}° ortalama", "EV {d}° average"), "evd_u1": ("EV {d}° U1", "EV {d}° U1"), "evd_u2": ("EV {d}° U2", "EV {d}° U2"),
    "evr": ("EV yön oranı", "EV direction ratio"), "ehr": ("EH ortalama (aralık)", "EH average (range)"),
    "ehu1": ("EH düzgünlük U1", "EH uniformity U1"), "ehu2": ("EH düzgünlük U2", "EH uniformity U2"),
    "not_meas": ("Ölçülmedi ({m}/{t})", "Not measured ({m}/{t})"),
    "ppa_n": ("{z}  ·  {n} nokta", "{z}  ·  {n} points"),
    "fiba_grid_sub": ("Grid No 1 = sol üst köşe  ·  satırlar soldan sağa, sonra sağdan sola (yılan düzeni)  ·  kesikli çerçeve = PPA",
                      "Grid No 1 = top-left corner  ·  rows left to right, then right to left (snake)  ·  dashed frame = PPA"),
    "fiba_grid_cap": ("TPA 35 x 22 m  ·  kesikli = PPA 32 x 19 m  ·  saha 28 x 15 m", "TPA 35 x 22 m  ·  dashed = PPA 32 x 19 m  ·  court 28 x 15 m"),
    "site": ("Tesis / proje adı", "Site / project name"),
    "chip_free": ("SERBEST ÖLÇÜM", "FREE MEASUREMENT"),
    "no_std": ("Standart yok (serbest ölçüm)", "None (free measurement)"),
    "area": ("Alan (uzunluk x genişlik)", "Area (length x width)"),
    "free_note": ("Bu rapor bir standarda göre değerlendirme içermez; ölçülen değerleri gösterir.",
                  "This report contains no evaluation against a standard; it presents the measured values."),
    "free_title": ("Ölçüm Sonuçları", "Measurement Results"),
    "free_sub": ("{date}  ·  {n}/{t} nokta  ·  değerler ölçüldüğü gibidir", "{date}  ·  {n}/{t} points  ·  values as measured"),
    "target": ("Hedef", "Target"),
    "free_target_note": ("Hedef değerler kullanıcı tarafından girilmiştir; bir standart gereksinimi değildir.",
                         "Target values were entered by the user; they are not a standard requirement."),
    "targets_ok": ("GİRİLEN HEDEFLERİ KARŞILIYOR", "MEETS THE ENTERED TARGETS"),
    "targets_fail": ("GİRİLEN HEDEFLERİ KARŞILAMIYOR", "DOES NOT MEET THE ENTERED TARGETS"),
    "no_values": ("Bu düzlemde ölçüm yok", "No measurements in this plane"),
    "round1": ("1. tur: 4 dikey + EC", "Round 1: 4 vertical + EC"), "round2": ("2. tur: yatay (Eh)", "Round 2: horizontal (Eh)"),
}
# Standartlardaki sabit Turkce metinlerin Ingilizcesi (dil = en iken)
EN_VALUES = {
    "Eh ort > 1000 lx (3 dk) / > 1250 lx (15 dk)": "Eh avg > 1000 lx (3 min) / > 1250 lx (15 min)",
    "Eh ort > 2000 lx, 15 dakika icinde": "Eh avg > 2000 lx, within 15 minutes",
    "FIFA tarafindan duruma gore belirlenir": "Determined by FIFA case by case",
    "Gecerli degil (antrenman sahasi)": "Not applicable (training pitch)",
    "Guc kesintisinden sonra 15 dakika icinde": "Within 15 minutes after a power interruption",
    "Isik surekliligine kesinti verilemez": "No interruption of light continuity permitted",
    "LED: kesinti yok. HID: FPSL A'ya bakiniz": "LED: no interruption. HID: see FPSL A",
    "belirtilmemis": "not specified", "belirtilmemis (MAUR bu standartta yok)": "not specified (no MAUR in this standard)",
    "ort < 1%   maks < 1%": "avg < 1%   max < 1%", "ort < 12%   maks < 15%": "avg < 12%   max < 15%",
    "ort < 20%   maks < 30%": "avg < 20%   max < 30%", "ort < 3%   maks < 3%": "avg < 3%   max < 3%", "< %1": "< 1%",
    "> 0.50   (en fazla 30 hata)": "> 0.50   (max 30 failures)", "> 0.60   (en fazla 10 hata)": "> 0.60   (max 10 failures)",
    "> 0.60   (en fazla 20 hata)": "> 0.60   (max 20 failures)", "> 0.60   (en fazla 30 hata)": "> 0.60   (max 30 failures)",
}
TR_VALUES = {
    "Eh ort > 1000 lx (3 dk) / > 1250 lx (15 dk)": "Eh ort. > 1000 lx (3 dk) / > 1250 lx (15 dk)",
    "Eh ort > 2000 lx, 15 dakika icinde": "Eh ort. > 2000 lx, 15 dakika içinde",
    "FIFA tarafindan duruma gore belirlenir": "FIFA tarafından duruma göre belirlenir",
    "Gecerli degil (antrenman sahasi)": "Geçerli değil (antrenman sahası)",
    "Guc kesintisinden sonra 15 dakika icinde": "Güç kesintisinden sonra 15 dakika içinde",
    "Isik surekliligine kesinti verilemez": "Işık sürekliliğine kesinti verilemez",
    "LED: kesinti yok. HID: FPSL A'ya bakiniz": "LED: kesinti yok. HID: FPSL A'ya bakınız",
    "belirtilmemis": "belirtilmemiş", "belirtilmemis (MAUR bu standartta yok)": "belirtilmemiş (bu standartta MAUR yok)",
    "ort < 1%   maks < 1%": "ort. < %1   maks. < %1", "ort < 12%   maks < 15%": "ort. < %12   maks. < %15",
    "ort < 20%   maks < 30%": "ort. < %20   maks. < %30", "ort < 3%   maks < 3%": "ort. < %3   maks. < %3", "< %1": "< %1",
    "> 0.50   (en fazla 30 hata)": "> 0,50   (en fazla 30 hata)", "> 0.60   (en fazla 10 hata)": "> 0,60   (en fazla 10 hata)",
    "> 0.60   (en fazla 20 hata)": "> 0,60   (en fazla 20 hata)", "> 0.60   (en fazla 30 hata)": "> 0,60   (en fazla 30 hata)",
}
EN_PLANE_LABEL = {"Yatay (Eh)": "Horizontal (Eh)", "Dikey 0°": "Vertical 0°", "Dikey 90°": "Vertical 90°",
                  "Dikey 180°": "Vertical 180°", "Dikey 270°": "Vertical 270°"}
EN_CRIT = {"Ortalama >": "Average >", "Minimum >": "Minimum >", "Uniformity U1": "Uniformity U1", "Uniformity U2": "Uniformity U2"}
PLANE_KEYS = ["Eh", "Ev0", "Ev90", "Ev180", "Ev270"]


def make_translator(lang):
    idx = 0 if lang == "tr" else 1
    def t(key, **kw):
        s = I[key][idx]
        return s.format(**kw) if kw else s
    def num(x, dec=2):
        s = f"{x:.{dec}f}"
        return s.replace(".", ",") if lang == "tr" else s
    def val(s):  # standartlardaki sabit metin
        s = str(s)
        return EN_VALUES.get(s, s) if lang == "en" else TR_VALUES.get(s, s)
    return t, num, val


class Rep(FPDF):
    def __init__(self, venue, assets_dir, t):
        super().__init__("P", "mm", "A4")
        self.venue = venue; self.t = t; self.assets = assets_dir; self.cover = False
        self.set_auto_page_break(False); self.alias_nb_pages()
        fd = os.path.join(assets_dir, "fonts")
        try:
            self.add_font("P", "", os.path.join(fd, "Poppins-Regular.ttf")); self.add_font("P", "B", os.path.join(fd, "Poppins-Bold.ttf"))
            self.add_font("PM", "", os.path.join(fd, "Poppins-Medium.ttf"))
            self.fam = {"": ("P", ""), "L": ("P", ""), "M": ("PM", ""), "B": ("P", "B")}
        except Exception:
            self.add_font("D", "", os.path.join(fd, "DejaVuSans.ttf")); self.add_font("D", "B", os.path.join(fd, "DejaVuSans-Bold.ttf"))
            self.fam = {"": ("D", ""), "L": ("D", ""), "M": ("D", "B"), "B": ("D", "B")}
        self.logo = os.path.join(assets_dir, "report_logo.svg")            # tam logo (kapak)
        self.logo_head = os.path.join(assets_dir, "report_logo_head.svg")  # alt yazisiz (sayfa ustleri)

    def f(self, style="", size=9, color=INK):
        fam, st = self.fam[style]; self.set_font(fam, st, size); self.set_text_color(*color)

    def rr(self, x, y, w, h, r=2, fill=None, line=None, lw=.25):
        if fill: self.set_fill_color(*fill)
        if line: self.set_draw_color(*line); self.set_line_width(lw)
        st = "DF" if fill and line else ("F" if fill else "D")
        try:
            self.rect(x, y, w, h, style=st, round_corners=True, corner_radius=r)
        except TypeError:
            self.rect(x, y, w, h, style=st)

    def txt(self, x, y, w, h, s, style="", size=9, color=INK, align="L"):
        s = "" if s is None else str(s)
        self.f(style, size, color); sz = size
        while sz > size * .6 and self.get_string_width(s) > w - .6:
            sz -= .3; self.f(style, sz, color)
        self.set_xy(x, y); self.cell(w, h, s, align=align)

    def hline(self, y, x1=LX, x2=RX, col=LINE, lw=.2):
        self.set_draw_color(*col); self.set_line_width(lw); self.line(x1, y, x2, y)

    def pill(self, x, y, w, h, s, ok=True, size=5.5):
        self.rr(x, y, w, h, h / 2, OK_BG if ok else BAD_BG); self.txt(x, y, w, h, s, "B", size, OK_TX if ok else BAD_TX, "C")

    def logo_img(self, x, y, w, head=False):
        """Vektor (SVG) logo: telefonda Pillow olmadigi icin PNG basilamiyordu."""
        try:
            path = self.logo_head if head else self.logo
            if os.path.exists(path): self.image(path, x, y, w)
        except Exception:
            pass

    def newpage(self, title, sub="", cover=False):
        self.add_page(); self.cover = cover
        if cover: return
        self.logo_img(LX, 7.5, 19, head=True)
        self.txt(60, 9, RX - 60, 6, (self.t("rep_title") + "  ·  " + self.venue), "", 6.5, GRAY, "R")
        self.hline(24); self.rr(LX, 30, 1.8, 9.5, .9, YEL)
        self.txt(LX + 4.5, 29.3, 170, 7, title, "B", 15)
        if sub: self.txt(LX + 4.5, 36, 170, 4, sub, "", 7.5, GRAY)
        self.hline(284); self.txt(LX, 286, 60, 4, "sahgroup.net", "", 7, GRAY)
        self.txt(RX - 40, 286, 40, 4, f"{self.t('page')} {self.page_no()} / {{nb}}", "", 7, GRAY, "R")


def heat_col(t):
    a, b = (253, 241, 166), (46, 125, 91)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _pos_name(seq):
    r, c = seq[-1]; return r, c


def kv_card(p, x, y, w, title, rows, rh=7.4):
    """Uzun degerler (adres vb.) 2 satira sarilir; kartin disina TASMAZ."""
    vw = w * .6 - 10; prepared = []
    for a, b in rows:
        b = b if b else "-"; p.f("M", 7.5)
        if p.get_string_width(str(b)) <= vw - .6: prepared.append((a, [str(b)], 7.5, rh))
        else:
            p.f("M", 6.2)
            try: lines = p.multi_cell(vw, 3.0, str(b), dry_run=True, output="LINES")
            except Exception: lines = [str(b)]
            lines = lines[:3]; prepared.append((a, lines, 6.2, max(rh, 3.0 * len(lines) + 3.6)))
    h = 10 + sum(r[3] for r in prepared) + 2
    p.rr(x, y, w, h, 3, (255, 255, 255), LINE); p.txt(x + 5, y + 3, w - 10, 5, title, "B", 9)
    yy = y + 10
    for i, (a, lines, fs, rr_) in enumerate(prepared):
        if i: p.hline(yy, x + 5, x + w - 5)
        p.txt(x + 5, yy + 1, w * .4 - 3, rh - 2, a, "", 7, GRAY)
        if len(lines) == 1: p.txt(x + 5 + w * .4, yy + 1, vw, rh - 2, lines[0], "M", fs)
        else:
            for k, ln in enumerate(lines): p.txt(x + 5 + w * .4, yy + 1.2 + 3.0 * k, vw, 3.0, ln, "M", fs)
        yy += rr_
    return y + h


def table(p, x, y, widths, head, rows, rh=6.2, aligns=None, hs=7):
    p.rr(x, y, sum(widths), 7.2, 1.6, BRAND); xx = x
    for i, (s, w) in enumerate(zip(head, widths)):
        p.txt(xx + 2, y + .8, w - 4, 5.6, s, "B", hs, (255, 255, 255), (aligns[i] if aligns else "L")); xx += w
    y += 8
    for ri, r in enumerate(rows):
        if ri % 2: p.set_fill_color(*CARD); p.rect(x, y, sum(widths), rh, "F")
        xx = x
        for i, (s, w) in enumerate(zip(r, widths)):
            p.txt(xx + 2, y + .4, w - 4, rh - .8, s, "", 7, INK, (aligns[i] if aligns else "L")); xx += w
        y += rh
    p.hline(y, x, x + sum(widths)); return y


def dir_labels(p, x0, y0, W, H, pad=0):
    for s, x, y in (("270°", x0 + W / 2 - 8, y0 - 7 - pad), ("90°", x0 + W / 2 - 8, y0 + H + 1.5 + pad)):
        p.rr(x, y, 16, 5.5, 2.7, YEL); p.txt(x, y, 16, 5.5, s, "B", 7, INK, "C")
    for s, x in (("180°", x0 - 13.5 - pad), ("0°", x0 + W + 1.5 + pad)):
        p.rr(x, y0 + H / 2 - 2.75, 12, 5.5, 2.7, YEL); p.txt(x, y0 + H / 2 - 2.75, 12, 5.5, s, "B", 7, INK, "C")


def kpi(p, x, y, w, h, label, val, req=None, ok=None):
    p.rr(x, y, w, h, 3, (255, 255, 255), ((OK_TX if ok else BAD_TX) if ok is not None else LINE), .5 if ok is not None else .25)
    p.txt(x, y + 2, w, 4, label, "", 6.3, GRAY, "C"); p.txt(x, y + 7, w, 8, val, "B", 13, INK, "C")
    if req: p.txt(x, y + h - 6, w, 4, req, "", 6, ((OK_TX if ok else BAD_TX) if ok is not None else GRAY), "C")


def heatmap(p, g, R, C, x0, y0, cw, ch, gridno, ppa=None, fs=7.5):
    """g: {(r,c): deger|None}. Uygulamadaki gibi: yatay=r (sol=0), dikey=c (ust=0).
    En dusuk 3 / en yuksek 3 HUCRE (uygulamadaki gibi siralama ile) mavi/kirmizi kose isareti alir."""
    idx = sorted([(v, c, r) for (r, c), v in g.items() if v is not None])
    n_ext = min(3, len(idx)); low = {(r, c) for v, c, r in idx[:n_ext]}; high = {(r, c) for v, c, r in idx[-n_ext:]}
    vals = [v for v, _, _ in idx]; lo, hi = (vals[0], vals[-1]) if vals else (0, 1)
    for r in range(R):
        for c in range(C):
            x = x0 + r * cw; y = y0 + c * ch; v = g.get((r, c))
            if v is None:
                p.rr(x + .3, y + .3, cw - .6, ch - .6, 1.2, (238, 238, 238))
                p.txt(x + .9, y + .6, cw, 2.6, str(gridno.get((r, c), "")), "", 4.6, (150, 150, 150)); continue
            t = (v - lo) / (hi - lo) if hi > lo else .5; col = heat_col(t); dark = t > .55
            p.rr(x + .3, y + .3, cw - .6, ch - .6, 1.2, col)
            p.txt(x, y + ch / 2 - 2.2, cw, 4.4, str(v), "B", fs, (255, 255, 255) if dark else INK, "C")
            p.txt(x + .9, y + .6, cw, 2.6, str(gridno.get((r, c), "")), "", 4.6, (255, 255, 255) if dark else (110, 110, 110))
            if (r, c) in low or (r, c) in high:
                p.set_fill_color(*((59, 130, 220) if (r, c) in low else (214, 60, 55))); p.rect(x + cw - 3.2, y + .6, 2.4, 2.4, "F")
    if ppa:
        r1, r2, c1, c2 = ppa; p.set_draw_color(*BRAND); p.set_line_width(.5); p.set_dash_pattern(1.2, .8)
        p.rect(x0 + r1 * cw, y0 + c1 * ch, (r2 - r1 + 1) * cw, (c2 - c1 + 1) * ch); p.set_dash_pattern()
    return lo, hi


def legend_bar(p, x, y, w, lo, hi):
    for i in range(60):
        p.set_fill_color(*heat_col(i / 59)); p.rect(x + i * w / 60, y, w / 60 + .2, 3, "F")
    p.txt(x - 16, y - .5, 15, 4, f"{lo:.0f}", "", 6.5, GRAY, "R"); p.txt(x + w + 1, y - .5, 20, 4, f"{hi:.0f}", "", 6.5, GRAY)


def notes_page(p, t, signer=""):
    p.newpage(t("notes_title"), "")
    p.txt(LX, 46, 40, 5, t("notes"), "B", 9)
    for i in range(10): p.hline(56 + i * 9, LX, RX)
    for i, lab in enumerate((t("measured_by"), t("approved_by"))):
        x = LX + i * 91; p.rr(x, 170, 87, 38, 3, (255, 255, 255), LINE); p.txt(x + 5, 173, 70, 4, lab, "M", 6.5, GRAY)
        if i == 0 and signer: p.txt(x + 5, 190, 77, 5, signer, "M", 8)
        p.hline(200, x + 5, x + 82); p.txt(x + 5, 201.5, 77, 4, t("name_sig"), "", 6.5, GRAY)


def _f(v, default=""):
    return v if v else default


def _num(s):
    try: return float(str(s).replace(",", "."))
    except Exception: return None


def cover_page(p, t, name, kind_title, chip, date, loc, by, R, C, seq, L, W, fiba=False, plain=False):
    p.newpage("", cover=True)
    p.logo_img(RX - 52, 14, 52)
    p.txt(LX, 92, 170, 5, kind_title, "M", 8.5, GRAY)
    p.set_xy(LX, 99); p.f("B", 26); p.multi_cell(170, 11, name or "-")
    ytag = max(p.get_y() + 3, 124)
    w = len(chip) * 2.6 + 12; p.rr(LX, ytag, w, 8.5, 4.25, YEL); p.txt(LX, ytag, w, 8.5, chip, "B", 8.5, INK, "C")
    # dekoratif ozet cizim: gercek izgara boyutunda nokta deseni (veriye bagli)
    gx, gy, gw = 36, 150, 138; gh = gw * (W / L) if L else gw * .65; gh = min(gh, 80)
    p.rr(gx - 6, gy - 6, gw + 12, gh + 12, 4, CARD, LINE)
    p.set_draw_color(205, 205, 200); p.set_line_width(.4); p.rect(gx, gy, gw, gh)
    if not plain: p.line(gx + gw / 2, gy, gx + gw / 2, gy + gh); p.ellipse(gx + gw / 2 - 9, gy + gh / 2 - 9, 18, 18)
    pts = [(gx + r * gw / max(R - 1, 1), gy + c * gh / max(C - 1, 1)) for (r, c) in seq]
    p.set_draw_color(215, 215, 210); p.set_line_width(.25)
    for a, b in zip(pts, pts[1:]): p.line(a[0], a[1], b[0], b[1])
    for i, (x, y) in enumerate(pts):
        p.set_fill_color(*(YEL if i == 0 else BRAND if i == len(pts) - 1 else (255, 255, 255))); p.set_draw_color(*BRAND); p.set_line_width(.2)
        p.ellipse(x - 1.1, y - 1.1, 2.2, 2.2, "DF")
    for i, (a, b) in enumerate(((t("date"), date), (t("location"), loc), (t("measured_by"), by))):
        x = LX + i * 60; p.txt(x, 246, 55, 4, a, "M", 6.5, GRAY); p.txt(x, 251, 58, 6, b or "-", "M", 10)
    p.txt(LX, 268, CW, 4, "sahgroup.net  ·  " + datetime.now().strftime("%d.%m.%Y %H:%M"), "", 7, GRAY)


def cover_sheet(p, t, proj, fi, std_name, grid_txt, fiba=False, areas_txt="", club=False, free=False, head_keys=None):
    p.newpage(t("cs_title"), t("cs_sub"))
    g = [(t("site") if free else (t("venue") if fiba else t("stadium")), proj.get("name"))]
    if club: g.append((t("club"), fi.get("club_name")))
    g += [(t("city"), proj.get("location")), (t("insp_date"), proj.get("date")), (t("insp_time"), fi.get("inspection_time"))]
    if fiba: g.append((t("areas"), areas_txt))
    else:
        wv, lv = fi.get("pitch_width"), fi.get("pitch_length")
        g.append((t("area") if free else t("pitch"), f"{lv} x {wv} m" if (wv and lv) else ""))
    g.append((t("weather"), fi.get("weather")))
    y1 = kv_card(p, LX, 46, 87, t("general"), g)
    ins = [(t("org"), fi.get("org_name")), (t("addr"), fi.get("org_address")), (t("phone"), fi.get("org_phone_email")),
           (t("insp_by"), fi.get("inspector_name")), (t("signature"), ""), (t("std"), std_name)]
    y2 = kv_card(p, LX + 91, 46, 87, t("inspection"), ins)
    y = max(y1, y2) + 6
    p.txt(LX, y, 100, 5, t("equipment"), "B", 9); y += 7
    cal = fi.get("cal_date") or ""
    rows = [(t("meter"), fi.get("meter_model") or "-", fi.get("meter_serial") or "-", cal or "-")]
    for i, k in enumerate(["probe_serial_eh", "probe_serial_ev0", "probe_serial_ev90", "probe_serial_ev180", "probe_serial_ev270"]):
        if head_keys is not None and ["Eh", "Ev0", "Ev90", "Ev180", "Ev270"][i] not in head_keys: continue
        rows.append((t("head", n=i) + ("  (Eh)" if i == 0 else f"  (Ev {[0, 90, 180, 270][i - 1]}°)"), fi.get("meter_model") or "-", fi.get(k) or "-", "-"))
    rows.append((t("colour_meter"), fi.get("colour_meter") or "-", fi.get("colour_meter_serial") or "-", fi.get("colour_meter_cal_date") or "-"))
    y = table(p, LX, y, [62, 52, 32, 32], [t("item"), t("model"), t("serial"), t("cal")], rows, 6.4)
    if not free: p.txt(LX, y + 1, CW, 4, t("cal_note"), "", 6.5, GRAY)
    y += 9
    p.txt(LX, y, 100, 5, t("grid"), "B", 9); p.txt(LX + 30, y, 150, 5, grid_txt, "", 7.5, GRAY); y += 8
    if not fiba:
        kv_card(p, LX, y, CW, t("luminaires"), [(t("manufacturer"), fi.get("lum1_manufacturer")), (t("lum_model"), fi.get("lum1_model"))], 7)


def grid_diagram(p, t, R, C, seq, L, W, fiba=False, ppa=None, plain=False):
    PW = 144; PH = PW * (W / L) if L else 93; PH = min(PH, 100); x0, y0 = 34, 62; dx, dy = PW / max(R - 1, 1), PH / max(C - 1, 1)
    p.rr(x0 - 4, y0 - 4, PW + 8, PH + 8, 3, (255, 255, 255), LINE)
    if plain:
        p.set_fill_color(240, 240, 237); p.rect(x0, y0, PW, PH, "F"); p.set_draw_color(205, 205, 200); p.set_line_width(.4); p.rect(x0, y0, PW, PH)
    elif not fiba:
        p.set_fill_color(228, 238, 210); p.rect(x0, y0, PW, PH, "F"); p.set_draw_color(255, 255, 255); p.set_line_width(.5)
        p.rect(x0, y0, PW, PH); p.line(x0 + PW / 2, y0, x0 + PW / 2, y0 + PH)
        k = PW / L; p.ellipse(x0 + PW / 2 - 9.15 * k, y0 + PH / 2 - 9.15 * k, 18.3 * k, 18.3 * k)
        for sx, sg in ((x0, 1), (x0 + PW, -1)):
            pw_, ph_, gw_, gh_ = 16.5 * k, 40.32 * PH / W, 5.5 * k, 18.32 * PH / W
            p.rect(sx if sg == 1 else sx - pw_, y0 + PH / 2 - ph_ / 2, pw_, ph_); p.rect(sx if sg == 1 else sx - gw_, y0 + PH / 2 - gh_ / 2, gw_, gh_)
    else:
        p.set_fill_color(235, 235, 232); p.rect(x0, y0, PW, PH, "F"); px, py = PW / 35, PH / 22
        p.set_fill_color(247, 232, 205); p.rect(x0 + 1.5 * px, y0 + 1.5 * py, 32 * px, 19 * py, "F")
        p.set_fill_color(236, 205, 165); p.rect(x0 + 3.5 * px, y0 + 3.5 * py, 28 * px, 15 * py, "F")
        p.set_draw_color(255, 255, 255); p.set_line_width(.5); p.rect(x0 + 3.5 * px, y0 + 3.5 * py, 28 * px, 15 * py)
        p.line(x0 + 17.5 * px, y0 + 3.5 * py, x0 + 17.5 * px, y0 + 18.5 * py); p.ellipse(x0 + 17.5 * px - 1.8 * px, y0 + 11 * py - 1.8 * px, 3.6 * px, 3.6 * px)
        p.set_draw_color(*BRAND); p.set_line_width(.4); p.set_dash_pattern(1.2, .8); p.rect(x0 + 1.5 * px, y0 + 1.5 * py, 32 * px, 19 * py); p.set_dash_pattern()
    pts = [(x0 + r * dx, y0 + c * dy) for (r, c) in seq]
    p.set_draw_color(130, 130, 130); p.set_line_width(.33)
    for a, b in zip(pts, pts[1:]): p.line(a[0], a[1], b[0], b[1])
    rad = max(2.0, min(3.3, dx * .36, dy * .36)); fs = 6.3 if rad > 3 else (5 if rad > 2.5 else 4.2)
    for i, (x, y) in enumerate(pts):
        p.set_draw_color(*BRAND); p.set_line_width(.28)
        p.set_fill_color(*(YEL if i == 0 else (BRAND if i == len(pts) - 1 else (255, 255, 255)))); p.ellipse(x - rad, y - rad, 2 * rad, 2 * rad, "DF")
        p.txt(x - rad, y - fs * .17, 2 * rad, fs * .35, str(i + 1), "B", fs, (255, 255, 255) if i == len(pts) - 1 else INK, "C")
    dir_labels(p, x0, y0, PW, PH, 4)
    return x0, y0, PW, PH


def _stats(vals):
    a = sum(vals) / len(vals); mn, mx = min(vals), max(vals)
    return a, mn, mx, (mn / mx if mx else 0), (mn / a if a else 0)


# ===================================================================== FIFA / UEFA
def _reqs(th, title, kind):
    avg = th.get(f"{title}_avg", th.get(f"{kind}_avg"))
    if avg is None: return None
    mn = th.get(f"{title}_min", th.get(f"{kind}_min"))
    u1 = th.get(f"{title}_u1", th["u1h"] if kind == "Eh" else th.get("u1v"))
    u2 = th.get(f"{title}_u2", th["u2h"] if kind == "Eh" else th.get("u2v"))
    return avg, mn, u1, u2


def build_match_pdf(data, lang, standards, assets_dir, out_path):
    t, num, val = make_translator(lang)
    proj, fi = data["project_info"], data["fifa_info"]; org, level = data["org"], data["level"]
    R, C = data["rows_count"], data["cols_count"]; seq = data["raw_sequence"]; meas = data["raw_measurements"]
    th = standards[org][level]; name = proj.get("name") or "-"; p = Rep(name, assets_dir, t)
    gn = {rc: i + 1 for i, rc in enumerate(seq)}; fm = data["fifa_metrics"]
    L = _num(fi.get("pitch_length")) or 105.0; W = _num(fi.get("pitch_width")) or 68.0
    std_name = f"{org} {level}"; incomplete = data["measured_count"] < data["total_points"]
    plane_name = {k: t("p_" + k) for k in PLANE_KEYS}
    cover_page(p, t, name, t("rep_title"), f"{org}  ·  {level}", proj.get("date"), proj.get("location"), proj.get("prepared_by") or fi.get("inspector_name"), R, C, seq, L, W)
    cover_sheet(p, t, proj, fi, f"{org} - {level}", f"{R} x {C}  ·  {data['total_points']} {t('points')}", club=(org == "UEFA"))

    # --- standart gereksinimleri
    p.newpage(t("std_title"), f"{org} - {level}  ·  {t('std_sub')}")
    y = 46; col = 0
    for title, kind in PROBES:
        x = LX + col * 91
        rq = _reqs(th, title, kind)
        if rq is None: rows = [(t("no_req"), "")]
        else:
            a, mn, u1, u2 = rq; rows = [(t("average"), f"> {a} lx")] + ([(t("minimum"), f"> {mn} lx")] if mn is not None else [])
            rows += ([(t("u1"), f"> {num(u1)}")] if u1 is not None else []) + ([(t("u2"), f"> {num(u2)}")] if u2 is not None else [])
        yy = kv_card(p, x, y, 87, plane_name[title], rows, 7); col += 1
        if col == 2: col = 0; y = yy + 5
        else: ymax = yy
    if col == 1:
        x = LX + 91
        mr = th.get("maur_ratio")
        rows = [(t("min_ratio"), f"> {num(mr)}"), (t("max_fail"), str(th.get("maur_max_fail")))] if mr is not None else [(t("maur_card"), val(th.get("maur", "")))]
        yy = kv_card(p, x, y, 87, t("maur_card"), rows, 7); y = max(yy, ymax) + 5
    rows = [(t("mcm"), val(th.get("mcm", ""))), (t("ff"), val(th.get("ff", ""))), (t("cct"), val(th.get("cct", ""))),
            (t("ra"), f">= {th.get('ra')} Ra"), (t("rg"), val(th.get("rg", "")))]
    y = kv_card(p, LX, y, CW, t("other_req"), rows, 6.8)
    p.txt(LX, y + 3, CW, 8, t("other_note"), "", 6.8, GRAY)

    # --- sonuc ozeti
    p.newpage(t("sum_title"), t("sum_sub", date=proj.get("date") or "-", n=data["measured_count"], t=data["total_points"]))
    ok_all = data["all_pass"]; p.rr(LX, 46, CW, 17, 3, OK_BG if ok_all else BAD_BG)
    p.txt(LX + 6, 48.2, CW - 12, 6, f"{t('complies') if ok_all else t('not_complies')}  -  {std_name}", "B", 10.5, OK_TX if ok_all else BAD_TX)
    mtxt = t("maur_line", f=data["maur_total_fail"], m=data["maur_max_fail"]) if data["maur_ratio"] is not None else t("maur_na")
    p.txt(LX + 6, 55.2, CW - 12, 5, mtxt, "", 7.5, OK_TX if ok_all else BAD_TX); y = 66
    if incomplete:
        p.rr(LX, y, CW, 7, 2, WARN_BG); p.txt(LX + 4, y + .8, CW - 8, 5.4, t("incomplete", n=data["measured_count"], t=data["total_points"]), "M", 7, WARN_TX); y += 10
    p.rr(LX, y, CW, 6.8, 1.6, BRAND)
    for s, w, xx in ((t("metric"), 72, 0), (t("req"), 36, 72), (t("meas"), 34, 108), (t("status"), 36, 142)):
        p.txt(LX + xx + 2, y + .6, w - 4, 5.6, s, "B", 7, (255, 255, 255), "L" if xx == 0 else "C")
    y += 7.6; no_req_lbl = "Bu yon icin gereksinim yok"
    for (glabel, crit), (title, _) in zip(data["plane_groups"], PROBES):
        p.rr(LX, y, CW, 5.4, 1.2, (240, 240, 236)); p.rr(LX, y, 1.4, 5.4, .6, YEL); p.txt(LX + 4, y + .2, 120, 5, plane_name[title], "B", 7); y += 5.9
        items = []
        for label, ref, v, ok in crit:
            if label == no_req_lbl: items.append((t("no_req"), "-", f"{t('average')} {v}", None)); continue
            lab = {"Ortalama >": t("average"), "Minimum >": t("minimum"), "Uniformity U1": t("u1m"), "Uniformity U2": t("u2m")}.get(label, label)
            ref_s = ("> " + str(ref).replace(".", ",")) if lang == "tr" else ("> " + str(ref)); items.append((lab, ref_s, str(v).replace(".", ",") if lang == "tr" else str(v), ok))
        m = fm[title]; items.append((t("max_ref"), "-", f"{m['max']:.0f}", None))
        if data["maur_ratio"] is not None: items.append((t("maur_fails"), "-", str(m["maur_fails"]), None))
        for lab, ref_s, ms_, ok in items:
            p.txt(LX + 4, y, 70, 4.6, lab, "", 6.8, INK); p.txt(LX + 72, y, 36, 4.6, ref_s, "", 6.8, GRAY, "C")
            p.txt(LX + 108, y, 34, 4.6, ms_, "M", 6.8, INK if ok is not False else BAD_TX, "C")
            if ok is not None: p.pill(LX + 150, y + .4, 20, 3.8, t("pass") if ok else t("fail"), ok, 5.3)
            y += 5.0
        y += 1.4

    # --- izgara + sira
    p.newpage(t("grid_title"), t("grid_sub"))
    x0, y0, PW, PH = grid_diagram(p, t, R, C, seq, L, W)
    p.txt(x0, y0 + PH + 16, PW, 4, t("spacing", L=f"{L:g}", a=R - 1, sa=f"{L / max(R - 1, 1):.3f}".rstrip("0").rstrip("."), W=f"{W:g}", b=C - 1, sb=f"{W / max(C - 1, 1):.3f}".rstrip("0").rstrip(".")), "", 7, GRAY, "C")

    # --- ham veri
    rows_all = [(i + 1, meas[i]["values"]) for i in range(len(seq)) if i in meas]
    per_page = 96; WD = [13, 15, 15, 15, 15, 15]; heads = ["Grid", "Eh", "Ev 0°", "Ev 90°", "Ev 180°", "Ev 270°"]
    for pg in range(0, max(len(rows_all), 1), per_page):
        chunk = rows_all[pg:pg + per_page]; half = (len(chunk) + 1) // 2
        p.newpage(t("raw_title"), t("raw_sub"))
        for h_ in range(2):
            part = chunk[h_ * half:(h_ + 1) * half]
            if not part: continue
            x = LX + h_ * 90; p.rr(x, 44, sum(WD), 6.2, 1.4, BRAND); xx = x
            for s, w in zip(heads, WD): p.txt(xx, 44.4, w, 5.4, s, "B", 6.5, (255, 255, 255), "C"); xx += w
            for j, (gno, vals) in enumerate(part):
                yy = 51 + j * 4.75
                if j % 2: p.set_fill_color(*CARD); p.rect(x, yy, sum(WD), 4.75, "F")
                xx = x
                for k, (v, w) in enumerate(zip([gno] + [vals.get(tk) for tk, _ in PROBES], WD)):
                    p.txt(xx, yy + .3, w, 4.2, "-" if v is None else str(v), "B" if k == 0 else "", 6.5, GRAY if k == 0 else INK, "C"); xx += w

    # --- isi haritalari
    crit_map = {title: {c[0]: c[3] for c in crit} for (gl, crit), (title, _) in zip(data["plane_groups"], PROBES)}
    for title, kind in PROBES:
        p.newpage(f"{t('map_title')}  ·  {plane_name[title]}", t("map_sub"))
        g = {(d["r"], d["c"]): d["values"].get(title) for d in meas.values()}
        cw = min(14.5, 168 / R); ch = min(14.5, 118 / C); x0 = (210 - R * cw) / 2; y0 = 56
        lo, hi = heatmap(p, g, R, C, x0, y0, cw, ch, gn); dir_labels(p, x0, y0, R * cw, C * ch)
        m = fm[title]; rq = _reqs(th, title, kind); cm = crit_map[title]
        legend_bar(p, 70, y0 + C * ch + 12, 70, lo, hi)
        cards = [("AVERAGE", f"{m['avg']:.0f}", (f"{t('reqk')} {rq[0]}" if rq else None), cm.get("Ortalama >")),
                 ("MINIMUM", f"{m['min']:.0f}", (f"{t('reqk')} {rq[1]}" if rq and rq[1] is not None else None), cm.get("Minimum >")),
                 ("MAXIMUM", f"{m['max']:.0f}", None, None),
                 ("U1", num(m["u1"]), (f"{t('reqk')} {num(rq[2])}" if rq and rq[2] is not None else None), cm.get("Uniformity U1")),
                 ("U2", num(m["u2"]), (f"{t('reqk')} {num(rq[3])}" if rq and rq[3] is not None else None), cm.get("Uniformity U2"))]
        for i, (la, v, rqs, ok) in enumerate(cards): kpi(p, LX + i * 36.25, 196, 33, 22, t(la), v, rqs, ok)

    # --- MAUR
    p.newpage(t("maur_title"), t("maur_sub"))
    if data["maur_ratio"] is None:
        p.rr(LX, 46, CW, 14, 3, CARD); p.txt(LX + 6, 50, CW - 12, 6, t("maur_na"), "M", 9, GRAY)
    else:
        rows = []
        for title, _ in PROBES:
            g = {(d["r"], d["c"]): d["values"].get(title) for d in meas.values() if d["values"].get(title) is not None}
            ratios = []
            for (r, c), v in g.items():
                for dr, dc in ((1, 0), (0, 1)):
                    n = (r + dr, c + dc)
                    if n in g and max(v, g[n]) > 0: ratios.append(min(v, g[n]) / max(v, g[n]))
            rows.append((plane_name[title], num(min(ratios)) if ratios else "-", str(fm[title]["maur_fails"]), f"> {num(data['maur_ratio'])}"))
        y = table(p, LX, 46, [70, 36, 36, 36], [t("plane"), t("lowest"), t("failures"), t("limit")], rows, 7, ["L", "C", "C", "C"])
        ok = data["maur_ok"]; p.rr(LX, y + 8, CW, 14, 3, OK_BG if ok else BAD_BG)
        p.txt(LX + 6, y + 11, CW - 12, 8, t("total_f", f=data["maur_total_fail"], m=data["maur_max_fail"]), "B", 10, OK_TX if ok else BAD_TX); y += 28
        any_d = any(fm[tk].get("maur_fail_details") for tk, _ in PROBES)
        if not any_d: p.txt(LX, y, CW, 5, t("no_pairs"), "", 7.5, OK_TX)
        else:
            for title, _ in PROBES:
                det = fm[title].get("maur_fail_details") or []
                if not det: continue
                if y > 235: p.newpage(t("maur_title"), t("maur_sub")); y = 46
                p.txt(LX, y, CW, 5, f"{plane_name[title]}  -  {len(det)} {t('pairs')}", "B", 8); y += 6
                rows = [(f"{item['grid1']}  ↔  {item['grid2']}".replace("↔", "<->"), str(item["v1"]), str(item["v2"]), num(item["ratio"])) for item in det]
                for k in range(0, len(rows), 30):
                    if y > 245: p.newpage(t("maur_title"), t("maur_sub")); y = 46
                    y = table(p, LX, y, [60, 38, 38, 38], [t("pair"), t("v1"), t("v2"), t("ratio")], rows[k:k + 30], 5.6, ["C", "C", "C", "C"]) + 6

    # --- ek veri
    p.newpage(t("add_title"), t("add_sub"))
    ne = t("not_entered")
    rows = [(t("avg_flicker"), val(th.get("ff", "")), fi.get("flicker_avg") or ne), (t("max_flicker"), val(th.get("ff", "")), fi.get("flicker_max") or ne),
            (t("cct"), th.get("cct", ""), fi.get("colour_temp_tc") or ne), (t("ra"), f">= {th.get('ra')} Ra", fi.get("colour_rendering_ra") or ne),
            (t("rg"), th.get("rg", ""), fi.get("glare_rating_rg") or ne)]
    table(p, LX, 46, [74, 52, 52], [t("param"), t("req"), t("meas")], rows, 8)
    notes_page(p, t, fi.get("inspector_name") or "")
    p.output(out_path)
    return out_path


# ===================================================================== FIBA
def build_fiba_pdf(data, lang, fiba_standards, assets_dir, out_path):
    t, num, val = make_translator(lang)
    proj, fi = data["project_info"], data["fifa_info"]; R, C = data["rows_count"], data["cols_count"]; seq = data["raw_sequence"]; meas = data["raw_measurements"]
    name = proj.get("name") or "-"; p = Rep(name, assets_dir, t); gn = {rc: i + 1 for i, rc in enumerate(seq)}
    P, T = fiba_standards["PPA"], fiba_standards["TPA"]; margin = data["ppa_margin"]; ok_all = data["all_pass"]
    cover_page(p, t, name, t("rep_title_bb"), "FIBA  ·  PPA / TPA", proj.get("date"), proj.get("location"), proj.get("prepared_by") or fi.get("inspector_name"), R, C, seq, 35, 22, True)
    cover_sheet(p, t, proj, fi, t("fiba_std"), f"{R} x {C}  ·  {data['total_points']} {t('points')}  ·  {t('round1')}  ·  {t('round2')}", fiba=True, areas_txt="TPA 22 x 35 m  /  PPA 19 x 32 m")

    p.newpage(t("std_title"), t("fiba_std") + "  ·  " + t("fiba_std_sub"))
    rows = [(t("ec_avg"), f"> {P['ec_avg']}", f"> {T['ec_avg']}"), (t("ec_u"), f"{num(P['ec_u1'], 1)} / {num(P['ec_u2'], 1)}", f"{num(T['ec_u1'], 1)} / {num(T['ec_u2'], 1)}"),
            (t("ev_avg"), f"> {P['ev_avg']}", f"> {T['ev_avg']}"), (t("ev_u"), f"{num(P['ev_u1'], 1)} / {num(P['ev_u2'], 1)}", f"{num(T['ev_u1'], 1)} / {num(T['ev_u2'], 1)}"),
            (t("ev_ratio"), f">= {num(P['ev_dir_ratio'], 1)}", f">= {num(T['ev_dir_ratio'], 1)}"), (t("eh_avg"), f"{P['eh_avg_min']} - {P['eh_avg_max']}", f"{T['eh_avg_min']} - {T['eh_avg_max']}"),
            (t("eh_u"), f"{num(P['eh_u1'], 1)} / {num(P['eh_u2'], 1)}", f"{num(T['eh_u1'], 1)} / {num(T['eh_u2'], 1)}")]
    y = table(p, LX, 46, [78, 50, 50], [t("param"), "PPA", "TPA"], rows, 8, ["L", "C", "C"])
    p.rr(LX, y + 8, CW, 20, 3, CARD); p.set_xy(LX + 5, y + 10.5); p.f("", 7, GRAY); p.multi_cell(CW - 10, 4.2, t("fiba_note"))

    def pill_row(y, label, req, meas_s, ok):
        p.txt(LX + 4, y, 74, 4.6, label, "", 6.8); p.txt(LX + 78, y, 34, 4.6, req, "", 6.8, GRAY, "C")
        p.txt(LX + 112, y, 34, 4.6, meas_s, "M", 6.8, INK if ok else BAD_TX, "C"); p.pill(LX + 152, y + .4, 20, 3.8, t("pass") if ok else t("fail"), ok, 5.3)

    for zone_name, th, ztitle in (("PPA", P, t("ppa_t")), ("TPA", T, t("tpa_t"))):
        zone = data["zones"].get(zone_name)
        p.newpage(f"{t('sum_title')}  ·  {zone_name}", t("fiba_sum_sub", date=proj.get("date") or "-", n=data["measured_count"], t=data["total_points"]))
        if zone is None:
            p.rr(LX, 46, CW, 14, 3, CARD); p.txt(LX + 6, 50, CW - 12, 6, "-", "M", 9, GRAY); continue
        zok = zone["zone_ok"]; p.rr(LX, 46, CW, 17, 3, OK_BG if zok else BAD_BG)
        p.txt(LX + 6, 48.2, CW - 12, 6, f"{ztitle}  -  {t('complies') if zok else t('not_complies')}", "B", 10, OK_TX if zok else BAD_TX)
        p.txt(LX + 6, 55.2, CW - 12, 5, (t("complies") if ok_all else t("not_complies")) + "  (PPA + TPA)", "", 7.5, OK_TX if ok_all else BAD_TX)
        y = 68; p.rr(LX, y, CW, 6.8, 1.6, BRAND)
        for s, w, xx in ((t("metric"), 78, 0), (t("req"), 34, 78), (t("meas"), 34, 112), (t("status"), 36, 146)): p.txt(LX + xx + 2, y + .6, w - 4, 5.6, s, "B", 7, (255, 255, 255), "L" if xx == 0 else "C")
        y += 8
        def block(title_s):
            nonlocal y
            p.rr(LX, y, CW, 5.4, 1.2, (240, 240, 236)); p.rr(LX, y, 1.4, 5.4, .6, YEL); p.txt(LX + 4, y + .2, 120, 5, title_s, "B", 7); y += 5.9
        ec = zone["EC"]; block("EC - " + t("p_EC"))
        if ec["avg"] is None:
            pill_row(y, t("ec_row"), f"> {th['ec_avg']}", t("not_meas", m=ec["measured_count"], t=ec["total_count"]), False); y += 5.0
        else:
            pill_row(y, t("ec_row"), f"> {th['ec_avg']}", f"{ec['avg']:.0f}", ec["avg"] >= th["ec_avg"]); y += 5.0
            pill_row(y, t("ecu1"), f">= {num(th['ec_u1'])}", num(ec["u1"]), ec["u1"] >= th["ec_u1"]); y += 5.0
            pill_row(y, t("ecu2"), f">= {num(th['ec_u2'])}", num(ec["u2"]), ec["u2"] >= th["ec_u2"]); y += 5.0
        y += 1.4; block("EV - " + ("Dikey" if lang == "tr" else "Vertical"))
        for dname, dd in zone["EV"]["per_direction"].items():
            deg = dname[2:]
            pill_row(y, t("evd_avg", d=deg), f"> {th['ev_avg']}", f"{dd['avg']:.0f}", dd["avg"] >= th["ev_avg"]); y += 5.0
            pill_row(y, t("evd_u1", d=deg), f">= {num(th['ev_u1'])}", num(dd["u1"]), dd["u1"] >= th["ev_u1"]); y += 5.0
            pill_row(y, t("evd_u2", d=deg), f">= {num(th['ev_u2'])}", num(dd["u2"]), dd["u2"] >= th["ev_u2"]); y += 5.0
        pill_row(y, t("evr"), f">= {num(th['ev_dir_ratio'])}", num(zone["EV"]["dir_ratio"]), zone["EV"]["dir_ratio_ok"]); y += 6.4
        eh = zone["EH"]; block("EH - " + t("p_Eh"))
        if eh["avg"] is None:
            pill_row(y, t("ehr"), f"{th['eh_avg_min']} - {th['eh_avg_max']}", t("not_meas", m=eh["measured_count"], t=eh["total_count"]), False)
        else:
            pill_row(y, t("ehr"), f"{th['eh_avg_min']} - {th['eh_avg_max']}", f"{eh['avg']:.0f}", eh["avg_ok"]); y += 5.0
            pill_row(y, t("ehu1"), f">= {num(th['eh_u1'])}", num(eh["u1"]), eh["u1"] >= th["eh_u1"]); y += 5.0
            pill_row(y, t("ehu2"), f">= {num(th['eh_u2'])}", num(eh["u2"]), eh["u2"] >= th["eh_u2"])

    p.newpage(t("grid_title"), t("fiba_grid_sub"))
    x0, y0, PW, PH = grid_diagram(p, t, R, C, seq, 35, 22, fiba=True)
    p.txt(x0, y0 + PH + 16, PW, 4, t("fiba_grid_cap"), "", 7, GRAY, "C")

    # --- ham veri (EC ve Eh dahil)
    rows_all = [(i + 1, meas[i]["values"]) for i in range(len(seq)) if i in meas]
    WD = [20, 26, 26, 26, 26, 26, 28]; heads = ["Grid", "Ev 0°", "Ev 90°", "Ev 180°", "Ev 270°", "EC", "Eh"]
    for pg in range(0, max(len(rows_all), 1), 50):
        p.newpage(t("raw_title"), t("raw_sub")); y = 44; p.rr(LX, y, sum(WD), 6.2, 1.4, BRAND); xx = LX
        for s, w in zip(heads, WD): p.txt(xx, y + .4, w, 5.4, s, "B", 6.5, (255, 255, 255), "C"); xx += w
        for j, (gno, vals) in enumerate(rows_all[pg:pg + 50]):
            yy = 51 + j * 4.8
            if j % 2: p.set_fill_color(*CARD); p.rect(LX, yy, sum(WD), 4.8, "F")
            xx = LX
            for k, (v, w) in enumerate(zip([gno, vals.get("Ev0"), vals.get("Ev90"), vals.get("Ev180"), vals.get("Ev270"), vals.get("EC"), vals.get("Eh")], WD)):
                p.txt(xx, yy + .3, w, 4.2, "-" if v is None else str(v), "B" if k == 0 else "", 6.5, GRAY if k == 0 else INK, "C"); xx += w

    in_ppa = lambda r, c: margin <= r < R - margin and margin <= c < C - margin
    for key in ["EC", "Eh", "Ev0", "Ev90", "Ev180", "Ev270"]:
        p.newpage(f"{t('map_title')}  ·  {t('p_' + key)}", t("map_sub_fiba"))
        g = {(d["r"], d["c"]): d["values"].get(key) for d in meas.values()}
        cw = min(168 / R, 118 / C); x0 = (210 - R * cw) / 2; y0 = 56
        heatmap(p, g, R, C, x0, y0, cw, cw, gn, (margin, R - margin - 1, margin, C - margin - 1), 6.4); dir_labels(p, x0, y0, R * cw, C * cw)
        yk = y0 + C * cw + 12
        for zi, (zone, sel) in enumerate((("PPA", lambda r, c: in_ppa(r, c)), ("TPA", lambda r, c: True))):
            vals = [v for (r, c), v in g.items() if v is not None and sel(r, c)]; yy = yk + zi * 22; p.txt(LX, yy + 6, 14, 5, zone, "B", 8, BRAND)
            if not vals:
                p.txt(LX + 15, yy + 6, 100, 5, "-", "", 8, GRAY); continue
            a, mn, mx, u1, u2 = _stats(vals)
            for i, (la, v) in enumerate((("AVERAGE", f"{a:.0f}"), ("MINIMUM", f"{mn}"), ("MAXIMUM", f"{mx}"), ("U1", num(u1)), ("U2", num(u2)))): kpi(p, LX + 15 + i * 32.6, yy, 30, 18, t(la), v)
    notes_page(p, t, fi.get("inspector_name") or "")
    p.output(out_path)
    return out_path


# ===================================================================== SERBEST (standartsiz) OLCUM
def build_free_pdf(data, lang, assets_dir, out_path):
    """Standart secilmeden alinan olcum raporu. Hicbir standarda gore uygun/degil DEMEZ.
    Kullanici hedef girdiyse yalnizca o hedeflerle karsilastirir (data['checks'])."""
    t, num, val = make_translator(lang)
    proj, fi = data["project_info"], data["fifa_info"]; R, C = data["rows_count"], data["cols_count"]
    seq = data["raw_sequence"]; meas = data["raw_measurements"]; probes = data["probes"]; metrics = data["metrics"]
    checks = data["checks"]; has_t = data["has_targets"]
    name = proj.get("name") or "-"; p = Rep(name, assets_dir, t); gn = {rc: i + 1 for i, rc in enumerate(seq)}
    Ld, Wd = _num(fi.get("pitch_length")), _num(fi.get("pitch_width")); L = Ld or float(R); W = Wd or float(C)
    plane_name = {k: t("p_" + k) for k in PLANE_KEYS}; incomplete = data["measured_count"] < data["total_points"]
    cover_page(p, t, name, t("rep_title"), t("chip_free"), proj.get("date"), proj.get("location"), proj.get("prepared_by") or fi.get("inspector_name"), R, C, seq, L, W, plain=True)
    cover_sheet(p, t, proj, fi, t("no_std"), f"{R} x {C}  ·  {data['total_points']} {t('points')}", free=True, head_keys=probes)

    # --- sonuc ozeti
    p.newpage(t("free_title"), t("free_sub", date=proj.get("date") or "-", n=data["measured_count"], t=data["total_points"]))
    y = 46
    if has_t:
        ok = data["all_pass"]; p.rr(LX, y, CW, 14, 3, OK_BG if ok else BAD_BG)
        p.txt(LX + 6, y + 1.8, CW - 12, 6, t("targets_ok") if ok else t("targets_fail"), "B", 10.5, OK_TX if ok else BAD_TX)
        p.txt(LX + 6, y + 8, CW - 12, 5, t("free_target_note"), "", 7, OK_TX if ok else BAD_TX)
    else:
        p.rr(LX, y, CW, 12, 3, CARD, LINE); p.txt(LX + 6, y + 3, CW - 12, 6, t("free_note"), "M", 8, GRAY)
    y += 18 if has_t else 16
    if incomplete:
        p.rr(LX, y, CW, 7, 2, WARN_BG); p.txt(LX + 4, y + .8, CW - 8, 5.4, t("incomplete", n=data["measured_count"], t=data["total_points"]), "M", 7, WARN_TX); y += 10
    p.rr(LX, y, CW, 6.8, 1.6, BRAND)
    hcols = ((t("metric"), 72, 0), (t("target"), 36, 72), (t("meas"), 34, 108), (t("status"), 36, 142)) if has_t else ((t("metric"), 72, 0), (t("meas"), 40, 72))
    for s_, w, xx in hcols:
        p.txt(LX + xx + 2, y + .6, w - 4, 5.6, s_, "B", 7, (255, 255, 255), "L" if xx == 0 else "C")
    y += 7.6
    for title in probes:
        p.rr(LX, y, CW, 5.4, 1.2, (240, 240, 236)); p.rr(LX, y, 1.4, 5.4, .6, YEL); p.txt(LX + 4, y + .2, 120, 5, plane_name[title], "B", 7); y += 5.9
        m = metrics.get(title)
        if m is None:
            p.txt(LX + 4, y, 120, 4.6, t("no_values"), "", 6.8, GRAY); y += 6.4; continue
        ck = {c["key"]: c for c in checks.get(title, [])}
        for key, lab, vs in (("avg", t("average"), f"{m['avg']:.0f}"), ("min", t("minimum"), f"{m['min']:.0f}"), ("max", t("maximum"), f"{m['max']:.0f}"),
                             ("u1", t("u1m"), num(m["u1"])), ("u2", t("u2m"), num(m["u2"]))):
            c = ck.get(key); ok = c["ok"] if c else None
            p.txt(LX + 4, y, 70, 4.6, lab, "", 6.8, INK)
            if c: p.txt(LX + 72, y, 36, 4.6, ">= " + (num(c["req"]) if key in ("u1", "u2") else f"{c['req']:g}"), "", 6.8, GRAY, "C")
            elif has_t: p.txt(LX + 72, y, 36, 4.6, "-", "", 6.8, GRAY, "C")
            p.txt(LX + (108 if has_t else 72), y, 34 if has_t else 40, 4.6, vs, "M", 6.8, INK if ok is not False else BAD_TX, "C")
            if ok is not None: p.pill(LX + 150, y + .4, 20, 3.8, t("pass") if ok else t("fail"), ok, 5.3)
            y += 5.0
        y += 1.4
    if has_t: p.txt(LX, y + 2, CW, 4, t("free_target_note"), "", 6.8, GRAY)

    # --- izgara + sira
    p.newpage(t("grid_title"), t("grid_sub"))
    x0, y0, PW, PH = grid_diagram(p, t, R, C, seq, L, W, plain=True)
    yy = y0 + PH + 16
    if Ld and Wd:
        p.txt(x0, yy, PW, 4, t("spacing", L=f"{Ld:g}", a=R - 1, sa=f"{Ld / max(R - 1, 1):.3f}".rstrip("0").rstrip("."), W=f"{Wd:g}", b=C - 1, sb=f"{Wd / max(C - 1, 1):.3f}".rstrip("0").rstrip(".")), "", 7, GRAY, "C"); yy += 12
    else: yy += 4

    # --- ham veri (yalnizca secilen problar)
    rows_all = [(i + 1, meas[i]["values"]) for i in range(len(seq)) if i in meas]
    k = len(probes); cwid = max(14, min(20, 76 // k)); WD = [14] + [cwid] * k
    lab = {"Eh": "Eh", "Ev0": "Ev 0°", "Ev90": "Ev 90°", "Ev180": "Ev 180°", "Ev270": "Ev 270°"}
    heads = ["Grid"] + [lab[x] for x in probes]; per_page = 96
    for pg in range(0, max(len(rows_all), 1), per_page):
        chunk = rows_all[pg:pg + per_page]; half = (len(chunk) + 1) // 2
        p.newpage(t("raw_title"), t("raw_sub"))
        for h_ in range(2):
            part = chunk[h_ * half:(h_ + 1) * half]
            if not part: continue
            x = LX + h_ * 90; p.rr(x, 44, sum(WD), 6.2, 1.4, BRAND); xx = x
            for s_, w in zip(heads, WD): p.txt(xx, 44.4, w, 5.4, s_, "B", 6.5, (255, 255, 255), "C"); xx += w
            for j, (gno, vals) in enumerate(part):
                yy = 51 + j * 4.75
                if j % 2: p.set_fill_color(*CARD); p.rect(x, yy, sum(WD), 4.75, "F")
                xx = x
                for kk, (v, w) in enumerate(zip([gno] + [vals.get(x_) for x_ in probes], WD)):
                    p.txt(xx, yy + .3, w, 4.2, "-" if v is None else str(v), "B" if kk == 0 else "", 6.5, GRAY if kk == 0 else INK, "C"); xx += w

    # --- isi haritalari
    for title in probes:
        m = metrics.get(title)
        if m is None: continue
        p.newpage(f"{t('map_title')}  ·  {plane_name[title]}", t("map_sub"))
        g = {(d["r"], d["c"]): d["values"].get(title) for d in meas.values()}
        cw = min(14.5, 168 / R); ch = min(14.5, 118 / C); x0 = (210 - R * cw) / 2; y0 = 56
        lo, hi = heatmap(p, g, R, C, x0, y0, cw, ch, gn); dir_labels(p, x0, y0, R * cw, C * ch)
        legend_bar(p, 70, y0 + C * ch + 12, 70, lo, hi)
        ck = {c["key"]: c for c in checks.get(title, [])}
        def rq(key, isnum):
            c = ck.get(key)
            return (f"{t('reqk')} " + (num(c["req"]) if isnum else f"{c['req']:g}")) if c else None
        cards = [("AVERAGE", f"{m['avg']:.0f}", rq("avg", False), ck.get("avg", {}).get("ok")),
                 ("MINIMUM", f"{m['min']:.0f}", rq("min", False), ck.get("min", {}).get("ok")),
                 ("MAXIMUM", f"{m['max']:.0f}", None, None),
                 ("U1", num(m["u1"]), rq("u1", True), ck.get("u1", {}).get("ok")),
                 ("U2", num(m["u2"]), rq("u2", True), ck.get("u2", {}).get("ok"))]
        for i, (la, v, rqs, ok) in enumerate(cards): kpi(p, LX + i * 36.25, 196, 33, 22, t(la), v, rqs, ok)
    notes_page(p, t, fi.get("inspector_name") or "")
    p.output(out_path)
    return out_path
