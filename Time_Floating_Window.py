import tkinter as tk
import webbrowser
from tkinter import ttk, colorchooser, messagebox
from tkinter.font import families
import json
from datetime import datetime, timedelta
import os
import ctypes
import ntplib
import translation
import sys
import win32com.client
import winreg as reg

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    if not is_admin():
        exe = sys.executable
        if exe.endswith("python.exe") or exe.endswith("pythonw.exe"):
            # dev mode
            exe = exe.replace("python.exe", "pythonw.exe")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, ' '.join(sys.argv), None, 1)
        sys.exit()

class FloatingClockApp():
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(sys.executable), "TimeWindowSettings.json")
        first_run = self.load_settings()
        self.init_language()
        self.root = tk.Tk()
        self.root.withdraw()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.settings.setdefault("max_width", self.screen_width)
        self.settings.setdefault("max_height", self.screen_height)
        self.settings_window = None  # To track if settings window is open
        self.create_window(first_run)

    def first_run(self):
        # Ask the user if they want to create a desktop shortcut
        desktop = win32com.client.Dispatch("WScript.Shell").SpecialFolders("Desktop")
        if messagebox.askyesno(self.texts["confirm"], self.texts["create_desktop_shortcut_confirm"]):
            self.create_shortcut(desktop)
        start_menu = os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        print(start_menu)
        if messagebox.askyesno(self.texts["confirm"], self.texts["create_menu_shortcut_confirm"]):
            self.create_shortcut(start_menu)

    def create_shortcut(self, path=None):
        # Create a desktop shortcut for the application
        try:
            shortcut_path = os.path.join(path, self.texts["app_name"] + ".lnk")
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.WorkingDirectory = os.path.dirname(sys.executable)
            shortcut.IconLocation = sys.executable
            shortcut.save()
        except Exception as e:
            messagebox.showerror(self.texts["error"], str(e))

    def load_settings(self):
        # Load settings from file or use defaults, return whether it's the first run
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
            return False
        else:
            run_as_admin() # Run as admin at the first run to create shortcuts
            self.settings = {
                "bg_color": "#000000",
                "text_color": "#FFFFFF",
                "bg_opacity": 0.8,
                "width": 180,
                "height": 60,
                "font_family": "Consolas",
                "time_font_size": 17,
                "icon_size": 10,
                "is_movable": True,
                "last_position": None,
                "sync_interval": 100,
                "language": "default",
                "show_buttons_when_locked": True,
                "show_buttons_when_unlocked": True,
                "settings_window_size": None,
                "settings_window_position": None,
                "time_excursion": 0,
                "time_precision_digits": 0,
            }
            return True

    def save_settings(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    def init_language(self):
        if self.settings["language"] == "default":
            self.lang = translation.get_local_language()
        else:
            self.lang = self.settings["language"]
        self.translations = translation.all_translations
        self.available_languages = [val["lang_label"] for val in self.translations.values()] # get all language labels
        self.texts = self.translations.get(self.lang, self.translations["en"])

    def create_window(self, first_run):
        # Create the floating window
        self.floating_window = tk.Toplevel(self.root)
        self.floating_window.title("Floating Clock")
        self.floating_window.overrideredirect(True)
        self.update_geometry()
        if os.name == "nt":
            hwnd = ctypes.windll.user32.GetParent(self.floating_window.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x80000)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 2, ctypes.byref(ctypes.c_int(2)), 4)

        # If the window was moved before, apply the position
        if self.settings["last_position"]:
            self.apply_position_or_center()
        else:
            self.center_window()

        # Create the time label
        self.time_label = tk.Label(
            self.floating_window,
            text="",
            font=(self.settings["font_family"], self.settings["time_font_size"]),
            bg=self.settings["bg_color"],
            fg=self.settings["text_color"]
        )
        self.time_label.pack(fill="both", expand=True)

        self.is_movable = self.settings["is_movable"]

        # Create the lock/unlock button
        self.pin_button = tk.Button(
            self.floating_window,
            text=self.get_lock_icon(),
            command=self.toggle_lock,
            bg=self.settings["bg_color"],
            fg=self.settings["text_color"],
            relief="flat",
            font=(self.settings["font_family"], self.settings["icon_size"])
        )

        # Create the close button
        self.close_button = tk.Button(
            self.floating_window,
            text="X",
            command=self.quit_app,
            bg=self.settings["bg_color"],
            fg=self.settings["text_color"],
            relief="flat",
            font=(self.settings["font_family"], self.settings["icon_size"])
        )

        self.start_x = 0
        self.start_y = 0

        self.arrange_buttons()
        self.floating_window.bind("<Button-3>", self.show_context)
        self.floating_window.bind("<Button-1>", self.drag_start)
        self.floating_window.bind("<B1-Motion>", self.drag_move)

        self.update_time()
        if first_run:
            self.first_run()
        self.floating_window.attributes("-topmost", True)
        self.floating_window.bind("<FocusOut>", lambda e: self.keep_on_top())
        self.floating_window.attributes("-alpha", self.settings["bg_opacity"])

    def arrange_buttons(self):
        # Place the buttons according to the settings
        condition = (self.is_movable and self.settings["show_buttons_when_unlocked"]) or \
                    (not self.is_movable and self.settings["show_buttons_when_locked"])
        if condition:
            self.pin_button.place(relx=0.05, rely=0.05, anchor="nw")
            self.close_button.place(relx=0.95, rely=0.05, anchor="ne")
        else:
            self.pin_button.place_forget()
            self.close_button.place_forget()

    def keep_on_top(self):
        # Keep the time window on top
        self.floating_window.attributes("-topmost", True)
        self.floating_window.lift()

    def get_lock_icon(self):
        return "🔓" if self.is_movable else "🔒"

    def toggle_lock(self):
        # Toggle the movable state of the window
        self.is_movable = not self.is_movable
        self.settings["is_movable"] = self.is_movable
        self.pin_button.config(text=self.get_lock_icon())
        self.arrange_buttons()
        self.save_settings()

    def drag_start(self, e):
        if self.is_movable:
            self.start_x = e.x
            self.start_y = e.y

    def drag_move(self, e):
        # Move the window
        if self.is_movable:
            x = self.floating_window.winfo_x() + e.x - self.start_x
            y = self.floating_window.winfo_y() + e.y - self.start_y
            self.floating_window.geometry(f"+{x}+{y}")
            self.settings["last_position"] = [x, y]

    def show_context(self, e):
        # Right click context menu
        menu = tk.Menu(self.floating_window, tearoff=0)
        menu.add_command(label=self.texts["lock"] if self.is_movable else self.texts["unlock"], command=self.toggle_lock)
        menu.add_command(label=self.texts["settings"], command=self.open_settings)
        menu.add_command(label=self.texts["close"], command=self.quit_app)
        menu.post(e.x_root, e.y_root)

    def open_settings(self):
        # Open the settings window only if it's not already open
        if self.settings_window and tk.Toplevel.winfo_exists(self.settings_window):
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title(self.texts["settings"])
        size = self.settings.get("settings_window_size")
        pos = self.settings.get("settings_window_position")
        if size and pos:
            self.settings_window.geometry(f"{size[0]}x{size[1]}+{pos[0]}+{pos[1]}")
        else:
            size_hw = self.texts["settings_hw"]
            w, h = map(int, size_hw.split('x'))
            sw, sh = self.screen_width, self.screen_height
            x, y = (sw - w) // 2, (sh - h) // 2
            self.settings_window.geometry(f"{w}x{h}+{x}+{y}")

        def on_configure(event):
            # Save when the size or position of the window changes
            self.settings["settings_window_size"] = [self.settings_window.winfo_width(), self.settings_window.winfo_height()]
            self.settings["settings_window_position"] = [self.settings_window.winfo_x(), self.settings_window.winfo_y()]
            self.save_settings()

        def on_close():
            self.settings_window.destroy()
            self.settings_window = None

        self.settings_window.bind("<Configure>", on_configure)
        self.settings_window.protocol("WM_DELETE_WINDOW", on_close)

        cf = ttk.Frame(self.settings_window)
        cv = tk.Canvas(cf)
        sb = ttk.Scrollbar(cf, orient="vertical", command=cv.yview)
        frm = ttk.Frame(cv)
        frm.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=frm, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cf.pack(fill="both", expand=True)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Disable mouse wheel scrolling
        def disable_mousewheel(wid):
            wid.bind("<MouseWheel>", lambda e: "break")
        for widget in [cf, cv, sb, frm]:
            disable_mousewheel(widget)

        r = 0 # row number, used for grid layout
        ttk.Label(frm, text=self.texts["bg_color"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Button(frm, text=self.texts["choose_color"], command=self.pick_bg_color).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        ttk.Label(frm, text=self.texts["text_color"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Button(frm, text=self.texts["choose_color"], command=self.pick_text_color).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        # Background opacity settings
        ttk.Label(frm, text=self.texts["bg_opacity"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        alpha_frame = ttk.Frame(frm)
        alpha_frame.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        self.alpha_scale = ttk.Scale(
            alpha_frame,
            from_=0.05,
            to=1.0,
            value=self.settings["bg_opacity"],
            orient="horizontal",
            length=120,
            command=self.alpha_scale_changed
        )
        self.alpha_scale.pack(side="left")

        self.alpha_entry = ttk.Entry(alpha_frame, width=5)
        self.alpha_entry.insert(0, str(self.settings["bg_opacity"]))
        self.alpha_entry.pack(side="left", padx=5)
        self.alpha_entry.bind("<FocusOut>", lambda e: self.alpha_entry_apply())
        self.alpha_entry.bind("<Return>", lambda e: self.alpha_entry_apply())
        r += 1

        chk_u = tk.BooleanVar(value=self.settings["show_buttons_when_unlocked"])
        ttk.Label(frm, text=self.texts["show_buttons_when_unlocked"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Checkbutton(frm, variable=chk_u, command=lambda: self.show_button_unlocked(chk_u.get())).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        chkl = tk.BooleanVar(value=self.settings["show_buttons_when_locked"])
        ttk.Label(frm, text=self.texts["show_buttons_when_locked"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Checkbutton(frm, variable=chkl, command=lambda: self.show_button_locked(chkl.get())).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        autostart = tk.BooleanVar(value=self.check_autostart())
        ttk.Label(frm, text=self.texts["auto_start"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ttk.Checkbutton(frm, variable=autostart, command=lambda: self.set_autostart(autostart.get())).grid(row=r, column=1, padx=10, pady=5, sticky="w")
        r += 1

        ttk.Label(frm, text=self.texts["lang_switch"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        combo_lang = ttk.Combobox(frm, values=self.available_languages, state="readonly")
        combo_lang.set(self.translations[self.lang]["lang_label"])
        combo_lang.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        combo_lang.bind("<MouseWheel>", lambda e: "break") # disable mouse wheel scrolling
        combo_lang.bind("<<ComboboxSelected>>", lambda e: self.switch_lang_by_label(combo_lang.get()))
        r += 1

        ttk.Label(frm, text=self.texts["font_label"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        combo_font = ttk.Combobox(frm, values=sorted(families()), state="readonly")
        combo_font.set(self.settings["font_family"])
        combo_font.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        combo_font.bind("<MouseWheel>", self.font_mouse_wheel) # enable mouse wheel scrolling
        combo_font.bind("<<ComboboxSelected>>", lambda e: self.change_font(combo_font.get()))
        r += 1

        ttk.Label(frm, text=self.texts["time_font_size"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        ftf = ttk.Frame(frm)
        ftf.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(ftf, text="-1", command=lambda: self.edit_time_font(-1)).pack(side="left")
        self.lbl_time_font = ttk.Label(ftf, text=str(self.settings["time_font_size"]))
        self.lbl_time_font.pack(side="left")
        ttk.Button(ftf, text="+1", command=lambda: self.edit_time_font(1)).pack(side="left")
        r += 1

        ttk.Label(frm, text=self.texts["icon_font_size"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        fic = ttk.Frame(frm)
        fic.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(fic, text="-1", command=lambda: self.edit_icon_size(-1)).pack(side="left")
        self.lbl_icon_font = ttk.Label(fic, text=str(self.settings["icon_size"]))
        self.lbl_icon_font.pack(side="left")
        ttk.Button(fic, text="+1", command=lambda: self.edit_icon_size(1)).pack(side="left")
        r += 1

        pcv = [self.texts["seconds"], "100" + self.texts["milliseconds"], "10" + self.texts["milliseconds"], self.texts["milliseconds"]]
        ttk.Label(frm, text=self.texts["precision"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        combo_tp = ttk.Combobox(frm, values=pcv, state="readonly")
        combo_tp.bind("<MouseWheel>", lambda e: "break")
        combo_tp.set(pcv[int(self.settings["time_precision_digits"])])
        combo_tp.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        combo_tp.bind("<<ComboboxSelected>>", lambda e: self.change_precision_by_text(combo_tp.get()))
        r += 1

        ttk.Label(frm, text=self.texts["width"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        width_frame = ttk.Frame(frm)
        self.width_entry = ttk.Entry(width_frame, width=6)
        width_frame.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(width_frame, text="-10", command=lambda: self.edit_width(-10), width=4).pack(side="left")
        ttk.Button(width_frame, text="-1", command=lambda: self.edit_width(-1), width=4).pack(side="left")
        self.width_entry.insert(0, str(self.settings["width"]))
        self.width_entry.pack(side="left", padx=5)
        ttk.Button(width_frame, text="+1", command=lambda: self.edit_width(1), width=4).pack(side="left")
        ttk.Button(width_frame, text="+10", command=lambda: self.edit_width(10), width=4).pack(side="left")
        self.width_entry.bind("<KeyRelease>", lambda e: self.change_width(self.width_entry.get()))
        r += 1

        ttk.Label(frm, text=self.texts["height"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        height_frame = ttk.Frame(frm)
        self.height_entry = ttk.Entry(height_frame, width=6)
        height_frame.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        ttk.Button(height_frame, text="-10", command=lambda: self.edit_height(-10), width=4).pack(side="left")
        ttk.Button(height_frame, text="-1", command=lambda: self.edit_height(-1), width=4).pack(side="left")
        self.height_entry.insert(0, str(self.settings["height"]))
        self.height_entry.pack(side="left", padx=5)
        ttk.Button(height_frame, text="+1", command=lambda: self.edit_height(1), width=4).pack(side="left")
        ttk.Button(height_frame, text="+10", command=lambda: self.edit_height(10), width=4).pack(side="left")
        self.height_entry.bind("<KeyRelease>", lambda e: self.change_height(self.height_entry.get()))
        r += 1

        ttk.Label(frm, text=self.texts["sync_interval"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        sync_frame = ttk.Frame(frm)
        self.sync_entry = ttk.Entry(sync_frame, width=10)
        sync_frame.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        self.sync_entry.insert(0, str(self.settings["sync_interval"]))
        self.sync_entry.pack(side="left", padx=5)
        self.sync_entry.bind("<KeyRelease>", lambda e: self.change_sync_interval(self.sync_entry.get()))
        r += 1

        ttk.Label(frm, text=self.texts["time_excursion"]).grid(row=r, column=0, padx=10, pady=5, sticky="w")
        time_excursion_frame = ttk.Frame(frm)
        self.time_excursion_entry = ttk.Entry(time_excursion_frame, width=10)
        time_excursion_frame.grid(row=r, column=1, padx=10, pady=5, sticky="w")
        self.time_excursion_entry.insert(0, str(self.settings["time_excursion"]))
        self.time_excursion_entry.pack(side="left", padx=5)
        ttk.Button(time_excursion_frame, text=self.texts["online_sync"], command=lambda: self.update_time(online=True)).pack(side="left")
        self.time_excursion_entry.bind("<KeyRelease>", lambda e: self.change_time_excursion(self.time_excursion_entry.get()))
        r += 1

        ttk.Button(frm, text=self.texts["restore_default"], command=self.restore_default).grid(row=r, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        r += 1

        ttk.Button(frm, text=self.texts["project_link"], command=lambda: webbrowser.open('https://github.com/liaoyanqing666/Time_Floating_Window')).grid(row=r, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        r += 1

        ttk.Button(frm, text=self.texts["author"], command=lambda: webbrowser.open('https://github.com/liaoyanqing666')).grid(row=r, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        r += 1

    def font_mouse_wheel(self, e):
        # Enable mouse wheel scrolling for the font combobox
        self.inc_font() if e.delta > 0 else self.dec_font()

    def inc_font(self):
        # Get the font families and change to the next one
        fonts = sorted(families())
        current = self.settings["font_family"]
        try:
            idx = fonts.index(current)
        except ValueError:
            idx = 0
        if idx < len(fonts) - 1:
            self.change_font(fonts[idx + 1])

    def dec_font(self):
        # Get the font families and change to the previous one
        fonts = sorted(families())
        current = self.settings["font_family"]
        try:
            idx = fonts.index(current)
        except ValueError:
            idx = 0
        if idx > 0:
            self.change_font(fonts[idx - 1])

    def alpha_scale_changed(self, v):
        # When the value of the scale widget changes
        try:
            f = max(0.05, min(float(v), 1.0))
            f = round(f, 2)
            self.settings["bg_opacity"] = f
            self.floating_window.attributes("-alpha", f)
            self.alpha_entry.delete(0, tk.END)
            self.alpha_entry.insert(0, str(f))
            self.save_settings()
        except ValueError:
            pass

    def alpha_entry_apply(self):
        # Apply the opacity value from the entry box
        try:
            f = float(self.alpha_entry.get())
            f = max(self.settings.get("min_opacity", 0.05), min(f, 1.0))
            f = round(f, 2)
            self.settings["bg_opacity"] = f
            self.floating_window.attributes("-alpha", f)
            self.alpha_scale.set(f)
            self.alpha_entry.delete(0, tk.END)
            self.alpha_entry.insert(0, str(f))
            self.save_settings()
        except ValueError:
            # Reset to current setting if invalid
            self.alpha_entry.delete(0, tk.END)
            self.alpha_entry.insert(0, str(self.settings["bg_opacity"]))

    def restore_default(self):
        # When the user clicks the Restore Default Settings button, confirm and restore
        if messagebox.askyesno(self.texts["confirm"], self.texts["restore_confirm"]):
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            self.load_settings()
            self.save_settings()
            messagebox.showinfo(self.texts["info"], self.texts["restore_done"])
            self.quit_app()

    def show_button_locked(self, v):
        self.settings["show_buttons_when_locked"] = v
        self.arrange_buttons()
        self.save_settings()

    def show_button_unlocked(self, v):
        self.settings["show_buttons_when_unlocked"] = v
        self.arrange_buttons()
        self.save_settings()

    def pick_bg_color(self):
        # Open the color chooser dialog and set the background color
        c = colorchooser.askcolor()[1]
        if c:
            self.settings["bg_color"] = c
            for widget in [self.floating_window, self.time_label, self.pin_button, self.close_button]:
                widget.config(bg=c)
            self.save_settings()

    def pick_text_color(self):
        # Open the color chooser dialog and set the text color
        c = colorchooser.askcolor()[1]
        if c:
            self.settings["text_color"] = c
            for widget in [self.time_label, self.pin_button, self.close_button]:
                widget.config(fg=c)
            self.save_settings()

    def change_font(self, f):
        # Change the font family
        self.settings["font_family"] = f
        self.time_label.config(font=(f, self.settings["time_font_size"]))
        self.pin_button.config(font=(f, self.settings["icon_size"]))
        self.close_button.config(font=(f, self.settings["icon_size"]))
        self.save_settings()
        self.check_size_for_font_change()

    def check_size_for_font_change(self):
        # Check if the window size is enough for the new font size
        w, h = self.settings["width"], self.settings["height"]
        lw, lh = self.min_label_w(), self.min_label_h()
        resized = False
        if w < lw:
            self.settings["width"] = lw
            resized = True
        if h < lh:
            self.settings["height"] = lh
            resized = True
        if resized:
            self.update_geometry()
            self.save_settings()

    def change_precision_by_text(self, txt):
        # Change the time precision
        if txt == self.texts["seconds"]:
            self.set_precision(0)
        elif txt == "100" + self.texts["milliseconds"]:
            self.set_precision(1)
        elif txt == "10" + self.texts["milliseconds"]:
            self.set_precision(2)
        elif txt == self.texts["milliseconds"]:
            self.set_precision(3)
        else:
            self.set_precision(0)

    def set_precision(self, p):
        # Set the time precision and adjust the window size if necessary
        self.settings["time_precision_digits"] = p
        if self.settings["width"] < self.min_label_w():
            self.settings["width"] = self.min_label_w()
            self.update_geometry()
        self.save_settings()

    def change_width(self, v):
        # Change the width of the window
        if v.isdigit():
            w = max(int(v), self.min_label_w())
            self.settings["width"] = min(w, self.settings["max_width"])
            self.update_geometry()
            self.save_settings()

    def change_height(self, v):
        # Change the height of the window
        if v.isdigit():
            h = max(int(v), self.min_label_h())
            self.settings["height"] = min(h, self.settings["max_height"])
            self.update_geometry()
            self.save_settings()

    def edit_width(self, n):
        # Edit the width of the window by button
        try:
            current = int(self.width_entry.get())
        except ValueError:
            current = self.settings["width"]
        new_width = current + n
        if new_width < self.min_label_w():
            new_width = self.min_label_w()
        elif new_width > self.settings["max_width"]:
            new_width = self.settings["max_width"]
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(new_width))
        self.change_width(str(new_width))

    def edit_height(self, n):
        # Edit the height of the window by button
        try:
            current = int(self.height_entry.get())
        except ValueError:
            current = self.settings["height"]
        new_height = current + n
        if new_height < self.min_label_h():
            new_height = self.min_label_h()
        elif new_height > self.settings["max_height"]:
            new_height = self.settings["max_height"]
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(new_height))
        self.change_height(str(new_height))

    def edit_time_font(self, n):
        # Edit the time font size
        self.settings["time_font_size"] += n
        if self.settings["time_font_size"] < 8:
            self.settings["time_font_size"] = 8
        elif self.settings["time_font_size"] > 72:
            self.settings["time_font_size"] = 72
        self.lbl_time_font.config(text=str(self.settings["time_font_size"]))
        self.time_label.config(font=(self.settings["font_family"], self.settings["time_font_size"]))
        self.save_settings()
        self.check_size_for_font_change()

    def edit_icon_size(self, n):
        # Edit the icon font size
        self.settings["icon_size"] += n
        if self.settings["icon_size"] < 8:
            self.settings["icon_size"] = 8
        elif self.settings["icon_size"] > 72:
            self.settings["icon_size"] = 72
        self.lbl_icon_font.config(text=str(self.settings["icon_size"]))
        self.update_buttons()
        self.save_settings()

    def change_sync_interval(self, v):
        # Change the sync interval
        try:
            i = int(v)
            self.settings["sync_interval"] = max(1, i)
            self.save_settings()
        except ValueError:
            pass

    def change_time_excursion(self, v):
        # Change the time excursion
        try:
            i = int(v)
            self.settings["time_excursion"] = i
            self.save_settings()
        except ValueError:
            pass

    def update_buttons(self):
        # Update the font size of the buttons
        for button in [self.pin_button, self.close_button]:
            button.config(font=(self.settings["font_family"], self.settings["icon_size"]))

    def min_label_w(self):
        # Get the minimum width of the time label to ensure the text fits
        original_text = self.time_label.cget("text")
        test_text = "89:88:88" + ("." if self.settings["time_precision_digits"] > 0 else "") + "8" * int(self.settings["time_precision_digits"])
        self.time_label.config(text=test_text)
        self.floating_window.update_idletasks()
        lw = self.time_label.winfo_reqwidth()
        self.time_label.config(text=original_text)
        return lw

    def min_label_h(self):
        # Get the minimum height of the time label to ensure the text fits
        original_text = self.time_label.cget("text")
        test_text = "89:88:88" + ("." if self.settings["time_precision_digits"] > 0 else "") + "8" * int(self.settings["time_precision_digits"])
        self.time_label.config(text=test_text)
        self.floating_window.update_idletasks()
        lh = self.time_label.winfo_reqheight()
        self.time_label.config(text=original_text)
        return lh

    def apply_position_or_center(self):
        # Apply the position if it is valid, otherwise center the window
        x, y = self.settings["last_position"]
        w, h = self.settings["width"], self.settings["height"]
        if not self.center_in_screen(x, y, w, h):
            self.center_window()
        else:
            self.floating_window.geometry(f'{w}x{h}+{x}+{y}')

    def center_window(self):
        # Center the window on the screen
        w, h = self.settings["width"], self.settings["height"]
        sw, sh = self.floating_window.winfo_screenwidth(), self.floating_window.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.floating_window.geometry(f'{w}x{h}+{x}+{y}')

    def update_geometry(self):
        # Update the window geometry
        if self.settings["last_position"]:
            x, y = self.settings["last_position"]
            w, h = self.settings["width"], self.settings["height"]
            self.floating_window.geometry(f'{w}x{h}+{x}+{y}')
        else:
            self.center_window()

    def center_in_screen(self, x, y, w, h):
        # Check if the window is within the screen boundaries
        cx, cy = x + w / 2, y + h / 2
        sw, sh = self.floating_window.winfo_screenwidth(), self.floating_window.winfo_screenheight()
        return 0 <= cx <= sw and 0 <= cy <= sh

    def update_time(self, online=False):
        # Update the time label
        if online:
            try:
                c = ntplib.NTPClient()
                response = c.request('pool.ntp.org')
                network_time = datetime.fromtimestamp(response.tx_time)
                now = datetime.now()
                # # with delay
                # round_trip_delay = response.delay
                # self.settings["time_excursion"] = int(((now - network_time).total_seconds() + round_trip_delay/2) * 1000)
                # without delay
                self.settings["time_excursion"] = int((now - network_time).total_seconds() * 1000)
                self.time_excursion_entry.delete(0, tk.END)
                self.time_excursion_entry.insert(0, str(self.settings["time_excursion"]))
                self.save_settings()
            except Exception as e:
                print(e)
        now = datetime.now()
        now += timedelta(milliseconds=self.settings["time_excursion"])
        if int(self.settings["time_precision_digits"]) > 0:
            formatted_time = now.strftime("%H:%M:%S.%f")[: -6 + int(self.settings["time_precision_digits"])]
        else:
            formatted_time = now.strftime("%H:%M:%S")
        self.time_label.config(text=formatted_time)
        self.floating_window.after(self.settings["sync_interval"], self.update_time)

    def quit_app(self):
        # Quit the application
        self.settings["last_position"] = [self.floating_window.winfo_x(), self.floating_window.winfo_y()]
        self.save_settings()
        if self.settings_window and tk.Toplevel.winfo_exists(self.settings_window):
            self.settings_window.destroy()
        self.floating_window.destroy()
        self.root.destroy()

    def switch_lang_by_label(self, lb):
        # Switch the language by the language label
        found_key = next((k for k, v in self.translations.items() if v["lang_label"] == lb), None)
        if found_key and found_key != self.lang:
            confirm_message = self.texts["lang_switch_confirm"].format(language=lb)
            if messagebox.askyesno(self.texts["confirm"], confirm_message):
                self.settings["language"] = found_key
                self.settings["settings_window_size"] = None
                self.quit_app()

    def check_autostart(self):
        # Check if the application is set to autostart
        try:
            program_name = self.texts["app_name"]
            program_path = sys.executable
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            reg_key = reg.HKEY_CURRENT_USER
            key = reg.OpenKey(reg_key, reg_path, 0, reg.KEY_READ)
            value, _ = reg.QueryValueEx(key, program_name)
            reg.CloseKey(key)
            return value == program_path

        except FileNotFoundError:
            return False

    def set_autostart(self, enable=True):
        # Set the application to autostart
        program_name = self.texts["app_name"]
        program_path = sys.executable
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        reg_key = reg.HKEY_CURRENT_USER
        key = reg.OpenKey(reg_key, reg_path, 0, reg.KEY_WRITE)

        if enable:
            reg.SetValueEx(key, program_name, 0, reg.REG_SZ, program_path)
        else:
            reg.DeleteValue(key, program_name)

        reg.CloseKey(key)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # start with admin rights
    FloatingClockApp().run()
