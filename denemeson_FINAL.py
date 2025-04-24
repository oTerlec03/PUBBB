def update_display(active_slot, weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref,
                   weapon_value, weapon_value_shadow1, weapon_value_shadow2,
                   sight_value, sight_value_shadow1, sight_value_shadow2,
                   muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2,
                   grip_value, grip_value_shadow1, grip_value_shadow2,
                   stock_value, stock_value_shadow1, stock_value_shadow2,
                   position_value, position_value_shadow1, position_value_shadow2):
    global translations
    none_text = translations.get("none", "YOK")
    slot_data = (
        weapon1_data if active_slot == 1 else
        weapon2_data if active_slot == 2 else
        pistol_data
    )
    weapon_name = slot_data['name']
    display_name = f"{weapon_name} [{'AUTO' if mk14_auto_mode_ref[0] else 'SINGLE'}]" if weapon_name == "Mk14" else weapon_name
    attachments = slot_data.get('attachments', {})
    formatted_attachments = {key: value.replace("_", " ") if value and value != "YOK" else none_text for key, value in attachments.items()}
    colors = [
        "red" if weapon_name == "YOK" else "green",
        "red" if formatted_attachments.get('durbun', none_text) == none_text else "green",
        "red" if formatted_attachments.get('namlu', none_text) == none_text else "green",
        "red" if formatted_attachments.get('tutamak', none_text) == none_text else "green",
        "red" if formatted_attachments.get('dipcik', none_text) == none_text else "green",
        "red" if current_position_ref[0] == "YOK" else "green"
    ]
    values = [
        f"[{none_text}]" if weapon_name == "YOK" else f"[{display_name}]",
        f"[{formatted_attachments.get('durbun', none_text)}]",
        f"[{formatted_attachments.get('namlu', none_text)}]",
        f"[{formatted_attachments.get('tutamak', none_text)}]",
        f"[{formatted_attachments.get('dipcik', none_text)}]",
        f"[{none_text}]" if current_position_ref[0] == "YOK" else f"[{translations.get(current_position_ref[0].lower(), current_position_ref[0])}]"
    ]
    for (value, shadow1, shadow2), color, text in zip(
        [
            (weapon_value, weapon_value_shadow1, weapon_value_shadow2),
            (sight_value, sight_value_shadow1, sight_value_shadow2),
            (muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2),
            (grip_value, grip_value_shadow1, grip_value_shadow2),
            (stock_value, stock_value_shadow1, stock_value_shadow2),
            (position_value, position_value_shadow1, position_value_shadow2)
        ], colors, values):
        value.config(text=text, fg=color)
        shadow1.config(text=text, fg=color)
        shadow2.config(text=text, fg=color)

import cv2
import numpy as np
import os
import json
from mss import mss
import time
import win32gui
import win32con
import win32api
from pynput import keyboard as pynput_keyboard
from pynput import mouse as pynput_mouse
from pynput.mouse import Button, Controller as MouseController
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk, Label, Canvas

# Loglamayı ayarla
logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# AppData\Roaming\PUBGMacro\Config dizinini oluştur
appdata_dir = os.path.join(os.getenv('APPDATA'), 'PUBGMacro', 'Config')
if not os.path.exists(appdata_dir):
    os.makedirs(appdata_dir)

# Dosya yolları
cps_file = os.path.join(appdata_dir, "rapidfire_cps.txt")
config_file = os.path.join(appdata_dir, "config.json")
macro_folder = r'C:\Users\HAN\Desktop\PUBG_Silah_Makrolari'
dil_paketleri_path = r'C:\Users\HAN\Desktop\PUBG Dil Paketleri'

# Klasör yolları
weapon_names_path = r'C:\Users\HAN\Desktop\PUBG_Silah_Isimleri'
attachments_paths = {
    "durbun": r'C:\Users\HAN\Desktop\PUBG Durbunler',
    "namlu": r'C:\Users\HAN\Desktop\PUBG Namlu Uclari',
    "tutamak": r'C:\Users\HAN\Desktop\PUBG Tutamaclar',
    "dipcik": r'C:\Users\HAN\Desktop\PUBG Dipcikler'
}

# Silah bilgileri (Tabancalar dahil)
weapon_info = {
    "AKM": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": False, "type": "AR"},
    "Beryl M762": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "AR"},
    "G36C": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "AR"},
    "M416": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": True, "type": "AR"},
    "M16A4": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": True, "type": "DMR"},
    "SCAR-L": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "AR"},
    "Mk47 Mutant": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": True, "type": "DMR"},
    "QBZ": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "AR"},
    "AUG": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "AR"},
    "Groza": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": False, "type": "AR"},
    "ACE32": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": True, "type": "AR"},
    "K2": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": False, "type": "AR"},
    "FAMAS": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": False, "type": "AR"},
    "SLR": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": True, "type": "DMR"},
    "Mini14": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": False, "type": "DMR"},
    "SKS": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": True, "type": "DMR"},
    "QBU": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": False, "type": "DMR"},
    "Mk14": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": True, "type": "DMR"},
    "Mk12": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "DMR"},
    "Dragunov": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": True, "type": "DMR"},
    "PP-19 Bizon": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": False, "type": "SMG"},
    "Tommy Gun": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "SMG"},
    "UMP": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "SMG"},
    "Micro UZI": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": True, "type": "SMG"},
    "Vector": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": True, "type": "SMG"},
    "MP5K": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": True, "type": "SMG"},
    "P90": {"durbun": False, "namlu": False, "tutamak": False, "dipcik": False, "type": "SMG"},
    "JS9": {"durbun": True, "namlu": True, "tutamak": False, "dipcik": False, "type": "SMG"},
    "MP9": {"durbun": True, "namlu": False, "tutamak": False, "dipcik": True, "type": "SMG"},
    "VSS": {"durbun": False, "namlu": False, "tutamak": False, "dipcik": True, "type": "Sniper"},
    "DP-28": {"durbun": True, "namlu": False, "tutamak": False, "dipcik": False, "type": "LMG"},
    "M249": {"durbun": True, "namlu": False, "tutamak": False, "dipcik": True, "type": "LMG"},
    "MG3": {"durbun": True, "namlu": False, "tutamak": False, "dipcik": False, "type": "LMG"},
    "P18C": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "Pistol"},
    "P1911": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "Pistol"},
    "P92": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": False, "type": "Pistol"},
    "R1895": {"durbun": False, "namlu": True, "tutamak": False, "dipcik": False, "type": "Pistol"},
    "Skorpion": {"durbun": True, "namlu": True, "tutamak": True, "dipcik": True, "type": "Pistol"},
    "R45": {"durbun": True, "namlu": False, "tutamak": True, "dipcik": False, "type": "Pistol"},
    "Deagle": {"durbun": True, "namlu": False, "tutamak": True, "dipcik": False, "type": "Pistol"},
}

# DMR silahlar listesi (Tabancalar eklendi)
dmr_weapons = [
    "SLR", "Mini14", "SKS", "QBU", "Mk14", "Mk12", "Dragunov", "M16A4", "Mk47 Mutant",
    "P1911", "P92", "R1895", "R45", "Deagle"
]

# Global değişkenler (FINAL_22'den eklenenler dahil)
macro_cache = {}
rapid_fire_cps = 2.0
is_cps_locked = False
locked_cps = None
current_preset_index = 0
grenade_active = False
mouse_controller = MouseController()
is_running = False
is_macro_clicking = False
move_sensitivity = 1.0
move_speed = 0.05
click_thread = None
move_thread = None
weapon1_bbox = (1328, 84, 1821, 290)
weapon2_bbox = (1330, 316, 1820, 517)
pistol_bbox = (1330, 541, 1824, 728)
global_slider_window = None
global_slider_outline = None
last_active_slot = None
translations = {}
tab_inventory_active = False
inventory_scan_thread = None
crosshair_window = None
crosshair_canvas = None
w_pressed = False
shift_pressed = False
reddot_window = None
reddot_canvas = None
space_pressed = False
space_thread = None
right_click_pressed = False
left_click_pressed = False

# Dil dosyalarını yükleme fonksiyonu
def load_translations(lang_code="tr"):
    lang_files = {
        "tr": "tr.json",
        "en": "en.json",
        "es": "es.json",
        "pt": "pt.json",
        "ar": "ar.json",
        "fr": "fr.json",
        "de": "de.json",
        "it": "it.json",
        "ru": "ru.json",
        "uk": "uk.json"
    }
    try:
        with open(os.path.join(dil_paketleri_path, lang_files[lang_code]), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Dil dosyası yükleme hatası: {e}")
        return {}

# Pencere konumlarını kaydetme ve yükleme
def save_window_positions(main_pos, slider_pos, lang="tr"):
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({
                "main_window": main_pos,
                "slider_window": slider_pos,
                "selected_language": lang
            }, f)
        logging.debug(f"Konfigürasyon kaydedildi: main={main_pos}, slider={slider_pos}, lang={lang}")
    except Exception as e:
        logging.error(f"Konfigürasyon kaydetme hatası: {e}")

def load_window_positions():
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except:
        logging.debug("Konfigürasyon dosyası bulunamadı, varsayılan ayarlar kullanılıyor")
        return {"main_window": None, "slider_window": None, "selected_language": "tr"}

# DMR tespiti
def is_dmr(weapon_name):
    return weapon_name in dmr_weapons

# Rapid Fire Tıklama
def run_clicks(slot_data):
    global is_running, is_macro_clicking, rapid_fire_cps
    logging.debug(f"run_clicks başladı: CPS={rapid_fire_cps}, Slot={slot_data['slot']}")
    while is_running and slot_data["rapid_fire_enabled"] and rapid_fire_cps is not None:
        if is_game_active() and not grenade_active:
            is_macro_clicking = True
            mouse_controller.click(Button.left, 1)
            is_macro_clicking = False
            time.sleep(1 / rapid_fire_cps)
        else:
            time.sleep(0.01)
    logging.debug(f"run_clicks sona erdi (Slot: {slot_data['slot']})")

# Mouse kaydırma
def run_move(slot_data):
    global is_running, move_sensitivity, move_speed
    logging.debug(f"run_move başladı: Sensitivity={move_sensitivity}, Move Speed={move_speed*1000}ms, Slot={slot_data['slot']}")
    while is_running and slot_data["active"]:
        if is_game_active() and not grenade_active:
            movement = int(move_sensitivity * 0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, movement, 0, 0)
            logging.debug(f"Mouse hareketi: {movement} piksel")
            time.sleep(move_speed)
        else:
            time.sleep(0.01)
    logging.debug(f"run_move sona erdi (Slot: {slot_data['slot']})")

# Crosshair ve Red Dot Fonksiyonları (FINAL_22'den eklendi)
def show_crosshair():
    global crosshair_window, crosshair_canvas
    if crosshair_window is None or not crosshair_window.winfo_exists():
        crosshair_window = tk.Toplevel()
        crosshair_window.overrideredirect(True)
        crosshair_window.attributes("-topmost", True)
        crosshair_window.attributes("-transparentcolor", "black")
        crosshair_window.geometry("50x50+{}+{}".format(
            root.winfo_screenwidth() // 2 - 25,
            root.winfo_screenheight() // 2 - 25
        ))
        crosshair_canvas = tk.Canvas(crosshair_window, width=50, height=50, bg="black", highlightthickness=0)
        crosshair_canvas.pack()
        crosshair_canvas.create_line(25, 0, 25, 50, fill="white", width=2)
        crosshair_canvas.create_line(0, 25, 50, 25, fill="white", width=2)
        crosshair_window.withdraw()
    crosshair_window.deiconify()

def hide_crosshair():
    global crosshair_window
    if crosshair_window and crosshair_window.winfo_exists():
        crosshair_window.withdraw()

def show_reddot():
    global reddot_window, reddot_canvas
    if reddot_window is None or not reddot_window.winfo_exists():
        reddot_window = tk.Toplevel()
        reddot_window.overrideredirect(True)
        reddot_window.attributes("-topmost", True)
        reddot_window.attributes("-transparentcolor", "black")
        reddot_window.geometry("10x10+{}+{}".format(
            root.winfo_screenwidth() // 2 - 5,
            root.winfo_screenheight() // 2 - 5
        ))
        reddot_canvas = tk.Canvas(reddot_window, width=10, height=10, bg="black", highlightthickness=0)
        reddot_canvas.pack()
        reddot_canvas.create_oval(0, 0, 10, 10, fill="red", outline="")

def hide_reddot():
    global reddot_window
    if reddot_window and reddot_window.winfo_exists():
        reddot_window.destroy()
    reddot_window = None

def send_space():
    global space_pressed
    while space_pressed:
        win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0)
        if not space_pressed:
            break
        time.sleep(0.1)

# Görsel yükleme
def load_templates(folder_path, use_canny=False, use_color=False, attachment_type=None):
    templates = {}
    base_names = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            template = cv2.imread(os.path.join(folder_path, filename))
            if template is not None:
                scale_factor = 1.0 if attachment_type in ["durbun", "dipcik"] else 0.5
                template = cv2.resize(template, (0, 0), fx=scale_factor, fy=scale_factor)
                name_without_ext = filename.split('.')[0]
                if '_' in name_without_ext:
                    parts = name_without_ext.split('_')
                    if parts[-1].isdigit():
                        base_name = '_'.join(parts[:-1])
                    else:
                        base_name = name_without_ext
                else:
                    base_name = name_without_ext
                if use_canny:
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
                    template = cv2.Canny(template, 50, 150)
                elif not use_color:
                    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                templates[name_without_ext] = template
                base_names[name_without_ext] = base_name
    logging.info(f"{folder_path} klasöründen {len(templates)} görsel yüklendi.")
    return templates, base_names

# Ekran görüntüsü alma
def capture_screen_area(bbox, use_canny=False, use_color=False, attachment_type=None):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with mss() as sct:
                monitor = {"left": bbox[0], "top": bbox[1], "width": bbox[2] - bbox[0], "height": bbox[3] - bbox[1]}
                screenshot = sct.grab(monitor)
                screenshot = np.array(screenshot)
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                scale_factor = 1.0 if attachment_type in ["durbun", "dipcik"] else 0.5
                screenshot = cv2.resize(screenshot, (0, 0), fx=scale_factor, fy=scale_factor)
                if use_canny:
                    screenshot = cv2.Canny(screenshot, 50, 150)
                elif not use_color:
                    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
                if attachment_type not in ["tutamak"]:
                    if bbox == weapon1_bbox:
                        cv2.rectangle(screenshot, (98, 142), (165, 206), (255, 255, 255), -1)
                    elif bbox == weapon2_bbox:
                        cv2.rectangle(screenshot, (98, 137), (161, 200), (255, 255, 255), -1)
                    elif bbox == pistol_bbox:
                        cv2.rectangle(screenshot, (98, 137), (161, 200), (255, 255, 255), -1)
            return screenshot
        except Exception as e:
            logging.error(f"Ekran görüntüsü alma hatası (Deneme {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(0.1)
    return None

def match_single_template(args):
    screen_area, name, template, base_name, threshold, method = args
    try:
        if template.shape[0] <= screen_area.shape[0] and template.shape[1] <= screen_area.shape[1]:
            result = cv2.matchTemplate(screen_area, template, method)
            if method == cv2.TM_SQDIFF_NORMED:
                loc = np.where(result <= threshold)
                if len(loc[0]) > 0:
                    return (name, base_name, np.min(result))
            else:
                loc = np.where(result >= threshold)
                if len(loc[0]) > 0:
                    return (name, base_name, np.max(result))
    except Exception as e:
        logging.error(f"Eşleme hatası: {name}, {e}")
    return None

def match_templates(screen_area, templates, base_names, threshold=0.7, attachment_type=None, weapon_type=None, weapon_name=None):
    if screen_area is None:
        logging.warning(f"Ekran alanı None, eşleşme yapılamadı.")
        return []
    threshold = 0.5 if attachment_type == "durbun" else 0.25 if attachment_type == "dipcik" else 0.55
    filtered_templates = {}
    if attachment_type == "tutamak" and weapon_type == "Pistol" and weapon_name == "Skorpion":
        allowed_grips = ["Half Grip", "Laser Sight", "Light Grip", "Vertical Foregrip"]
        filtered_templates = {
            k: v for k, v in templates.items() 
            if any(k.startswith(grip) for grip in allowed_grips)
        }
        logging.debug(f"Skorpion tutamak filtreleme: {list(filtered_templates.keys())}")
    elif attachment_type == "tutamak" and weapon_type == "Pistol":
        filtered_templates = {k: v for k, v in templates.items() if k.startswith("Laser Sight")}
        logging.debug(f"Tabanca tutamak filtreleme: {list(filtered_templates.keys())}")
    elif attachment_type == "dipcik" and weapon_name in ["Micro UZI", "Skorpion"]:
        filtered_templates = {k: v for k, v in templates.items() if k.startswith("Stock UZI")}
        logging.debug(f"Micro UZI/Skorpion dipçik filtreleme: {list(filtered_templates.keys())}")
    else:
        for name, template in templates.items():
            if attachment_type == "namlu":
                if weapon_type == "SMG" and ("SMG_" in name or "HG_SMG_" in name):
                    filtered_templates[name] = template
                elif weapon_type == "AR" and "AR_" in name:
                    filtered_templates[name] = template
                elif weapon_type in ["DMR", "Sniper"]:
                    if weapon_name in ["M16A4", "Mk47 Mutant"] and "AR_" in name:
                        filtered_templates[name] = template
                    elif "SR_" in name or "AR_" in name:
                        filtered_templates[name] = template
                elif weapon_type == "LMG" and "LMG_" in name:
                    filtered_templates[name] = template
                elif weapon_type == "Pistol" and "HG_SMG_" in name:
                    filtered_templates[name] = template
            elif attachment_type == "dipcik":
                if weapon_type in ["DMR", "Sniper"] and "CheekPad" in name:
                    filtered_templates[name] = template
                elif weapon_info.get(weapon_name, {}).get("dipcik", False) and (
                    "Stock AR Composite" in name or "Stock AR Heavy" in name
                ):
                    filtered_templates[name] = template
                elif (weapon_type == "AR" or weapon_name in ["M16A4", "Mk47 Mutant", "M249"]) and "Stock AR Composite" in name:
                    filtered_templates[name] = template
            else:
                filtered_templates[name] = template
    method = cv2.TM_SQDIFF_NORMED if attachment_type == "dipcik" else cv2.TM_CCOEFF_NORMED
    args_list = [(screen_area, name, template, base_names[name], threshold, method) 
                 for name, template in filtered_templates.items()]
    with ThreadPoolExecutor() as executor:
        matches = list(filter(None, executor.map(match_single_template, args_list)))
    logging.debug(f"{attachment_type} eşleşmeleri: {len(matches)} bulundu, Matches={matches}")
    return matches

def get_best_match(matches, attachment_type=None, weapon_type=None):
    if not matches:
        return None
    thresholds = {
        "AR": 0.78,
        "SMG": 0.70,
        "DMR": 0.72,
        "Sniper": 0.72,
        "Pistol": 0.70,
        "Grip": 0.75
    }
    if attachment_type == "dipcik":
        best_match = min(matches, key=lambda x: x[2])
    else:
        best_match = max(matches, key=lambda x: x[2])
    if attachment_type == "durbun":
        return "1x" if best_match[1].startswith("1x_") else best_match[1]
    elif attachment_type == "namlu":
        if weapon_type == "AR":
            if best_match[1] == "AR_Supressor" and best_match[2] < 0.82:
                return "YOK"
            elif best_match[2] < thresholds.get("AR", 0.78):
                return "YOK"
        elif weapon_type in ["SMG", "Pistol"]:
            if best_match[2] < thresholds.get("SMG", 0.70):
                return "YOK"
        elif weapon_type in ["DMR", "Sniper"]:
            if best_match[2] < thresholds.get("DMR", 0.72):
                return "YOK"
            elif best_match[1].startswith("SR_"):
                return best_match[1].replace("SR_", "AR_")
        else:
            return "YOK"
    elif attachment_type == "tutamak":
        if best_match[2] < thresholds.get("Grip", 0.75):
            return "YOK"
    return best_match[1]

def is_game_active(window_title="PUBG: BATTLEGROUNDS"):
    hwnd = win32gui.GetForegroundWindow()
    return window_title in win32gui.GetWindowText(hwnd)

def update_cps_file():
    global rapid_fire_cps
    try:
        with open(cps_file, "w", encoding="utf-8") as f:
            f.write(str(rapid_fire_cps))
        logging.debug(f"CPS dosyası güncellendi: {rapid_fire_cps}")
    except Exception as e:
        logging.error(f"CPS dosyası güncelleme hatası: {e}")

def show_notification(message):
    notification = tk.Toplevel()
    notification.overrideredirect(True)
    notification.configure(bg="#1E2A44")
    screen_width = notification.winfo_screenwidth()
    notification.geometry(f"{screen_width}x30+0+{-30}")
    label = tk.Label(notification, text=message, font=("Arial", 10, "bold"), fg="white", bg="#1E2A44")
    label.pack(expand=True, fill="both")
    notification.attributes("-topmost", True)
    def slide_in(y_pos=-30):
        if y_pos < 0:
            notification.geometry(f"{screen_width}x30+0+{y_pos}")
            y_pos += 3
            notification.after(10, slide_in, y_pos)
        else:
            notification.geometry(f"{screen_width}x30+0+0")
            notification.after(450, slide_out)
    def slide_out(y_pos=0):
        if y_pos > -30:
            notification.geometry(f"{screen_width}x30+0+{y_pos}")
            y_pos -= 3
            notification.after(10, slide_out, y_pos)
        else:
            notification.destroy()
    slide_in()

def update_ui_language(root, translations, *ui_elements):
    try:
        (weapon_label, _, _, _, sight_label, _, _, _, muzzle_label, _, _, _, 
         grip_label, _, _, _, stock_label, _, _, _, position_label, _, _, _) = ui_elements
        weapon_label.config(text=translations.get("weapon", "SİLAH:"))
        sight_label.config(text=translations.get("sight", "DÜRBÜN:"))
        muzzle_label.config(text=translations.get("muzzle", "NAMLU:"))
        grip_label.config(text=translations.get("grip", "TUTAMAK:"))
        stock_label.config(text=translations.get("stock", "DİPÇİK:"))
        position_label.config(text=translations.get("position", "POZİSYON:"))
        if global_slider_window and hasattr(global_slider_window, 'cps_label'):
            global_slider_window.cps_label.config(text=translations.get("rapid_fire_speed", "Rapid Fire Hızı:"))
            global_slider_window.slow_label.config(text=translations.get("slow", "Yavaş"))
            global_slider_window.fast_label.config(text=translations.get("fast", "Hızlı"))
            global_slider_window.manual_cps_label.config(text=translations.get("manual_cps", "Manuel CPS:"))
            global_slider_window.lock_label.config(text=translations.get("locked", "Kilitli:"))
            global_slider_window.language_label.config(text=translations.get("language", "Dil:"))
        logging.debug("Arayüz metinleri güncellendi")
    except Exception as e:
        logging.error(f"Arayüz metinleri güncelleme hatası: {e}")

def on_language_change(event, root, window_objects):
    global translations
    lang_map = {
        "English": "en",
        "Español": "es",
        "Português": "pt",
        "Türkçe": "tr",
        "العربية": "ar",
        "Français": "fr",
        "Deutsch": "de",
        "Italiano": "it",
        "Русский": "ru",
        "Українська": "uk"
    }
    try:
        selected_lang_display = event.widget.get()
        lang_code = lang_map.get(selected_lang_display, "tr")
        translations = load_translations(lang_code)
        update_ui_language(root, translations, *window_objects)
        saved_pos = load_window_positions()
        save_window_positions(
            saved_pos.get('main_window'),
            saved_pos.get('slider_window'),
            lang_code
        )
        show_notification(translations.get("language_changed", "Dil değiştirildi: ") + selected_lang_display)
        logging.debug(f"Dil değiştirildi: {selected_lang_display} ({lang_code})")
    except Exception as e:
        logging.error(f"Dil değiştirme hatası: {e}")
        show_notification(translations.get("error", "Hata: Dil değiştirilemedi"))

def capture_all_screens():
    slots = [
        (weapon1_bbox, True, False, None, "weapon1"),
        (weapon2_bbox, True, False, None, "weapon2"),
        (pistol_bbox, True, False, None, "pistol")
    ]
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(capture_screen_area, bbox, use_canny, use_color, attachment_type): slot_name 
                   for bbox, use_canny, use_color, attachment_type, slot_name in slots}
        for future in futures:
            slot_name = futures[future]
            try:
                results[slot_name] = future.result()
            except Exception as e:
                logging.error(f"Ekran yakalama hatası ({slot_name}): {e}")
                results[slot_name] = None
    return results

def capture_attachment_screens(bbox, supported_attachments, weapon_type, weapon_name):
    tasks = []
    for key in ["durbun", "namlu", "tutamak", "dipcik"]:
        if supported_attachments.get(key, False):
            use_canny = key in ["durbun", "dipcik"]
            tasks.append((bbox, use_canny, False, key))
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(capture_screen_area, bbox, use_canny, use_color, attachment_type): attachment_type 
                   for bbox, use_canny, use_color, attachment_type in tasks}
        for future in futures:
            attachment_type = futures[future]
            try:
                results[attachment_type] = future.result()
            except Exception as e:
                logging.error(f"Ek parçası ekran yakalama hatası ({attachment_type}): {e}")
                results[attachment_type] = None
    return results

def process_slot(weapon_area, bbox, current_weapon_data, weapon_templates, attachment_templates, attachment_base_names, slot_name):
    logging.debug(f"{slot_name} tarama başlıyor: weapon_area shape={weapon_area.shape if weapon_area is not None else None}")
    matched_weapons = match_templates(weapon_area, weapon_templates[0], weapon_templates[1], threshold=0.7)
    detected_weapon = get_best_match(matched_weapons) if matched_weapons else "YOK"
    logging.debug(f"Silah algılandı - {slot_name}: {detected_weapon}, Matches={len(matched_weapons)}, Scores={[m[2] for m in matched_weapons]}")
    attachments = current_weapon_data["attachments"].copy() if current_weapon_data["name"] == detected_weapon else {}
    if detected_weapon in weapon_info:
        supported_attachments = weapon_info[detected_weapon]
        weapon_type = supported_attachments["type"]
        attachment_areas = capture_attachment_screens(bbox, supported_attachments, weapon_type, detected_weapon)
        for key, area in attachment_areas.items():
            threshold = 0.5 if key == "durbun" else 0.25 if key == "dipcik" else 0.55
            att_matches = match_templates(area, attachment_templates[key], attachment_base_names[key], threshold, key, weapon_type, detected_weapon)
            attachment = get_best_match(att_matches, key, weapon_type)
            if key == "namlu" and supported_attachments.get("tutamak", False):
                if attachment and attachment.startswith("YOK"):
                    attachment = "YOK"
            attachments[key] = attachment if attachment else "YOK"
            logging.debug(f"{slot_name}, {key} tarama: Matches={len(att_matches)}, Scores={[m[2] for m in att_matches]}")
    else:
        logging.debug(f"{slot_name} için desteklenmeyen silah: {detected_weapon}")
        for key in ["durbun", "namlu", "tutamak", "dipcik"]:
            attachments[key] = "YOK"
    return detected_weapon, attachments

def check_inventory(root, weapon_templates, attachment_templates, attachment_base_names, 
                    weapon1_data, weapon2_data, pistol_data, current_weapon_ref, 
                    current_position_ref, mk14_auto_mode_ref, previous_weapon1_data, 
                    previous_weapon2_data, previous_pistol_data):
    if not is_game_active() or not tab_inventory_active:
        logging.debug("Oyun aktif değil veya tarama durduruldu, tarama yapılmadı.")
        return False

    # Önceki verileri güncelle
    previous_weapon1_data["name"] = weapon1_data["name"]
    previous_weapon1_data["attachments"] = weapon1_data["attachments"].copy()
    previous_weapon2_data["name"] = weapon2_data["name"]
    previous_weapon2_data["attachments"] = weapon2_data["attachments"].copy()
    previous_pistol_data["name"] = pistol_data["name"]
    previous_pistol_data["attachments"] = pistol_data["attachments"].copy()

    screen_areas = capture_all_screens()
    weapon1_area = screen_areas.get("weapon1")
    weapon2_area = screen_areas.get("weapon2")
    pistol_area = screen_areas.get("pistol")

    slot_tasks = [
        (weapon1_area, weapon1_bbox, weapon1_data, weapon_templates, attachment_templates, attachment_base_names, "Slot 1"),
        (weapon2_area, weapon2_bbox, weapon2_data, weapon_templates, attachment_templates, attachment_base_names, "Slot 2"),
        (pistol_area, pistol_bbox, pistol_data, weapon_templates, attachment_templates, attachment_base_names, "Tabanca")
    ]
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_slot, *task): task[-1] for task in slot_tasks}
        for future in futures:
            slot_name = futures[future]
            try:
                results[slot_name] = future.result()
            except Exception as e:
                logging.error(f"{slot_name} işleme hatası: {e}")
                results[slot_name] = (previous_weapon1_data["name"] if slot_name == "Slot 1" else 
                                      previous_weapon2_data["name"] if slot_name == "Slot 2" else 
                                      previous_pistol_data["name"], 
                                      previous_weapon1_data["attachments"] if slot_name == "Slot 1" else 
                                      previous_weapon2_data["attachments"] if slot_name == "Slot 2" else 
                                      previous_pistol_data["attachments"])

    # Yalnızca değişen verileri güncelle
    def update_if_changed(slot_data, detected_name, detected_attachments):
        changed = False
        if slot_data["name"] != detected_name:
            slot_data["name"] = detected_name
            slot_data["attachments"] = detected_attachments
            changed = True
        else:
            for key, value in detected_attachments.items():
                if slot_data["attachments"].get(key) != value:
                    slot_data["attachments"][key] = value
                    changed = True
        if changed:
            call_macro(slot_data["name"], slot_data["attachments"], slot_data, current_position_ref[0], mk14_auto_mode_ref[0])
        return changed

    changed1 = update_if_changed(weapon1_data, *results.get("Slot 1", (weapon1_data["name"], weapon1_data["attachments"])))
    changed2 = update_if_changed(weapon2_data, *results.get("Slot 2", (weapon2_data["name"], weapon2_data["attachments"])))
    changed3 = update_if_changed(pistol_data, *results.get("Tabanca", (pistol_data["name"], pistol_data["attachments"])))

    # Arayüzü yalnızca değişiklik varsa güncelle
    if changed1 or changed2 or changed3 or current_weapon_ref[0] != last_active_slot:
        root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, 
                                             weapon_value, weapon_value_shadow1, weapon_value_shadow2, 
                                             sight_value, sight_value_shadow1, sight_value_shadow2, 
                                             muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, 
                                             grip_value, grip_value_shadow1, grip_value_shadow2, 
                                             stock_value, stock_value_shadow1, stock_value_shadow2, 
                                             position_value, position_value_shadow1, position_value_shadow2))
        logging.debug(f"Tarama sonrası - Slot 1: Name={weapon1_data['name']}, Attachments={weapon1_data['attachments']}, Changed={changed1}")
        logging.debug(f"Tarama sonrası - Slot 2: Name={weapon2_data['name']}, Attachments={weapon2_data['attachments']}, Changed={changed2}")
        logging.debug(f"Tarama sonrası - Tabanca: Name={pistol_data['name']}, Attachments={pistol_data['attachments']}, Changed={changed3}")
        logging.debug(f"GUI güncelleme - Aktif slot: {current_weapon_ref[0]}")
    return True

def start_inventory_scan(args):
    global tab_inventory_active
    root, weapon_templates, attachment_templates, attachment_base_names, weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, previous_weapon1_data, previous_weapon2_data, previous_pistol_data = args
    while tab_inventory_active:
        if is_game_active():
            check_inventory(root, weapon_templates, attachment_templates, attachment_base_names, 
                            weapon1_data, weapon2_data, pistol_data, current_weapon_ref, 
                            current_position_ref, mk14_auto_mode_ref, previous_weapon1_data, 
                            previous_weapon2_data, previous_pistol_data)
        time.sleep(0.05)
    logging.debug("Envanter tarama döngüsü sona erdi.")

def create_slider_window(root, outline_window, window_objects):
    def toggle_slider_window():
        global global_slider_window, global_slider_outline
        logging.debug("toggle_slider_window çağrıldı")
        try:
            if global_slider_window is None or not global_slider_window.winfo_exists():
                logging.debug("Rapid fire penceresi oluşturuluyor")
                try:
                    if root and root.winfo_exists():
                        root.withdraw()
                        logging.debug("root gizlendi")
                    else:
                        logging.warning("root None veya mevcut değil")
                except Exception as e:
                    logging.error(f"root gizleme hatası: {e}")
                try:
                    if outline_window and outline_window.winfo_exists():
                        outline_window.withdraw()
                        logging.debug("outline_window gizlendi")
                    else:
                        logging.warning("outline_window None veya mevcut değil")
                except Exception as e:
                    logging.error(f"outline_window gizleme hatası: {e}")
                global_slider_window = tk.Toplevel()
                global_slider_window.overrideredirect(True)
                window_width, window_height = 300, 180
                saved_pos = load_window_positions()
                x_pos, y_pos = 100, 100
                if saved_pos:
                    slider_pos = saved_pos.get("slider_window")
                    if slider_pos:
                        x_pos, y_pos = slider_pos
                    else:
                        try:
                            main_x = root.winfo_x() if root and root.winfo_exists() else 100
                            main_y = root.winfo_y() if root and root.winfo_exists() else 100
                            x_pos = main_x + 220
                            y_pos = main_y
                        except tk.TclError:
                            pass
                global_slider_window.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
                global_slider_window.attributes("-topmost", True)
                global_slider_window.configure(bg="#162038")
                logging.debug(f"Rapid fire penceresi oluşturuldu: {window_width}x{window_height}+{x_pos}+{y_pos}")
                border_offset = 2
                outline_width = window_width + (border_offset * 2)
                outline_height = window_height + (border_offset * 2)
                outline_x = x_pos - border_offset
                outline_y = y_pos - border_offset
                global_slider_outline = tk.Toplevel(global_slider_window)
                global_slider_outline.overrideredirect(True)
                global_slider_outline.geometry(f"{outline_width}x{outline_height}+{int(outline_x)}+{int(outline_y)}")
                global_slider_outline.attributes("-topmost", False)
                global_slider_outline.attributes("-alpha", 0.75)
                global_slider_outline.configure(bg="#2A3555")
                outline_canvas = tk.Canvas(global_slider_outline, bg="#070E1B", highlightthickness=0)
                outline_canvas.pack(fill="both", expand=True)
                outline_canvas.create_rectangle(0, 0, outline_width, outline_height, outline="#3A4555", width=4)
                logging.debug(f"Rapid fire outline penceresi oluşturuldu: {outline_width}x{outline_height}+{int(outline_x)}+{int(outline_y)}")
                global_slider_window.cps_label = tk.Label(global_slider_window, text=translations.get("rapid_fire_speed", "Rapid Fire Hızı:"), font=("Arial", 10, "bold"), fg="white", bg="#162038")
                global_slider_window.cps_label.pack(pady=5)
                cps_slider_frame = tk.Frame(global_slider_window, bg="#162038")
                cps_slider_frame.pack(pady=5)
                global_slider_window.slow_label = tk.Label(cps_slider_frame, text=translations.get("slow", "Yavaş"), font=("Arial", 8), fg="white", bg="#162038")
                global_slider_window.slow_label.pack(side=tk.LEFT, padx=5)
                cps_slider = tk.Scale(cps_slider_frame, from_=2, to=20, orient=tk.HORIZONTAL, length=200, resolution=0.1, bg="#162038", fg="white", highlightthickness=0, troughcolor="#1E2A44", showvalue=0)
                cps_slider.set(rapid_fire_cps if rapid_fire_cps is not None else 2.0)
                cps_slider.pack(side=tk.LEFT)
                global_slider_window.fast_label = tk.Label(cps_slider_frame, text=translations.get("fast", "Hızlı"), font=("Arial", 8), fg="white", bg="#162038")
                global_slider_window.fast_label.pack(side=tk.LEFT, padx=5)
                cps_textbox_frame = tk.Frame(global_slider_window, bg="#162038")
                cps_textbox_frame.pack(pady=5)
                global_slider_window.manual_cps_label = tk.Label(cps_textbox_frame, text=translations.get("manual_cps", "Manuel CPS:"), font=("Arial", 8), fg="white", bg="#162038")
                global_slider_window.manual_cps_label.pack(side=tk.LEFT, padx=5)
                cps_textbox = tk.Entry(cps_textbox_frame, width=10, bg="#1E2A44", fg="white", insertbackground="white")
                cps_textbox.insert(0, str(rapid_fire_cps) if rapid_fire_cps is not None else "2.0")
                cps_textbox.pack(side=tk.LEFT, padx=5)
                lock_frame = tk.Frame(global_slider_window, bg="#162038")
                lock_frame.pack(pady=5)
                lock_var = tk.BooleanVar(value=is_cps_locked)
                global_slider_window.lock_label = tk.Label(lock_frame, text=translations.get("locked", "Kilitli:"), font=("Arial", 8), fg="white", bg="#162038")
                global_slider_window.lock_label.pack(side=tk.LEFT)
                lock_checkbox = tk.Checkbutton(lock_frame, variable=lock_var, font=("Arial", 8), fg="white", bg="#162038", 
                                            selectcolor="#1E2A44", command=lambda: on_lock_toggle(lock_var.get()))
                lock_checkbox.pack(side=tk.LEFT)
                language_frame = tk.Frame(global_slider_window, bg="#162038")
                language_frame.pack(pady=5)
                global_slider_window.language_label = tk.Label(language_frame, text=translations.get("language", "Dil:"), font=("Arial", 8), fg="white", bg="#162038")
                global_slider_window.language_label.pack(side=tk.LEFT)
                language_options = [
                    "English", "Español", "Português", "Türkçe", "العربية",
                    "Français", "Deutsch", "Italiano", "Русский", "Українська"
                ]
                saved_pos = load_window_positions()
                selected_lang = saved_pos.get("selected_language", "tr")
                lang_map_reverse = {
                    "en": "English",
                    "es": "Español",
                    "pt": "Português",
                    "tr": "Türkçe",
                    "ar": "العربية",
                    "fr": "Français",
                    "de": "Deutsch",
                    "it": "Italiano",
                    "ru": "Русский",
                    "uk": "Українська"
                }
                language_var = tk.StringVar(value=lang_map_reverse.get(selected_lang, "Türkçe"))
                language_combobox = ttk.Combobox(language_frame, textvariable=language_var, 
                                                values=language_options, state="readonly", width=12)
                language_combobox.pack(side=tk.LEFT, padx=5)
                def combobox_selected(event):
                    logging.debug(f"Combobox seçimi: {language_var.get()}")
                    on_language_change(event, root, window_objects)
                language_combobox.bind("<<ComboboxSelected>>", combobox_selected)
                logging.debug("Rapid fire penceresi bileşenleri eklendi")
                close_label = tk.Label(global_slider_window, text="X", font=("Arial", 10, "bold"), fg="#3A4555", bg="#162038")
                close_label.place(x=window_width-20, y=5, width=15, height=15)
                def on_enter(event):
                    close_label.config(fg="#2A3555")
                def on_leave(event):
                    close_label.config(fg="#3A4555")
                def close_program():
                    logging.debug("X butonuna tıklandı, program kapatılıyor")
                    try:
                        if global_slider_window:
                            global_slider_window.destroy()
                        if global_slider_outline:
                            global_slider_outline.destroy()
                        if root:
                            root.destroy()
                        if outline_window:
                            outline_window.destroy()
                        os._exit(0)
                    except Exception as e:
                        logging.error(f"Program kapatma hatası: {e}")
                close_label.bind("<Enter>", on_enter)
                close_label.bind("<Leave>", on_leave)
                close_label.bind("<Button-1>", lambda e: close_program())
                logging.debug("X kapatma butonu eklendi")
                def update_rapid_fire_cps(val):
                    global rapid_fire_cps
                    if not is_cps_locked:
                        rapid_fire_cps = float(val)
                        cps_textbox.delete(0, tk.END)
                        cps_textbox.insert(0, str(rapid_fire_cps))
                        update_cps_file()
                        show_notification(f"{translations.get('cps_updated', 'CPS Güncellendi:')} {rapid_fire_cps}")
                def update_from_cps_textbox(event=None):
                    global rapid_fire_cps
                    if not is_cps_locked:
                        try:
                            value = float(cps_textbox.get())
                            if value < 2:
                                value = 2
                            elif value > 20:
                                value = 20
                            rapid_fire_cps = value
                            cps_slider.set(rapid_fire_cps)
                            update_cps_file()
                            show_notification(f"{translations.get('cps_updated', 'CPS Güncellendi:')} {rapid_fire_cps}")
                        except ValueError:
                            cps_textbox.delete(0, tk.END)
                            cps_textbox.insert(0, str(rapid_fire_cps) if rapid_fire_cps is not None else "2.0")
                def on_lock_toggle(locked):
                    global rapid_fire_cps, is_cps_locked, locked_cps, current_preset_index
                    is_cps_locked = locked
                    locked_cps = rapid_fire_cps if locked else None
                    cps_slider.config(state="disabled" if locked else "normal")
                    cps_textbox.config(state="disabled" if locked else "normal")
                    if locked:
                        current_preset_index = 0
                        current_slot_data = (
                            weapon1_data if current_weapon_ref[0] == 1 else
                            weapon2_data if current_weapon_ref[0] == 2 else
                            pistol_data
                        )
                        macro_name = current_slot_data.get("macro_name")
                        if macro_name:
                            if current_slot_data["name"] in ["M16A4", "Mk47 Mutant", "P1911", "P92", "R1895", "R45", "Deagle"]:
                                preset_file = os.path.join(macro_folder, f"{macro_name}_AUTO.json")
                            else:
                                preset_file = os.path.join(macro_folder, f"{macro_name}_{current_preset_index + 1}.json")
                            if os.path.exists(preset_file):
                                with open(preset_file, "r", encoding="utf-8") as f:
                                    macro_data = json.load(f)
                                rapid_fire_cps = macro_data.get("rapid_fire_speed", rapid_fire_cps)
                                update_cps_file()
                                if current_slot_data["name"] in ["M16A4", "Mk47 Mutant", "P1911", "P92", "R1895", "R45", "Deagle"]:
                                    show_notification(f"{translations.get('rapid_fire_speed', 'Rapid Fire Hızı:')} AUTO")
                                else:
                                    show_notification(f"{translations.get('preset', 'Preset')} 1 - CPS: {rapid_fire_cps}")
                            else:
                                show_notification(f"{translations.get('preset', 'Preset')} 1 - [{translations.get('none', 'YOK')}]")
                cps_slider.config(command=update_rapid_fire_cps)
                cps_textbox.bind("<Return>", update_from_cps_textbox)
                global_slider_window.drag_data = {"x": 0, "y": 0, "dragging": False}
                def start_drag(event):
                    if event.widget == global_slider_window:
                        global_slider_window.drag_data["x"] = event.x_root - global_slider_window.winfo_x()
                        global_slider_window.drag_data["y"] = event.y_root - global_slider_window.winfo_y()
                        global_slider_window.drag_data["dragging"] = True
                def on_drag(event):
                    if global_slider_window.drag_data["dragging"]:
                        x = event.x_root - global_slider_window.drag_data["x"]
                        y = event.y_root - global_slider_window.drag_data["y"]
                        global_slider_window.geometry(f"+{int(x)}+{int(y)}")
                        outline_x = x - 2
                        outline_y = y - 2
                        if global_slider_outline:
                            global_slider_outline.geometry(f"+{int(outline_x)}+{int(outline_y)}")
                        saved_pos = load_window_positions()
                        save_window_positions(saved_pos.get('main_window'), (x, y), saved_pos.get('selected_language', 'tr'))
                def stop_drag(event):
                    global_slider_window.drag_data["dragging"] = False
                def sync_outline_with_slider():
                    try:
                        if global_slider_window and global_slider_window.winfo_exists() and global_slider_outline and global_slider_outline.winfo_exists():
                            border_offset = 2
                            x = global_slider_window.winfo_x()
                            y = global_slider_window.winfo_y()
                            outline_x = x - border_offset
                            outline_y = y - border_offset
                            global_slider_outline.geometry(f"+{int(outline_x)}+{int(outline_y)}")
                        global_slider_window.after(100, sync_outline_with_slider)
                    except:
                        pass
                sync_outline_with_slider()
                global_slider_window.bind("<Button-1>", start_drag)
                global_slider_window.bind("<B1-Motion>", on_drag)
                global_slider_window.bind("<ButtonRelease-1>", stop_drag)
                def close_slider():
                    global global_slider_window, global_slider_outline
                    logging.debug("close_slider çağrıldı")
                    try:
                        saved_pos = load_window_positions()
                        slider_pos = (global_slider_window.winfo_x(), global_slider_window.winfo_y()) if global_slider_window and global_slider_window.winfo_exists() else None
                        save_window_positions(saved_pos.get('main_window'), slider_pos, saved_pos.get('selected_language', 'tr'))
                        if global_slider_window:
                            global_slider_window.destroy()
                            global_slider_window = None
                        if global_slider_outline:
                            global_slider_outline.destroy()
                            global_slider_outline = None
                        if root:
                            root.deiconify()
                        if outline_window:
                            outline_window.deiconify()
                        logging.debug("Rapid fire penceresi kapatıldı, ana pencereler geri getirildi")
                    except Exception as e:
                        logging.error(f"close_slider hatası: {e}")
                global_slider_window.protocol("WM_DELETE_WINDOW", close_slider)
                global_slider_window.bind("<Escape>", lambda e: close_slider())
                logging.debug("Rapid fire penceresi tamamen oluşturuldu")
            else:
                logging.debug("Rapid fire penceresi zaten açık, kapatılıyor")
                try:
                    saved_pos = load_window_positions()
                    slider_pos = (global_slider_window.winfo_x(), global_slider_window.winfo_y()) if global_slider_window and global_slider_window.winfo_exists() else None
                    save_window_positions(saved_pos.get('main_window'), slider_pos, saved_pos.get('selected_language', 'tr'))
                    if global_slider_window:
                        global_slider_window.destroy()
                        global_slider_window = None
                    if global_slider_outline:
                        global_slider_outline.destroy()
                        global_slider_outline = None
                    if root:
                        root.deiconify()
                    if outline_window:
                        outline_window.deiconify()
                    logging.debug("Rapid fire penceresi kapatıldı")
                except Exception as e:
                    logging.error(f"Rapid fire penceresi kapatma hatası: {e}")
        except Exception as e:
            logging.error(f"toggle_slider_window genel hata: {e}")
            try:
                if root:
                    root.deiconify()
                if outline_window:
                    outline_window.deiconify()
            except Exception as e2:
                logging.error(f"Ana pencereleri geri getirme hatası: {e2}")
    return toggle_slider_window

def create_window():
    global root  # FINAL_22'den gelen güncelleme
    root = tk.Tk()
    root.title("Envanter Bilgisi")
    saved_pos = load_window_positions()
    window_width, window_height = 215, 120
    if saved_pos and 'main_window' in saved_pos and saved_pos['main_window']:
        x_pos, y_pos = saved_pos['main_window']
    else:
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.9)
    root.overrideredirect(True)
    root.configure(bg="#162038")
    outline_width, outline_height = int(window_width * 1.04), int(window_height * 1.06)
    outline_x = x_pos - (outline_width - window_width) // 2
    outline_y = y_pos - (outline_height - window_height) // 2
    outline_window = tk.Toplevel(root)
    outline_window.overrideredirect(True)
    outline_window.geometry(f"{outline_width}x{outline_height}+{outline_x}+{outline_y}")
    outline_window.attributes("-topmost", False)
    outline_window.attributes("-alpha", 0.75)
    outline_window.configure(bg="#2A3555")
    outline_canvas = tk.Canvas(outline_window, bg="#070E1B", highlightthickness=0)
    outline_canvas.pack(fill="both", expand=True)
    outline_canvas.create_rectangle(0, 0, outline_width, outline_height, outline="#3A4555", width=4)
    root.drag_start_x = 0
    root.drag_start_y = 0
    def start_drag(event):
        root.drag_start_x = event.x_root - root.winfo_x()
        root.drag_start_y = event.y_root - root.winfo_y()
    def on_main_drag(event):
        x = event.x_root - root.drag_start_x
        y = event.y_root - root.drag_start_y
        root.geometry(f"+{x}+{y}")
        outline_x = x - (outline_width - window_width) // 2
        outline_y = y - (outline_height - window_height) // 2
        outline_window.geometry(f"+{outline_x}+{outline_y}")
        saved_pos = load_window_positions()
        save_window_positions((x, y), saved_pos.get('slider_window'), saved_pos.get('selected_language', 'tr'))
    canvas = tk.Canvas(root, bg="#162038", highlightthickness=0)
    canvas.place(x=0, y=0, width=215, height=120)
    for i in range(20, 120, 20):
        canvas.create_line(0, i, 215, i, fill="gray", width=2)
    global translations
    selected_lang = saved_pos.get("selected_language", "tr")
    translations = load_translations(selected_lang)
    none_text = translations.get("none", "YOK")
    labels = [
        translations.get("weapon", "SİLAH:"),
        translations.get("sight", "DÜRBÜN:"),
        translations.get("muzzle", "NAMLU:"),
        translations.get("grip", "TUTAMAK:"),
        translations.get("stock", "DİPÇİK:"),
        translations.get("position", "POZİSYON:")
    ]
    label_objects = []
    value_objects = []
    for i, text in enumerate(labels):
        label = tk.Label(root, text=text, font=("Arial", 8, "bold"), fg="white", bg="#162038", anchor="w")
        value = tk.Label(root, text=f"[{none_text}]", font=("Arial", 8, "bold"), fg="red", bg="#162038", anchor="w")
        value_shadow1 = tk.Label(root, text=f"[{none_text}]", font=("Arial", 8, "bold"), fg="red", bg="#162038", anchor="w")
        value_shadow2 = tk.Label(root, text=f"[{none_text}]", font=("Arial", 8, "bold"), fg="red", bg="#162038", anchor="w")
        label.place(x=0, y=i*20, width=90, height=16)
        value.place(x=90, y=i*20, width=125, height=16)
        value_shadow1.place(x=92, y=2 + i*20, width=125, height=16)
        value_shadow2.place(x=93, y=3 + i*20, width=125, height=16)
        label_objects.append(label)
        value_objects.append((value, value_shadow1, value_shadow2))
    root.bind("<Button-1>", start_drag)
    root.bind("<B1-Motion>", on_main_drag)
    def on_closing():
        saved_pos = load_window_positions()
        save_window_positions(
            (root.winfo_x(), root.winfo_y()),
            saved_pos.get('slider_window'),
            saved_pos.get('selected_language', 'tr')
        )
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    window_objects = (
        label_objects[0], value_objects[0][0], value_objects[0][1], value_objects[0][2],
        label_objects[1], value_objects[1][0], value_objects[1][1], value_objects[1][2],
        label_objects[2], value_objects[2][0], value_objects[2][1], value_objects[2][2],
        label_objects[3], value_objects[3][0], value_objects[3][1], value_objects[3][2],
        label_objects[4], value_objects[4][0], value_objects[4][1], value_objects[4][2],
        label_objects[5], value_objects[5][0], value_objects[5][1], value_objects[5][2]
    )
    update_ui_language(root, translations, *window_objects)
    return window_objects, root, outline_window

def call_macro(weapon, attachments, slot_data, position, mk14_auto_mode):
    global grenade_active, rapid_fire_cps, move_sensitivity, move_speed
    logging.debug(f"call_macro başlangıç - Slot {slot_data['slot']}: Weapon={weapon}, Attachments={attachments}")
    if weapon == "YOK":
        slot_data["active"] = False
        slot_data["rapid_fire_enabled"] = False
        logging.debug(f"Silah YOK, makro çalışmadı: {weapon}")
        return False, None, False, None

    is_dmr_weapon = is_dmr(weapon)
    rapid_fire_enabled = is_dmr_weapon and not grenade_active
    slot_data["rapid_fire_enabled"] = rapid_fire_enabled
    slot_data["active"] = not grenade_active

    attachments = attachments if attachments is not None else {}
    weapon_name = weapon.replace(" ", "_")
    durbun = (attachments.get("durbun", "YOK") or "YOK").replace(" ", "_")
    if durbun.startswith("1x") or durbun == "YOK":
        durbun = "1x_RedDot"
    namlu = (attachments.get("namlu", "YOK") or "YOK").replace(" ", "_")
    if weapon in dmr_weapons and namlu.startswith("SR_Supressor"):
        namlu = namlu.replace("SR_", "AR_")
    tutamak = (attachments.get("tutamak", "YOK") or "YOK").replace(" ", "_")
    dipcik = (attachments.get("dipcik", "YOK") or "YOK").replace(" ", "_")
    position = position.replace(" ", "_")
    macro_name = f"{weapon_name}_{durbun}_{namlu}_{tutamak}_{dipcik}_{position}"
    if weapon == "Mk14" and mk14_auto_mode:
        macro_name += "_AUTO"
    slot_data["macro_name"] = macro_name

    if is_cps_locked and weapon in ["M16A4", "Mk47 Mutant", "P1911", "P92", "R1895", "R45", "Deagle"]:
        preset_file = os.path.join(macro_folder, f"{macro_name}_AUTO.json")
    else:
        preset_file = os.path.join(macro_folder, f"{macro_name}_{current_preset_index + 1}.json" if is_cps_locked and is_dmr_weapon else f"{macro_name}.json")

    macro_exists = os.path.exists(preset_file)
    if macro_exists:
        try:
            with open(preset_file, 'r', encoding='utf-8') as f:
                macro_data = json.load(f)
            move_sensitivity = macro_data.get("sensitivity", move_sensitivity)
            move_speed = macro_data.get("move_speed", move_speed)
            if is_dmr_weapon and "rapid_fire_speed" in macro_data:
                rapid_fire_cps = macro_data["rapid_fire_speed"]
                update_cps_file()
            macro_cache.clear()
            macro_cache[macro_name] = macro_data
            logging.info(f"Makro yüklendi: {preset_file}, CPS={rapid_fire_cps if is_dmr_weapon else 'None'}, Sensitivity={move_sensitivity}, Move Speed={move_speed}")
        except Exception as e:
            logging.error(f"Makro çalıştırma hatası: {e}")
            slot_data["active"] = False
            return False, move_sensitivity, rapid_fire_enabled, None
    else:
        logging.warning(f"Makro bulunamadı: {preset_file}, varsayılan ayarlar kullanıldı")
        macro_cache.pop(macro_name, None)
        move_sensitivity = 1.0
        move_speed = 0.05
        if is_dmr_weapon and not is_cps_locked:
            rapid_fire_cps = rapid_fire_cps
            update_cps_file()
        if is_cps_locked and is_dmr_weapon and weapon not in ["M16A4", "Mk47 Mutant", "P1911", "P92", "R1895", "R45", "Deagle"]:
            slot_data["macro_name"] = "YOK"
        logging.debug(f"Varsayılan ayarlar uygulandı: Sensitivity={move_sensitivity}, Move Speed={move_speed}, CPS={rapid_fire_cps if is_dmr_weapon else 'None'}")

    logging.debug(f"call_macro çıkış - Slot {slot_data['slot']}: Weapon={slot_data['name']}, Attachments={slot_data['attachments']}")
    return True, move_sensitivity, rapid_fire_enabled, macro_exists

# Envanter güncelleme
def update_inventory(root, outline_window, 
                    weapon_label, weapon_value, weapon_value_shadow1, weapon_value_shadow2,
                    sight_label, sight_value, sight_value_shadow1, sight_value_shadow2,
                    muzzle_label, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2,
                    grip_label, grip_value, grip_value_shadow1, grip_value_shadow2,
                    stock_label, stock_value, stock_value_shadow1, stock_value_shadow2,
                    position_label, position_value, position_value_shadow1, position_value_shadow2,
                    weapon_templates, attachment_templates, weapon1_data, weapon2_data, pistol_data, 
                    current_weapon_ref, current_position_ref, mk14_auto_mode_ref):
    # Değişkenleri açıkça tanımla
    global tab_press_detected, overlay_hidden, last_b_press_time, last_click_time
    tab_press_detected = False
    overlay_hidden = False
    last_b_press_time = 0
    last_click_time = 0
    debounce_delay = 200
    previous_weapon1_data = {"name": "YOK", "attachments": {}}
    previous_weapon2_data = {"name": "YOK", "attachments": {}}
    previous_pistol_data = {"name": "YOK", "attachments": {}}
    attachment_base_names = {k: v[1] for k, v in attachment_templates.items()}
    attachment_templates = {k: v[0] for k, v in attachment_templates.items()}
    window_objects = (
        weapon_label, weapon_value, weapon_value_shadow1, weapon_value_shadow2,
        sight_label, sight_value, sight_value_shadow1, sight_value_shadow2,
        muzzle_label, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2,
        grip_label, grip_value, grip_value_shadow1, grip_value_shadow2,
        stock_label, stock_value, stock_value_shadow1, stock_value_shadow2,
        position_label, position_value, position_value_shadow1, position_value_shadow2
    )
    toggle_slider_window = create_slider_window(root, outline_window, window_objects)

    def toggle_inventory():
        global tab_inventory_active, inventory_scan_thread
        tab_inventory_active = not tab_inventory_active
        if tab_inventory_active:
            if inventory_scan_thread is None or not inventory_scan_thread.is_alive():
                args = (
                    root, weapon_templates, attachment_templates, attachment_base_names,
                    weapon1_data, weapon2_data, pistol_data, current_weapon_ref,
                    current_position_ref, mk14_auto_mode_ref, previous_weapon1_data,
                    previous_weapon2_data, previous_pistol_data
                )
                inventory_scan_thread = threading.Thread(target=start_inventory_scan, args=(args,), daemon=True)
                inventory_scan_thread.start()
                logging.debug("Envanter tarama aktif hale getirildi.")
        else:
            logging.debug("Envanter tarama durduruldu.")
            if inventory_scan_thread is not None and inventory_scan_thread.is_alive():
                logging.debug("Envanter tarama thread'i hala canlı, sonlandırılıyor...")

    def on_press(key):
        global current_preset_index, grenade_active, locked_cps, is_cps_locked, rapid_fire_cps, click_thread, move_thread, is_running, move_sensitivity, move_speed, last_active_slot, w_pressed, shift_pressed, space_pressed, space_thread, tab_press_detected, overlay_hidden, last_b_press_time, last_click_time
        try:
            if key == pynput_keyboard.Key.tab:
                if not tab_press_detected:
                    tab_press_detected = True
                    alt_pressed = win32api.GetKeyState(win32con.VK_MENU) & 0x8000
                    if not alt_pressed and is_game_active():
                        toggle_inventory()
                        if tab_inventory_active:
                            grenade_active = True
                            last_active_slot = current_weapon_ref[0]
                            logging.debug(f"TAB toggle: Envanter tarama başlatıldı, son aktif slot: {last_active_slot}")
                        else:
                            grenade_active = False
                            # Önceki slot verilerini koru ve doğru slotu geri yükle
                            if last_active_slot == 1:
                                current_weapon_ref[0] = 1
                                if weapon1_data["name"] != "YOK":
                                    call_macro(weapon1_data['name'], weapon1_data['attachments'], weapon1_data, current_position_ref[0], mk14_auto_mode_ref[0])
                                    logging.debug(f"Slot 1 geri yüklendi: {weapon1_data}")
                                else:
                                    logging.debug("Slot 1 YOK, makro çağrılmadı")
                            elif last_active_slot == 2:
                                current_weapon_ref[0] = 2
                                if weapon2_data["name"] != "YOK":
                                    call_macro(weapon2_data['name'], weapon2_data['attachments'], weapon2_data, current_position_ref[0], mk14_auto_mode_ref[0])
                                    logging.debug(f"Slot 2 geri yüklendi: {weapon2_data}")
                                else:
                                    logging.debug("Slot 2 YOK, makro çağrılmadı")
                            elif last_active_slot == 3:
                                current_weapon_ref[0] = 3
                                if pistol_data["name"] != "YOK":
                                    call_macro(pistol_data['name'], pistol_data['attachments'], pistol_data, current_position_ref[0], mk14_auto_mode_ref[0])
                                    logging.debug(f"Tabanca slotu geri yüklendi: {pistol_data}")
                                else:
                                    logging.debug("Tabanca slotu YOK, makro çağrılmadı")
                            # Arayüzü güncelle, mevcut verileri kullan
                            root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
                            logging.debug(f"TAB toggle: Envanter tarama durduruldu, aktif slot: {current_weapon_ref[0]}, weapon1: {weapon1_data}, weapon2: {weapon2_data}, pistol: {pistol_data}")
                    elif alt_pressed:
                        logging.debug("ALT+TAB algılandı, tarama tetiklenmedi")
            elif key == pynput_keyboard.Key.shift:
                shift_pressed = True
                if w_pressed and shift_pressed:
                    show_crosshair()
            elif key == pynput_keyboard.KeyCode.from_char('w'):
                w_pressed = True
                if w_pressed and shift_pressed:
                    show_crosshair()
            elif key == pynput_keyboard.Key.space:
                if not space_pressed:
                    space_pressed = True
                    space_thread = threading.Thread(target=send_space, daemon=True)
                    space_thread.start()
            elif key == pynput_keyboard.KeyCode.from_char('m'):
                if grenade_active:
                    grenade_active = False
                    if last_active_slot == 1:
                        current_weapon_ref[0] = 1
                        call_macro(weapon1_data['name'], weapon1_data['attachments'], weapon1_data, current_position_ref[0], mk14_auto_mode_ref[0])
                    elif last_active_slot == 2:
                        current_weapon_ref[0] = 2
                        call_macro(weapon2_data['name'], weapon2_data['attachments'], weapon2_data, current_position_ref[0], mk14_auto_mode_ref[0])
                    elif last_active_slot == 3:
                        current_weapon_ref[0] = 3
                        call_macro(pistol_data['name'], pistol_data['attachments'], pistol_data, current_position_ref[0], mk14_auto_mode_ref[0])
                    root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
                    logging.debug(f"M basıldı, makrolar yeniden başlatıldı, slot: {last_active_slot}")
                else:
                    last_active_slot = current_weapon_ref[0]
                    grenade_active = True
                    logging.debug(f"M basıldı, makrolar durduruldu, son aktif slot: {last_active_slot}")
            elif key == pynput_keyboard.KeyCode.from_char('5'):
                grenade_active = True
                current_weapon_ref[0] = 0
                logging.debug("5 basıldı, makrolar durduruldu")
            elif key == pynput_keyboard.KeyCode.from_char('1'):
                grenade_active = False
                current_weapon_ref[0] = 1
                last_active_slot = 1
                _, _, _, macro_exists = call_macro(weapon1_data['name'], weapon1_data['attachments'], weapon1_data, current_position_ref[0], mk14_auto_mode_ref[0])
                root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
                if is_cps_locked and weapon1_data["name"] in dmr_weapons:
                    if weapon1_data["name"] in ["M16A4", "Mk47 Mutant", "P1911", "P92", "R1895", "R45", "Deagle"] and macro_exists:
                        show_notification(f"{translations.get('rapid_fire_speed', 'Rapid Fire Hızı:')} AUTO")
                    elif macro_exists:
                        show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - CPS: {rapid_fire_cps}")
                    else:
                        show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - [{translations.get('none', 'YOK')}]")
            elif key == pynput_keyboard.KeyCode.from_char('2'):
                grenade_active = False
                current_weapon_ref[0] = 2
                last_active_slot = 2
                _, _, _, macro_exists = call_macro(weapon2_data['name'], weapon2_data['attachments'], weapon2_data, current_position_ref[0], mk14_auto_mode_ref[0])
                root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
                if is_cps_locked and weapon2_data["name"] in dmr_weapons:
                    if weapon2_data["name"] in ["M16A4", "Mk47 Mutant", "P1911", "P92", "R1895", "R45", "Deagle"] and macro_exists:
                        show_notification(f"{translations.get('rapid_fire_speed', 'Rapid Fire Hızı:')} AUTO")
                    elif macro_exists:
                        show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - CPS: {rapid_fire_cps}")
                    else:
                        show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - [{translations.get('none', 'YOK')}]")
            elif key == pynput_keyboard.KeyCode.from_char('3'):
                grenade_active = False
                current_weapon_ref[0] = 3
                last_active_slot = 3
                _, _, _, macro_exists = call_macro(pistol_data['name'], pistol_data['attachments'], pistol_data, current_position_ref[0], mk14_auto_mode_ref[0])
                root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
                if is_cps_locked and pistol_data["name"] in dmr_weapons:
                    if pistol_data["name"] in ["P1911", "P92", "R1895", "R45", "Deagle"] and macro_exists:
                        show_notification(f"{translations.get('rapid_fire_speed', 'Rapid Fire Hızı:')} AUTO")
                    elif macro_exists:
                        show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - CPS: {rapid_fire_cps}")
                    else:
                        show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - [{translations.get('none', 'YOK')}]")
            elif key == pynput_keyboard.KeyCode.from_char('b'):
                current_time = time.time() * 1000
                if current_time - last_b_press_time < debounce_delay:
                    return
                last_b_press_time = current_time
                if weapon1_data["name"] == "Mk14" or weapon2_data["name"] == "Mk14" or pistol_data["name"] == "Mk14":
                    mk14_auto_mode_ref[0] = not mk14_auto_mode_ref[0]
                    current_slot_data = (
                        weapon1_data if current_weapon_ref[0] == 1 else
                        weapon2_data if current_weapon_ref[0] == 2 else
                        pistol_data
                    )
                    call_macro(current_slot_data['name'], current_slot_data['attachments'], current_slot_data, current_position_ref[0], mk14_auto_mode_ref[0])
                    root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
            elif key == pynput_keyboard.KeyCode.from_char('c'):
                current_position_ref[0] = "Crouching" if current_position_ref[0] in ["Standing", "Prone"] else "Standing"
                call_macro(weapon1_data['name'], weapon1_data['attachments'], weapon1_data, current_position_ref[0], mk14_auto_mode_ref[0])
                call_macro(weapon2_data['name'], weapon2_data['attachments'], weapon2_data, current_position_ref[0], mk14_auto_mode_ref[0])
                call_macro(pistol_data['name'], pistol_data['attachments'], pistol_data, current_position_ref[0], mk14_auto_mode_ref[0])
                root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
            elif key == pynput_keyboard.KeyCode.from_char('z'):
                current_position_ref[0] = "Prone" if current_position_ref[0] in ["Standing", "Crouching"] else "Standing"
                call_macro(weapon1_data['name'], weapon1_data['attachments'], weapon1_data, current_position_ref[0], mk14_auto_mode_ref[0])
                call_macro(weapon2_data['name'], weapon2_data['attachments'], weapon2_data, current_position_ref[0], mk14_auto_mode_ref[0])
                call_macro(pistol_data['name'], pistol_data['attachments'], pistol_data, current_position_ref[0], mk14_auto_mode_ref[0])
                root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
            elif key == pynput_keyboard.Key.space:
                if current_position_ref[0] in ["Crouching", "Prone"]:
                    current_position_ref[0] = "Standing"
                    call_macro(weapon1_data['name'], weapon1_data['attachments'], weapon1_data, current_position_ref[0], mk14_auto_mode_ref[0])
                    call_macro(weapon2_data['name'], weapon2_data['attachments'], weapon2_data, current_position_ref[0], mk14_auto_mode_ref[0])
                    call_macro(pistol_data['name'], pistol_data['attachments'], pistol_data, current_position_ref[0], mk14_auto_mode_ref[0])
                    root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
            elif key == pynput_keyboard.Key.delete:
                logging.debug("Delete tuşuna basıldı, toggle_slider_window çağrılıyor")
                toggle_slider_window()
            elif key == pynput_keyboard.Key.insert:
                global overlay_hidden
                overlay_hidden = not overlay_hidden
                if overlay_hidden:
                    root.withdraw()
                    outline_window.withdraw()
                    if global_slider_window:
                        global_slider_window.withdraw()
                        global_slider_outline.withdraw()
                else:
                    root.deiconify()
                    outline_window.deiconify()
                    if global_slider_window:
                        global_slider_window.deiconify()
                        global_slider_outline.deiconify()
            elif key == pynput_keyboard.Key.up:
                current_slot_data = (
                    weapon1_data if current_weapon_ref[0] == 1 else
                    weapon2_data if current_weapon_ref[0] == 2 else
                    pistol_data
                )
                if current_slot_data["name"] in dmr_weapons:
                    if not is_cps_locked:
                        if rapid_fire_cps < 20:
                            rapid_fire_cps = min(20, rapid_fire_cps + 1.0)
                            update_cps_file()
                            show_notification(f"{translations.get('rapid_fire_cps', 'Rapid Fire CPS:')} {rapid_fire_cps}")
                    else:
                        macro_name = current_slot_data.get("macro_name")
                        if macro_name:
                            if current_slot_data["name"] in ["M16A4", "Mk47 Mutant", "P1911", "P92", "R1895", "R45", "Deagle"]:
                                preset_file = os.path.join(macro_folder, f"{macro_name}_AUTO.json")
                                if os.path.exists(preset_file):
                                    with open(preset_file, "r", encoding="utf-8") as f:
                                        macro_data = json.load(f)
                                    rapid_fire_cps = macro_data.get("rapid_fire_speed", rapid_fire_cps)
                                    move_sensitivity = macro_data.get("sensitivity", move_sensitivity)
                                    move_speed = macro_data.get("move_speed", move_speed)
                                    update_cps_file()
                                    show_notification(f"{translations.get('rapid_fire_speed', 'Rapid Fire Hızı:')} AUTO")
                            else:
                                current_preset_index = (current_preset_index + 1) % 3
                                preset_file = os.path.join(macro_folder, f"{macro_name}_{current_preset_index + 1}.json")
                                if os.path.exists(preset_file):
                                    with open(preset_file, "r", encoding="utf-8") as f:
                                        macro_data = json.load(f)
                                    rapid_fire_cps = macro_data.get("rapid_fire_speed", rapid_fire_cps)
                                    move_sensitivity = macro_data.get("sensitivity", move_sensitivity)
                                    move_speed = macro_data.get("move_speed", move_speed)
                                    update_cps_file()
                                    show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - CPS: {rapid_fire_cps}")
                                else:
                                    current_slot_data["macro_name"] = "YOK"
                                    show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - [{translations.get('none', 'YOK')}]")
                            root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
            elif key == pynput_keyboard.Key.down:
                current_slot_data = (
                    weapon1_data if current_weapon_ref[0] == 1 else
                    weapon2_data if current_weapon_ref[0] == 2 else
                    pistol_data
                )
                if current_slot_data["name"] in dmr_weapons:
                    if not is_cps_locked:
                        if rapid_fire_cps > 2:
                            rapid_fire_cps = max(2, rapid_fire_cps - 1.0)
                            update_cps_file()
                            show_notification(f"{translations.get('rapid_fire_cps', 'Rapid Fire CPS:')} {rapid_fire_cps}")
                    else:
                        macro_name = current_slot_data.get("macro_name")
                        if macro_name:
                            if current_slot_data["name"] in ["M16A4", "Mk47 Mutant", "P1911", "P92", "R1895", "R45", "Deagle"]:
                                preset_file = os.path.join(macro_folder, f"{macro_name}_AUTO.json")
                                if os.path.exists(preset_file):
                                    with open(preset_file, "r", encoding="utf-8") as f:
                                        macro_data = json.load(f)
                                    rapid_fire_cps = macro_data.get("rapid_fire_speed", rapid_fire_cps)
                                    move_sensitivity = macro_data.get("sensitivity", move_sensitivity)
                                    move_speed = macro_data.get("move_speed", move_speed)
                                    update_cps_file()
                                    show_notification(f"{translations.get('rapid_fire_speed', 'Rapid Fire Hızı:')} AUTO")
                            else:
                                current_preset_index = (current_preset_index - 1 + 3) % 3
                                preset_file = os.path.join(macro_folder, f"{macro_name}_{current_preset_index + 1}.json")
                                if os.path.exists(preset_file):
                                    with open(preset_file, "r", encoding="utf-8") as f:
                                        macro_data = json.load(f)
                                    rapid_fire_cps = macro_data.get("rapid_fire_speed", rapid_fire_cps)
                                    move_sensitivity = macro_data.get("sensitivity", move_sensitivity)
                                    move_speed = macro_data.get("move_speed", move_speed)
                                    update_cps_file()
                                    show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - CPS: {rapid_fire_cps}")
                                else:
                                    current_slot_data["macro_name"] = "YOK"
                                    show_notification(f"{translations.get('preset', 'Preset')} {current_preset_index + 1} - [{translations.get('none', 'YOK')}]")
                            root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))
        except AttributeError:
            pass

    def on_release(key):
        global w_pressed, shift_pressed, space_pressed, tab_press_detected
        try:
            if key == pynput_keyboard.Key.tab:
                tab_press_detected = False
                logging.debug("TAB bırakıldı")
            elif key == pynput_keyboard.Key.shift:
                shift_pressed = False
                hide_crosshair()
            elif key == pynput_keyboard.KeyCode.from_char('w'):
                w_pressed = False
                hide_crosshair()
            elif key == pynput_keyboard.Key.space:
                space_pressed = False
        except AttributeError:
            pass

    def on_click(x, y, button, pressed):
        global is_running, click_thread, move_thread, is_macro_clicking, right_click_pressed, left_click_pressed, last_click_time
        current_time = time.time()
        if button == Button.right:
            right_click_pressed = pressed
            current_slot_data = (
                weapon1_data if current_weapon_ref[0] == 1 else
                weapon2_data if current_weapon_ref[0] == 2 else
                pistol_data
            )
            if pressed and current_slot_data["attachments"].get("durbun") == "YOK":
                show_reddot()
            elif not pressed:
                hide_reddot()
        elif button == Button.left:
            left_click_pressed = pressed
            if not grenade_active and not is_macro_clicking:
                current_slot_data = (
                    weapon1_data if current_weapon_ref[0] == 1 else
                    weapon2_data if current_weapon_ref[0] == 2 else
                    pistol_data
                )
                if current_slot_data["name"] != "YOK" and (current_time - last_click_time > 0.5):
                    last_click_time = current_time
                    call_macro(current_slot_data['name'], current_slot_data['attachments'], current_slot_data, current_position_ref[0], mk14_auto_mode_ref[0])
                if pressed:
                    is_running = True
                    if click_thread is None or not click_thread.is_alive():
                        click_thread = threading.Thread(target=run_clicks, args=(current_slot_data,), daemon=True)
                        click_thread.start()
                    if move_thread is None or not move_thread.is_alive():
                        move_thread = threading.Thread(target=run_move, args=(current_slot_data,), daemon=True)
                        move_thread.start()
                else:
                    is_running = False
                    logging.debug(f"Slot {current_slot_data['slot']}: Tıklama durduruldu")
        
        # Shift kontrolü
        if right_click_pressed and left_click_pressed:
            win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        else:
            win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

    # Klavye ve fare dinleyicilerini başlat
    keyboard_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()
    mouse_listener = pynput_mouse.Listener(on_click=on_click)
    mouse_listener.start()

    # Program başlatıldığında arayüzü güncelle
    root.after(0, lambda: update_display(current_weapon_ref[0], weapon1_data, weapon2_data, pistol_data, current_weapon_ref, current_position_ref, mk14_auto_mode_ref, weapon_value, weapon_value_shadow1, weapon_value_shadow2, sight_value, sight_value_shadow1, sight_value_shadow2, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2, grip_value, grip_value_shadow1, grip_value_shadow2, stock_value, stock_value_shadow1, stock_value_shadow2, position_value, position_value_shadow1, position_value_shadow2))

# Ana program akışı
if __name__ == "__main__":
    # Verileri başlat
    weapon1_data = {
        "name": "YOK",
        "slot": 1,
        "active": False,
        "rapid_fire_enabled": False,
        "attachments": {
            "durbun": "YOK",
            "namlu": "YOK",
            "tutamak": "YOK",
            "dipcik": "YOK"
        }
    }
    weapon2_data = {
        "name": "YOK",
        "slot": 2,
        "active": False,
        "rapid_fire_enabled": False,
        "attachments": {
            "durbun": "YOK",
            "namlu": "YOK",
            "tutamak": "YOK",
            "dipcik": "YOK"
        }
    }
    pistol_data = {
        "name": "YOK",
        "slot": 3,
        "active": False,
        "rapid_fire_enabled": False,
        "attachments": {
            "durbun": "YOK",
            "namlu": "YOK",
            "tutamak": "YOK",
            "dipcik": "YOK"
        }
    }
    current_weapon_ref = [1]  # Aktif slot (1: weapon1, 2: weapon2, 3: pistol)
    current_position_ref = ["Standing"]  # Pozisyon: Standing, Crouching, Prone
    mk14_auto_mode_ref = [False]  # Mk14 AUTO modu

    # Şablonları yükle
    weapon_templates = load_templates(weapon_names_path, use_canny=True)
    attachment_templates = {
        key: load_templates(path, use_canny=key in ["durbun", "dipcik"], attachment_type=key)
        for key, path in attachments_paths.items()
    }

    # Pencereyi oluştur
    window_objects, root, outline_window = create_window()

    # window_objects'ı aç
    (weapon_label, weapon_value, weapon_value_shadow1, weapon_value_shadow2,
     sight_label, sight_value, sight_value_shadow1, sight_value_shadow2,
     muzzle_label, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2,
     grip_label, grip_value, grip_value_shadow1, grip_value_shadow2,
     stock_label, stock_value, stock_value_shadow1, stock_value_shadow2,
     position_label, position_value, position_value_shadow1, position_value_shadow2) = window_objects

    # Envanter güncelleme işlemini başlat
    update_inventory(
        root, outline_window,
        weapon_label, weapon_value, weapon_value_shadow1, weapon_value_shadow2,
        sight_label, sight_value, sight_value_shadow1, sight_value_shadow2,
        muzzle_label, muzzle_value, muzzle_value_shadow1, muzzle_value_shadow2,
        grip_label, grip_value, grip_value_shadow1, grip_value_shadow2,
        stock_label, stock_value, stock_value_shadow1, stock_value_shadow2,
        position_label, position_value, position_value_shadow1, position_value_shadow2,
        weapon_templates, attachment_templates, weapon1_data, weapon2_data, pistol_data,
        current_weapon_ref, current_position_ref, mk14_auto_mode_ref
    )

    # Ana döngüyü başlat
    root.mainloop()