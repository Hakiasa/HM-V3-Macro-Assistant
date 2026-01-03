import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
import mouse
import keyboard
import pydirectinput
import threading
import time
import json
import os

# --- AYARLAR ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# --- ÇEVİRİLER ---
DIL = "TR"
TRANSLATIONS = {
    "TR": {
        "title": "HM V3",
        "subtitle": "HM V3 Edition",
        "tab_macro": "Makro Kayıt",
        "tab_mouse": "Oto Mouse",
        "tab_keyb": "Oto Klavye (Full Q)",
        "btn_save": "KAYDET (.HMV2)",
        "btn_load": "YÜKLE (.HMV2)",
        "lbl_prof": "PROFİLLER", # EKLENDİ
        "status_ready": "HAZIR",
        "status_rec": "KAYITTA 🔴",
        "status_play": "OYNATILIYOR ▶️",
        "status_stop": "DURDURULDU ⏹️",
        "lbl_loop": "Döngü (0 = Sonsuz)",
        "btn_rec": "KAYIT (F8)",
        "btn_stop_rec": "BİTİR (F8)",
        "btn_play": "OYNAT (F9)",
        "btn_stop": "DURDUR (F10)",
        "btn_edit": "DÜZENLE ✏️",
        "cl_close": "KAPAT [X]",
        "theme_dark": "Mod: Karanlık",
        "theme_light": "Mod: Aydınlık",
        "unsaved": "Kaydedilmemiş",
        "fc_engine": "ANA MOTOR GÜCÜ",
        "fc_cps": "CPS (Hız)",
        "fc_trigger": "Tetikleyici Tuş",
        "fc_total": "TOPLAM TIK",
        "fk_engine": "KLAVYE MOTORU",
        "fk_spam": "Spamlanacak Tuş",
        "fk_trigger": "Başlat/Durdur Tuşu",
        # DURUM MESAJLARI (EKLENDİ)
        "st_off": "KAPALI",
        "st_on": "AÇIK",
        "st_idle": "BEKLİYOR",
        "st_motor_off": "MOTOR KAPALI",
        "st_running": "ÇALIŞIYOR (SPAM)",
        "st_waiting": "HAZIR"
    },
    "EN": {
        "title": "HM V3",
        "subtitle": "HM V3 Edition",
        "tab_macro": "Macro Rec",
        "tab_mouse": "Auto Mouse",
        "tab_keyb": "Auto Key (Full Q)",
        "btn_save": "SAVE (.HMV2)",
        "btn_load": "LOAD (.HMV2)",
        "lbl_prof": "PROFILES", # EKLENDİ
        "status_ready": "READY",
        "status_rec": "RECORDING 🔴",
        "status_play": "PLAYING ▶️",
        "status_stop": "STOPPED ⏹️",
        "lbl_loop": "Loop (0 = Infinite)",
        "btn_rec": "REC (F8)",
        "btn_stop_rec": "STOP (F8)",
        "btn_play": "PLAY (F9)",
        "btn_stop": "STOP (F10)",
        "btn_edit": "EDIT ✏️",
        "cl_close": "CLOSE [X]",
        "theme_dark": "Mode: Dark",
        "theme_light": "Mode: Light",
        "unsaved": "Unsaved",
        "fc_engine": "MAIN ENGINE POWER",
        "fc_cps": "CPS (Speed)",
        "fc_trigger": "Trigger Key",
        "fc_total": "TOTAL CLICKS",
        "fk_engine": "KEYBOARD ENGINE",
        "fk_spam": "Spam Key",
        "fk_trigger": "Start/Stop Key",
        # DURUM MESAJLARI (EKLENDİ)
        "st_off": "OFF",
        "st_on": "ON",
        "st_idle": "IDLE",
        "st_motor_off": "ENGINE OFF",
        "st_running": "RUNNING (SPAM)",
        "st_waiting": "READY"
    }
}

CHANGELOG_DATA = {
    "TR": """
V3.0
----------------------
• Arayüz değişti.
• Klavye Makrosu Eklendi.

V2.2
----------------------
• Görsel hatalar giderildi (Karanlık Mod).
• Yeni dil seçeneği eklendi.
• Oto Tıklayıcıya eklendi.
• Changelog kısmı eklendi.

V2.1
----------------------
• Makro düzenleme butonu eklendi.
• Makro kaydetme ve yükleme butonu eklendi.
• Karanlık tema eklendi.

V2.0
----------------------
• Uygulama yayınlandı.""",
    "EN": """

V3.0
----------------------
• The interface has changed.
• Keyboard Macro Added

V2.2
----------------------
• Visual bugs fixed (Dark Mode).
• New language option added.
• Auto Clicker added.
• Changelog section added.

V2.1
----------------------
• Macro edit button added.
• Macro save and load buttons added.
• Dark theme added.

V2.0
----------------------
• Application released."""
}

# --- GLOBAL DEĞİŞKENLER ---
PROFILES = {
    1: {"data": [], "name": "Kaydedilmemiş"},
    2: {"data": [], "name": "Kaydedilmemiş"},
    3: {"data": [], "name": "Kaydedilmemiş"}
}
aktif_profil = 1
tum_olaylar = PROFILES[1]["data"]

kaydediyor = False
oynatiyor = False

# Mouse & Keyboard Globals
fc_engine = False; fc_active = False; fc_cps = 10; fc_trigger_key = "f6"; fc_mouse_btn = "left"; fc_mode = "toggle"; fc_total_clicks = 0
fk_engine = False; fk_active = False; fk_cps = 10; fk_trigger_key = "f7"; fk_spam_key = "q"
tus_atama_modu = False; tus_atama_hedef = None
son_hareket_zamani = 0; baslangic_zamani = 0

# --- LOGIC ---

def smart_sleep(duration):
    global oynatiyor
    end_time = time.time() + duration
    while time.time() < end_time:
        if not oynatiyor: return False
        time.sleep(0.005)
    return True

def fast_clicker_loop():
    global fc_active, fc_total_clicks
    while True:
        try:
            if not fc_engine:
                if fc_active: fc_active = False
                time.sleep(0.1); continue
            if fc_active and not tus_atama_modu:
                mouse.click(button=fc_mouse_btn)
                fc_total_clicks += 1
                time.sleep(1.0 / max(1, fc_cps))
            else: time.sleep(0.01)
        except: time.sleep(0.1)

def fast_keyboard_loop():
    global fk_active
    while True:
        try:
            if not fk_engine:
                if fk_active: fk_active = False
                time.sleep(0.1); continue
            if fk_active and not tus_atama_modu:
                keyboard.press_and_release(fk_spam_key)
                time.sleep(1.0 / max(1, fk_cps))
            else: time.sleep(0.01)
        except: time.sleep(0.1)

threading.Thread(target=fast_clicker_loop, daemon=True).start()
threading.Thread(target=fast_keyboard_loop, daemon=True).start()

def global_key_handler(event):
    global fc_active, fk_active, fc_trigger_key, fk_trigger_key, fk_spam_key, tus_atama_modu, tus_atama_hedef
    if event.event_type == 'down':
        if tus_atama_modu:
            if event.name not in ['esc']:
                if tus_atama_hedef == 'mouse_trig': fc_trigger_key = event.name; app.upd_trig_ui()
                elif tus_atama_hedef == 'key_trig': fk_trigger_key = event.name; app.upd_kb_ui()
                elif tus_atama_hedef == 'key_spam': fk_spam_key = event.name; app.upd_kb_ui()
                tus_atama_modu = False; tus_atama_hedef = None
            return
        if fc_engine and event.name == fc_trigger_key:
            if fc_mode == "toggle": fc_active = not fc_active
            elif fc_mode == "hold": fc_active = True
            app.upd_fc_stat()
        if fk_engine and event.name == fk_trigger_key:
            fk_active = not fk_active; app.upd_fk_stat()
    elif event.event_type == 'up':
        if fc_engine and event.name == fc_trigger_key and fc_mode == "hold": 
            fc_active = False; app.upd_fc_stat()

keyboard.hook(global_key_handler)

def mouse_callback(event):
    global son_hareket_zamani
    if kaydediyor:
        su_an = time.time()
        if isinstance(event, mouse.MoveEvent):
            if su_an - son_hareket_zamani < 0.02: return
            tum_olaylar.append({'tip': 'mouse_move', 'x': event.x, 'y': event.y, 'zaman': su_an - baslangic_zamani, 'bekleme': 0})
            son_hareket_zamani = su_an
        elif isinstance(event, mouse.ButtonEvent):
            tip = 'down' if event.event_type == 'down' else 'up'
            tum_olaylar.append({'tip': 'mouse_click', 'tus': event.button, 'aksiyon': tip, 'zaman': su_an - baslangic_zamani, 'bekleme': 0})

def keyboard_record_callback(event):
    if kaydediyor and event.name not in ['f8', 'f9', 'f10']:
        tip = 'down' if event.event_type == 'down' else 'up'
        tum_olaylar.append({'tip': 'keyboard', 'tus': event.name, 'aksiyon': tip, 'zaman': time.time() - baslangic_zamani, 'bekleme': 0})

def oynat_thread():
    global oynatiyor
    if oynatiyor: return
    oynatiyor = True
    threading.Thread(target=oynat_islem, daemon=True).start()

def oynat_islem():
    global oynatiyor
    ozel = ['up', 'down', 'left', 'right', 'enter', 't', 'esc', 'space', 'shift', 'ctrl', 'backspace', 'tab']
    try: h = int(app.ent_loop.get())
    except: h = 0
    cur = 0
    while oynatiyor:
        if h > 0 and cur >= h: break
        app.lbl_macro_stat.configure(text=f"{TRANSLATIONS[DIL]['status_play']} ({cur+1})", text_color="#2ECC71")
        
        for o in tum_olaylar:
            if not oynatiyor: break
            if o.get('bekleme', 0) > 0.001:
                if not smart_sleep(o['bekleme']): break
            try:
                if o['tip'] == 'mouse_move': mouse.move(o['x'], o['y'], absolute=True, duration=0)
                elif o['tip'] == 'mouse_click': 
                    if o['aksiyon'] == 'down': mouse.press(o['tus'])
                    else: mouse.release(o['tus'])
                elif o['tip'] == 'keyboard':
                    tus = o['tus'].lower()
                    if tus in ozel:
                        if o['aksiyon'] == 'down': pydirectinput.keyDown(tus)
                        else: pydirectinput.keyUp(tus)
                    else:
                        if o['aksiyon'] == 'down': keyboard.press(tus)
                        else: keyboard.release(tus)
            except: pass 
        cur += 1
        if not smart_sleep(0.1): break
    
    app.stop_play() 

# --- GUI ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HM V3")
        try:
            self.iconbitmap("logo.ico")
        except:
            pass
        self.geometry("850x600")
        self.resizable(False, False)
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew"); self.sidebar.grid_rowconfigure(5, weight=1)

        self.logo = ctk.CTkLabel(self.sidebar, text="HM V3", font=ctk.CTkFont(size=30, weight="bold")); self.logo.grid(row=0, column=0, padx=20, pady=(20,5))
        self.sub = ctk.CTkLabel(self.sidebar, text="MVV Edition", font=ctk.CTkFont(size=12)); self.sub.grid(row=1, column=0, padx=20, pady=(0,20))

        self.lbl_prof = ctk.CTkLabel(self.sidebar, text="PROFİLLER", anchor="w"); self.lbl_prof.grid(row=2, column=0, padx=20)
        self.f_prof = ctk.CTkFrame(self.sidebar, fg_color="transparent"); self.f_prof.grid(row=3, column=0, padx=20, pady=5)
        self.btn_p1 = ctk.CTkButton(self.f_prof, text="P1", width=40, command=lambda: self.set_prof(1)); self.btn_p1.pack(side="left", padx=2)
        self.btn_p2 = ctk.CTkButton(self.f_prof, text="P2", width=40, command=lambda: self.set_prof(2)); self.btn_p2.pack(side="left", padx=2)
        self.btn_p3 = ctk.CTkButton(self.f_prof, text="P3", width=40, command=lambda: self.set_prof(3)); self.btn_p3.pack(side="left", padx=2)

        self.btn_save = ctk.CTkButton(self.sidebar, text="KAYDET", fg_color="#2980b9", command=self.save_file); self.btn_save.grid(row=4, column=0, padx=20, pady=(20, 10))
        self.btn_load = ctk.CTkButton(self.sidebar, text="YÜKLE", fg_color="#27ae60", command=self.load_file); self.btn_load.grid(row=5, column=0, padx=20, pady=10, sticky="n")

        self.f_bott = ctk.CTkFrame(self.sidebar, fg_color="transparent"); self.f_bott.grid(row=6, column=0, pady=20)
        self.btn_lang = ctk.CTkButton(self.f_bott, text="TR/EN", width=80, fg_color="transparent", border_width=1, command=self.toggle_lang); self.btn_lang.pack(pady=5)
        self.sw_theme = ctk.CTkSwitch(self.f_bott, text="Karanlık", command=self.toggle_theme); self.sw_theme.select(); self.sw_theme.pack(pady=5)
        self.btn_cl = ctk.CTkButton(self.f_bott, text="📜", width=40, command=self.toggle_cl); self.btn_cl.pack(pady=5)

        self.tabs = ctk.CTkTabview(self); self.tabs.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.tab_macro = self.tabs.add("Makro"); self.tab_mouse = self.tabs.add("Mouse"); self.tab_keyb = self.tabs.add("Klavye")

        self.init_macro_tab(); self.init_mouse_tab(); self.init_keyb_tab()
        self.cl_fr = ctk.CTkFrame(self, corner_radius=15, fg_color="#1a1a1a", border_width=2, border_color="grey")
        self.upd_text(); self.loop()

    def init_macro_tab(self):
        self.lbl_macro_stat = ctk.CTkLabel(self.tab_macro, text="HAZIR", font=ctk.CTkFont(size=24, weight="bold"), text_color="#BDC3C7"); self.lbl_macro_stat.pack(pady=30)
        self.lbl_file = ctk.CTkLabel(self.tab_macro, text="..."); self.lbl_file.pack()
        self.f_acts = ctk.CTkFrame(self.tab_macro, fg_color="transparent"); self.f_acts.pack(pady=20)
        self.btn_rec = ctk.CTkButton(self.f_acts, text="KAYIT", width=200, height=40, fg_color="#c0392b", hover_color="#e74c3c", command=self.toggle_rec); self.btn_rec.pack(pady=5)
        self.btn_play = ctk.CTkButton(self.f_acts, text="OYNAT", width=200, height=40, fg_color="#27ae60", hover_color="#2ecc71", command=oynat_thread); self.btn_play.pack(pady=5)
        self.btn_stop = ctk.CTkButton(self.f_acts, text="DURDUR", width=200, height=40, fg_color="grey", command=self.stop_play); self.btn_stop.pack(pady=5)
        self.btn_edit = ctk.CTkButton(self.f_acts, text="DÜZENLE", width=200, height=40, fg_color="#f39c12", hover_color="#d35400", command=self.open_editor); self.btn_edit.pack(pady=5)
        self.f_lp = ctk.CTkFrame(self.tab_macro); self.f_lp.pack(pady=10)
        self.lbl_loop = ctk.CTkLabel(self.f_lp, text="Loop:"); self.lbl_loop.pack(side="left", padx=10)
        self.ent_loop = ctk.CTkEntry(self.f_lp, width=50, justify="center"); self.ent_loop.insert(0, "0"); self.ent_loop.pack(side="left", padx=10)

    def init_mouse_tab(self):
        self.f_m_eng = ctk.CTkFrame(self.tab_mouse, border_width=2, border_color="#8e44ad"); self.f_m_eng.pack(pady=20, padx=20, fill="x")
        self.lbl_m_eng = ctk.CTkLabel(self.f_m_eng, text="MOTOR", font=ctk.CTkFont(size=16, weight="bold")); self.lbl_m_eng.pack(side="left", padx=20, pady=15)
        self.sw_m_eng = ctk.CTkSwitch(self.f_m_eng, text="", command=self.tog_eng, progress_color="#00E676"); self.sw_m_eng.pack(side="right", padx=20)
        self.f_m_set = ctk.CTkFrame(self.tab_mouse, fg_color="transparent"); self.f_m_set.pack(pady=10)
        self.lbl_cps = ctk.CTkLabel(self.f_m_set, text="CPS:"); self.lbl_cps.grid(row=0, column=0, pady=10, sticky="w")
        self.sl_cps = ctk.CTkSlider(self.f_m_set, from_=1, to=50, command=self.set_cps); self.sl_cps.set(10); self.sl_cps.grid(row=0, column=1, padx=10)
        self.lbl_cps_val = ctk.CTkLabel(self.f_m_set, text="10"); self.lbl_cps_val.grid(row=0, column=2)
        self.lbl_trig = ctk.CTkLabel(self.f_m_set, text="Tuş:"); self.lbl_trig.grid(row=1, column=0, pady=10, sticky="w")
        self.btn_trig = ctk.CTkButton(self.f_m_set, text="[F6]", width=80, command=lambda: self.bind_k('mouse_trig')); self.btn_trig.grid(row=1, column=1, padx=10)
        self.seg_btn = ctk.CTkSegmentedButton(self.tab_mouse, values=["Left", "Middle", "Right"], command=self.set_m_sets); self.seg_btn.set("Left"); self.seg_btn.pack(pady=5)
        self.seg_mode = ctk.CTkSegmentedButton(self.tab_mouse, values=["Toggle", "Hold"], command=self.set_m_sets); self.seg_mode.set("Toggle"); self.seg_mode.pack(pady=5)
        self.lbl_tot_txt = ctk.CTkLabel(self.tab_mouse, text="TOTAL"); self.lbl_tot_txt.pack(pady=(20,0))
        self.lbl_tot = ctk.CTkLabel(self.tab_mouse, text="0", font=ctk.CTkFont(size=30, weight="bold"), text_color="#3498DB"); self.lbl_tot.pack()
        self.lbl_fc_stat = ctk.CTkLabel(self.tab_mouse, text="...", text_color="grey"); self.lbl_fc_stat.pack()

    def init_keyb_tab(self):
        self.f_k_eng = ctk.CTkFrame(self.tab_keyb, border_width=2, border_color="#e67e22"); self.f_k_eng.pack(pady=20, padx=20, fill="x")
        self.lbl_k_eng = ctk.CTkLabel(self.f_k_eng, text="KLAVYE MOTORU", font=ctk.CTkFont(size=16, weight="bold")); self.lbl_k_eng.pack(side="left", padx=20, pady=15)
        self.sw_k_eng = ctk.CTkSwitch(self.f_k_eng, text="", command=self.tog_k_eng, progress_color="#e67e22"); self.sw_k_eng.pack(side="right", padx=20)
        self.f_k_set = ctk.CTkFrame(self.tab_keyb, fg_color="transparent"); self.f_k_set.pack(pady=10)
        self.lbl_kcps = ctk.CTkLabel(self.f_k_set, text="Hız:"); self.lbl_kcps.grid(row=0, column=0, pady=10, sticky="w")
        self.sl_kcps = ctk.CTkSlider(self.f_k_set, from_=1, to=50, command=self.set_kcps); self.sl_kcps.set(10); self.sl_kcps.grid(row=0, column=1, padx=10)
        self.lbl_kcps_val = ctk.CTkLabel(self.f_k_set, text="10"); self.lbl_kcps_val.grid(row=0, column=2)
        self.lbl_ktrig = ctk.CTkLabel(self.f_k_set, text="Tetikleyici:"); self.lbl_ktrig.grid(row=1, column=0, pady=10, sticky="w")
        self.btn_ktrig = ctk.CTkButton(self.f_k_set, text="[F7]", width=80, command=lambda: self.bind_k('key_trig')); self.btn_ktrig.grid(row=1, column=1, padx=10)
        self.lbl_kspam = ctk.CTkLabel(self.f_k_set, text="Basılacak Tuş:"); self.lbl_kspam.grid(row=2, column=0, pady=10, sticky="w")
        self.btn_kspam = ctk.CTkButton(self.f_k_set, text="[Q]", width=80, fg_color="#8e44ad", command=lambda: self.bind_k('key_spam')); self.btn_kspam.grid(row=2, column=1, padx=10)
        self.lbl_fk_stat = ctk.CTkLabel(self.tab_keyb, text="BEKLİYOR", font=ctk.CTkFont(size=20), text_color="grey"); self.lbl_fk_stat.pack(pady=30)
        self.lbl_k_info = ctk.CTkLabel(self.tab_keyb, text="", text_color="grey", font=("Arial", 10)); self.lbl_k_info.pack(side="bottom", pady=20)

    def toggle_cl(self):
        if self.cl_fr.winfo_ismapped(): self.cl_fr.place_forget()
        else:
            self.cl_fr.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8); self.cl_fr.lift()
            for w in self.cl_fr.winfo_children(): w.destroy()
            t = TRANSLATIONS[DIL]
            ctk.CTkButton(self.cl_fr, text=t["cl_close"], fg_color="#c0392b", command=self.toggle_cl).pack(anchor="ne", padx=10, pady=10)
            txt = ctk.CTkTextbox(self.cl_fr, font=("Consolas", 12)); txt.pack(fill="both", expand=True, padx=20, pady=(0,20))
            txt.insert("0.0", CHANGELOG_DATA[DIL]); txt.configure(state="disabled")

    # --- EDİTÖR ---
    def open_editor(self):
        if not tum_olaylar and not kaydediyor: pass 
        top = tk.Toplevel(self)
        top.title("Editör")
        top.geometry("750x550") # GENİŞLETİLDİ
        top.resizable(False, False) # KİLİTLENDİ
        
        bg_col = "#2b2b2b" if ctk.get_appearance_mode()=="Dark" else "#ecf0f1"
        fg_col = "white" if ctk.get_appearance_mode()=="Dark" else "black"
        top.configure(bg=bg_col)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=bg_col, foreground=fg_col, fieldbackground=bg_col, font=('Arial', 10), rowheight=25)
        style.map("Treeview", background=[('selected', '#3498db')])
        
        f_top = tk.Frame(top, bg=bg_col)
        f_top.pack(fill="x", padx=10, pady=5)
        var_show_move = tk.BooleanVar(value=False)

        cols = ('ID', 'Tip', 'Detay', 'Gecikme')
        tree = ttk.Treeview(top, columns=cols, show='headings')
        tree.heading('ID', text='#'); tree.column('ID', width=40, anchor="center")
        tree.heading('Tip', text='Tür'); tree.column('Tip', width=80, anchor="w")
        tree.heading('Detay', text='İşlem'); tree.column('Detay', width=300, anchor="w")
        tree.heading('Gecikme', text='Gecikme'); tree.column('Gecikme', width=80, anchor="e")
        
        vsb = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill='both', expand=True, padx=(10,0), pady=5)
        vsb.pack(side="left", fill="y", padx=(0,10), pady=5)

        def refresh():
            for item in tree.get_children(): tree.delete(item)
            for i, o in enumerate(tum_olaylar):
                if not var_show_move.get() and o['tip'] == 'mouse_move': continue
                
                tip_str = ""; det_str = ""
                if o['tip'] == 'mouse_click': 
                    tip_str = "Click"; det_str = f"Mouse {o['tus']} ({o['aksiyon']})"
                elif o['tip'] == 'keyboard': 
                    tip_str = "Key"; det_str = f"Tuş {o['tus']} ({o['aksiyon']})"
                elif o['tip'] == 'mouse_move': 
                    tip_str = "Move"; det_str = f"X:{o['x']} Y:{o['y']}"
                
                tree.insert("", "end", iid=str(i), values=(i+1, tip_str, det_str, f"{o['bekleme']:.4f}"))

        chk = tk.Checkbutton(f_top, text="Mouse Hareketlerini Göster", variable=var_show_move, command=refresh, bg=bg_col, fg=fg_col, selectcolor="grey")
        chk.pack(side="left")

        def delete_item():
            sel = tree.selection()
            if not sel: return
            idx = int(sel[0]); del tum_olaylar[idx]; refresh()
        
        def edit_time():
            sel = tree.selection()
            if not sel: return
            idx = int(sel[0]); old = tum_olaylar[idx]['bekleme']
            new_val = simpledialog.askfloat("Süre", "Yeni gecikme (sn):", initialvalue=old, parent=top)
            if new_val is not None: tum_olaylar[idx]['bekleme'] = new_val; refresh()

        f_bot = tk.Frame(top, bg=bg_col)
        f_bot.pack(fill="x", padx=10, pady=10)
        tk.Button(f_bot, text="SÜRE DÜZENLE", command=edit_time, bg="#3498db", fg="white", relief="flat", padx=10).pack(side="left")
        tk.Button(f_bot, text="SİL", command=delete_item, bg="#e74c3c", fg="white", relief="flat", padx=10).pack(side="right")
        refresh()

    def set_cps(self, v): global fc_cps; fc_cps = int(v); self.lbl_cps_val.configure(text=str(fc_cps))
    def set_kcps(self, v): global fk_cps; fk_cps = int(v); self.lbl_kcps_val.configure(text=str(fk_cps))
    
    def bind_k(self, target): 
        global tus_atama_modu, tus_atama_hedef; tus_atama_modu=True; tus_atama_hedef = target
        t = TRANSLATIONS[DIL]["fc_waiting"]
        if target == 'mouse_trig': self.btn_trig.configure(text=t, fg_color="orange")
        elif target == 'key_trig': self.btn_ktrig.configure(text=t, fg_color="orange")
        elif target == 'key_spam': self.btn_kspam.configure(text=t, fg_color="orange")

    def upd_trig_ui(self): self.btn_trig.configure(text=f"[{fc_trigger_key.upper()}]", fg_color=["#3B8ED0", "#1F6AA5"])
    def upd_kb_ui(self): self.btn_ktrig.configure(text=f"[{fk_trigger_key.upper()}]", fg_color=["#3B8ED0", "#1F6AA5"]); self.btn_kspam.configure(text=f"[{fk_spam_key.upper()}]", fg_color="#8e44ad")

    def tog_eng(self): global fc_engine, fc_active; fc_engine = self.sw_m_eng.get(); fc_active = False; self.upd_fc_stat()
    def tog_k_eng(self): global fk_engine, fk_active; fk_engine = self.sw_k_eng.get(); fk_active = False; self.upd_fk_stat()

    def upd_fc_stat(self):
        t = TRANSLATIONS[DIL]
        if not fc_engine: self.lbl_fc_stat.configure(text=t["st_off"], text_color="#e74c3c")
        elif fc_active: self.lbl_fc_stat.configure(text=t["st_on"], text_color="#2ecc71")
        else: self.lbl_fc_stat.configure(text=t["st_idle"], text_color="grey")

    def upd_fk_stat(self):
        t = TRANSLATIONS[DIL]
        if not fk_engine: self.lbl_fk_stat.configure(text=t["st_motor_off"], text_color="#e74c3c")
        elif fk_active: self.lbl_fk_stat.configure(text=t["st_running"], text_color="#2ecc71")
        else: self.lbl_fk_stat.configure(text=t["st_waiting"], text_color="grey")
    
    def set_m_sets(self, v):
        global fc_mouse_btn, fc_mode
        if v in ["Left", "Middle", "Right"]: fc_mouse_btn = v.lower()
        if v in ["Toggle", "Hold"]: fc_mode = v.lower()

    def loop(self):
        self.lbl_tot.configure(text=str(fc_total_clicks)); self.after(100, self.loop)

    def set_prof(self, p):
        global aktif_profil, tum_olaylar; aktif_profil = p; tum_olaylar = PROFILES[p]["data"]
        for i, b in enumerate([self.btn_p1, self.btn_p2, self.btn_p3]): b.configure(fg_color="#3498DB" if (i+1)==p else "transparent", border_width=2 if (i+1)!=p else 0)
        self.upd_file_lbl()

    def save_file(self):
        if not tum_olaylar: return
        p = filedialog.asksaveasfilename(defaultextension=".HMV2", filetypes=[("Hakiasa Macro V3", "*.HMV2")]); 
        if p:
            with open(p, 'w', encoding='utf-8') as f: json.dump(tum_olaylar, f, indent=4)
            PROFILES[aktif_profil]["name"] = os.path.basename(p); self.upd_file_lbl()

    def load_file(self):
        global tum_olaylar
        p = filedialog.askopenfilename(filetypes=[("Hakias Macro V2", "*.HMV2")])
        if p:
            with open(p, 'r', encoding='utf-8') as f: PROFILES[aktif_profil]["data"] = json.load(f); tum_olaylar = PROFILES[aktif_profil]["data"]
            PROFILES[aktif_profil]["name"] = os.path.basename(p); self.upd_file_lbl()

    def upd_file_lbl(self):
        n = PROFILES[aktif_profil]["name"]; t = TRANSLATIONS[DIL]["unsaved"] if n == "Kaydedilmemiş" else n; self.lbl_file.configure(text=t)

    def toggle_rec(self):
        global kaydediyor, baslangic_zamani, son_hareket_zamani, tum_olaylar
        if kaydediyor:
            kaydediyor = False; mouse.unhook(mouse_callback); keyboard.unhook(keyboard_record_callback)
            d = []; p = 0
            for o in tum_olaylar:
                diff = o['zaman'] - p; diff = 0 if diff < 0 else diff
                o['bekleme'] = 0 if o['tip'] == 'mouse_move' and diff < 0.005 else round(diff, 4)
                p = o['zaman']; d.append(o)
            tum_olaylar[:] = d; PROFILES[aktif_profil]["data"] = tum_olaylar; self.upd_text()
        else:
            PROFILES[aktif_profil]["data"] = []; tum_olaylar = PROFILES[aktif_profil]["data"]
            PROFILES[aktif_profil]["name"] = "Kaydedilmemiş"; self.upd_file_lbl()
            baslangic_zamani = time.time(); son_hareket_zamani = 0; kaydediyor = True
            mouse.hook(mouse_callback); keyboard.hook(keyboard_record_callback); self.upd_text()
    def stop_play(self):
        global oynatiyor; oynatiyor = False
        # --- DEĞİŞEN KISIM BAŞLANGIÇ ---
        for i in range(150): 
            try:
                keyboard.release(i)
            except:
                pass
        # --- DEĞİŞEN KISIM BİTİŞ ---
        try: mouse.release('left'); mouse.release('right')
        except: pass
        self.lbl_macro_stat.configure(text=TRANSLATIONS[DIL]['status_stop'], text_color="#E74C3C")

    def toggle_lang(self): global DIL; DIL = "EN" if DIL == "TR" else "TR"; self.upd_text()
    def toggle_theme(self): mode = "Light" if self.sw_theme.get() == 0 else "Dark"; ctk.set_appearance_mode(mode); self.upd_text()

    def upd_text(self):
        t = TRANSLATIONS[DIL]
        self.title(t["title"]); self.logo.configure(text=t["title"]); self.sub.configure(text=t["subtitle"])
        self.btn_save.configure(text=t["btn_save"]); self.btn_load.configure(text=t["btn_load"])
        self.lbl_loop.configure(text=t["lbl_loop"]); self.lbl_m_eng.configure(text=t["fc_engine"])
        self.lbl_cps.configure(text=t["fc_cps"]); self.lbl_trig.configure(text=t["fc_trigger"])
        self.lbl_tot_txt.configure(text=t["fc_total"]); self.btn_rec.configure(text=t["btn_rec"] if not kaydediyor else t["btn_stop_rec"])
        self.btn_play.configure(text=t["btn_play"]); self.btn_stop.configure(text=t["btn_stop"]); self.btn_edit.configure(text=t["btn_edit"])
        self.lbl_prof.configure(text=t["lbl_prof"]) # DİL GÜNCELLEMESİ
        try: self.lbl_k_eng.configure(text=t["fk_engine"]); self.lbl_kcps.configure(text=t["fc_cps"]); self.lbl_ktrig.configure(text=t["fk_trigger"]); self.lbl_kspam.configure(text=t["fk_spam"])
        except: pass
        self.sw_theme.configure(text=t["theme_dark"] if ctk.get_appearance_mode()=="Dark" else t["theme_light"]); self.upd_file_lbl(); self.upd_fc_stat(); self.upd_fk_stat()

app = App()
keyboard.add_hotkey('f8', lambda: app.toggle_rec())
keyboard.add_hotkey('f9', oynat_thread)
keyboard.add_hotkey('f10', app.stop_play)


app.mainloop()