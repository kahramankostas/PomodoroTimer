#!/usr/bin/env python3
"""
Pomodoro Pro v2.3
- MP3/WAV Alarm Support Added
- Sound Alarm On/Off Feature
- Duration Settings
- Tabbed Interface (Timer, History, Statistics)
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import csv
from datetime import datetime, date
from pathlib import Path
import os

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# pygame for sound playback
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# File names
RECORDS_PATH = Path(os.path.expanduser("~")) / "pomodoro_records.csv"
SETTINGS_PATH = Path(os.path.expanduser("~")) / "pomodoro_settings.txt"

class AdvancedPomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Pro - Full Control")
        self.root.geometry("900x750")
        
        # --- VARIABLES ---
        self.work_min = tk.IntVar(value=25)
        self.short_break_min = tk.IntVar(value=5)
        self.long_break_min = tk.IntVar(value=15)
        self.cycles_before_long = tk.IntVar(value=4)
        self.sound_enabled = tk.BooleanVar(value=True)
        self.sound_file = tk.StringVar(value="")

        self.sequence = []
        self.build_sequence()
        self.seq_index = 0
        self.remaining = 0
        self.running = False
        self.paused = False
        self.after_id = None

        # Load settings
        self.load_settings()

        # --- INTERFACE (TABS) ---
        self.tabs = ttk.Notebook(self.root, bootstyle="primary")
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Timer
        self.tab_timer = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_timer, text='⏱ Timer & Settings')
        self.build_timer_tab()

        # Tab 2: History
        self.tab_history = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_history, text='📝 History')
        self.build_history_tab()

        # Tab 3: Statistics
        self.tab_stats = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_stats, text='📊 Statistics')
        self.build_stats_tab()

        # Events
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Initial
        self.update_display_initial()
        self.load_history_data()

    # ----------------------------------------------------------------
    # 1. TIMER AND SETTINGS TAB
    # ----------------------------------------------------------------
    def build_timer_tab(self):
        # 1. Counter Area
        timer_frame = ttk.Frame(self.tab_timer, padding=10)
        timer_frame.pack(fill="x")

        self.mode_label = ttk.Label(timer_frame, text="Ready", font=("Helvetica", 16, "bold"), bootstyle="secondary")
        self.mode_label.pack(anchor="center")

        self.time_label = ttk.Label(timer_frame, text="00:00", font=("Helvetica", 72, "bold"), bootstyle="primary")
        self.time_label.pack(anchor="center", pady=5)

        self.progress = ttk.Progressbar(timer_frame, length=600, mode='determinate', bootstyle="primary-striped")
        self.progress.pack(pady=10)

        # 2. Control Buttons
        ctrl_frame = ttk.Frame(self.tab_timer, padding=5)
        ctrl_frame.pack(fill="x")
        btn_box = ttk.Frame(ctrl_frame)
        btn_box.pack(anchor="center")

        ttk.Button(btn_box, text="▶ START", command=self.start, bootstyle="success", width=10).pack(side="left", padx=5)
        ttk.Button(btn_box, text="⏸ PAUSE", command=self.pause_resume, bootstyle="warning", width=10).pack(side="left", padx=5)
        ttk.Button(btn_box, text="⏭ SKIP", command=self.skip, bootstyle="info", width=8).pack(side="left", padx=5)
        ttk.Button(btn_box, text="⟳ RESET", command=self.reset, bootstyle="secondary-outline", width=8).pack(side="left", padx=5)

        # 3. SETTINGS AREA
        settings_frame = ttk.Labelframe(self.tab_timer, text="Time Settings (Minutes)", padding=15, bootstyle="secondary")
        settings_frame.pack(fill="x", padx=20, pady=15)

        # Work Duration
        ttk.Label(settings_frame, text="Work:").grid(row=0, column=0, padx=5, sticky="e")
        self.spin_work = ttk.Spinbox(settings_frame, from_=1, to=120, textvariable=self.work_min, width=5, command=self.on_settings_change)
        self.spin_work.grid(row=0, column=1, padx=5)

        # Short Break
        ttk.Label(settings_frame, text="Short Break:").grid(row=0, column=2, padx=5, sticky="e")
        self.spin_short = ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.short_break_min, width=5, command=self.on_settings_change)
        self.spin_short.grid(row=0, column=3, padx=5)

        # Long Break
        ttk.Label(settings_frame, text="Long Break:").grid(row=0, column=4, padx=5, sticky="e")
        self.spin_long = ttk.Spinbox(settings_frame, from_=5, to=60, textvariable=self.long_break_min, width=5, command=self.on_settings_change)
        self.spin_long.grid(row=0, column=5, padx=5)

        # Cycle Count
        ttk.Label(settings_frame, text="Cycles:").grid(row=0, column=6, padx=5, sticky="e")
        self.spin_cycle = ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.cycles_before_long, width=5, command=self.on_settings_change)
        self.spin_cycle.grid(row=0, column=7, padx=5)

        settings_frame.grid_columnconfigure(8, weight=1)

        # 4. SOUND ALARM SETTINGS
        sound_frame = ttk.Labelframe(self.tab_timer, text="🔔 Sound Alarm Settings", padding=15, bootstyle="info")
        sound_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Alarm Toggle
        self.sound_check = ttk.Checkbutton(
            sound_frame, 
            text="Enable sound alarm when timer ends",
            variable=self.sound_enabled,
            bootstyle="info-round-toggle",
            command=self.save_settings
        )
        self.sound_check.pack(anchor="w", pady=(0, 10))

        # Sound File Selection
        file_box = ttk.Frame(sound_frame)
        file_box.pack(fill="x")
        
        ttk.Label(file_box, text="Alarm Sound:").pack(side="left", padx=(0, 10))
        
        self.sound_file_label = ttk.Label(
            file_box, 
            text=self.get_sound_file_display(), 
            font=("Segoe UI", 9),
            foreground="gray"
        )
        self.sound_file_label.pack(side="left", fill="x", expand=True)
        
        ttk.Button(
            file_box, 
            text="📁 Select Sound", 
            command=self.choose_sound_file, 
            bootstyle="info-outline",
            width=12
        ).pack(side="right", padx=5)
        
        ttk.Button(
            file_box, 
            text="🔊 Test", 
            command=self.test_sound, 
            bootstyle="success-outline",
            width=8
        ).pack(side="right")

        # Pygame Warning
        if not PYGAME_AVAILABLE:
            warn_label = ttk.Label(
                sound_frame, 
                text="⚠ To play sound, 'pygame' library is required: pip install pygame",
                font=("Segoe UI", 8),
                foreground="orange"
            )
            warn_label.pack(anchor="w", pady=(5, 0))

        # 5. Quick Note Area
        note_area = ttk.Labelframe(self.tab_timer, text="What are you doing right now? (Note)", padding=10, bootstyle="info")
        note_area.pack(fill="x", padx=20, pady=(0, 20))
        
        self.note_text = ttk.Entry(note_area, font=("Segoe UI", 10))
        self.note_text.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(note_area, text="Save", command=self.save_manual_note, bootstyle="light-outline").pack(side="right")

    # ----------------------------------------------------------------
    # 2. HISTORY TAB
    # ----------------------------------------------------------------
    def build_history_tab(self):
        container = ttk.Frame(self.tab_history, padding=10)
        container.pack(fill="both", expand=True)

        cols = ("Date", "Mode", "Duration", "Note")
        self.tree = ttk.Treeview(container, columns=cols, show='headings', bootstyle="info")
        
        self.tree.heading("Date", text="Time")
        self.tree.column("Date", width=150, anchor="center")
        self.tree.heading("Mode", text="Type")
        self.tree.column("Mode", width=80, anchor="center")
        self.tree.heading("Duration", text="Duration (min)")
        self.tree.column("Duration", width=70, anchor="center")
        self.tree.heading("Note", text="Note")
        self.tree.column("Note", width=400, anchor="w")

        sb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ----------------------------------------------------------------
    # 3. STATISTICS TAB
    # ----------------------------------------------------------------
    def build_stats_tab(self):
        container = ttk.Frame(self.tab_stats, padding=20)
        container.pack(fill="both", expand=True)

        grid_frame = ttk.Frame(container)
        grid_frame.pack(fill="x", expand=True)

        # Today
        card1 = ttk.Labelframe(grid_frame, text="📅 TODAY", padding=20, bootstyle="success")
        card1.pack(side="left", fill="both", expand=True, padx=10)
        self.lbl_today_count = ttk.Label(card1, text="0 Sessions", font=("Helvetica", 12))
        self.lbl_today_count.pack()
        self.lbl_today_time = ttk.Label(card1, text="0 min", font=("Helvetica", 20, "bold"), bootstyle="success")
        self.lbl_today_time.pack(pady=5)

        # Total
        card2 = ttk.Labelframe(grid_frame, text="🏆 TOTAL", padding=20, bootstyle="primary")
        card2.pack(side="left", fill="both", expand=True, padx=10)
        self.lbl_total_count = ttk.Label(card2, text="0 Sessions", font=("Helvetica", 12))
        self.lbl_total_count.pack()
        self.lbl_total_time = ttk.Label(card2, text="0 min", font=("Helvetica", 20, "bold"), bootstyle="primary")
        self.lbl_total_time.pack(pady=5)

    # ----------------------------------------------------------------
    # SOUND OPERATIONS
    # ----------------------------------------------------------------
    def choose_sound_file(self):
        """Selected sound file"""
        filetypes = (
            ('Audio Files', '*.mp3 *.wav *.ogg'),
            ('MP3', '*.mp3'),
            ('WAV', '*.wav'),
            ('All Files', '*.*')
        )
        filename = filedialog.askopenfilename(
            title='Select Alarm Sound',
            filetypes=filetypes
        )
        if filename:
            self.sound_file.set(filename)
            self.sound_file_label.config(text=self.get_sound_file_display())
            self.save_settings()
            messagebox.showinfo("Success", "Alarm sound selected!")

    def get_sound_file_display(self):
        """Shorten sound file name"""
        if not self.sound_file.get():
            return "No sound file selected (default system sound will play)"
        filename = Path(self.sound_file.get()).name
        if len(filename) > 40:
            return filename[:37] + "..."
        return filename

    def test_sound(self):
        """Test selected sound"""
        if not self.sound_enabled.get():
            messagebox.showwarning("Warning", "Enable 'Sound Alarm' option first!")
            return
        self.play_alarm()

    def play_alarm(self):
        """Play alarm sound"""
        if not self.sound_enabled.get():
            return

        # If custom sound file exists
        if self.sound_file.get() and Path(self.sound_file.get()).exists():
            if PYGAME_AVAILABLE:
                try:
                    pygame.mixer.music.load(self.sound_file.get())
                    pygame.mixer.music.play()
                    return
                except Exception as e:
                    messagebox.showerror("Sound Error", f"Could not play sound: {e}")
            else:
                messagebox.showwarning("Pygame Required", "Pygame must be installed to play MP3/WAV:\npip install pygame")
        
        # Default system sound
        try:
            self.root.bell()
        except:
            pass

    # ----------------------------------------------------------------
    # SETTINGS SAVE/LOAD
    # ----------------------------------------------------------------
    def save_settings(self):
        """Save settings"""
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                f.write(f"sound_enabled={self.sound_enabled.get()}\n")
                f.write(f"sound_file={self.sound_file.get()}\n")
        except:
            pass

    def load_settings(self):
        """Load settings"""
        if not SETTINGS_PATH.exists():
            return
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        if key == "sound_enabled":
                            self.sound_enabled.set(value.lower() == "true")
                        elif key == "sound_file":
                            self.sound_file.set(value)
        except:
            pass

    # ----------------------------------------------------------------
    # LOGIC
    # ----------------------------------------------------------------
    def on_settings_change(self):
        """Update timer when settings change (If not running)"""
        if self.running: return
        self.build_sequence()
        self.seq_index = 0
        self.update_display_initial()

    def on_tab_change(self, event):
        self.load_history_data()
        self.calculate_stats()

    def build_sequence(self):
        cycles = self.cycles_before_long.get()
        self.sequence = []
        for i in range(cycles):
            self.sequence.append(("Work", self.work_min.get()))
            if i < cycles - 1:
                self.sequence.append(("Short", self.short_break_min.get()))
            else:
                self.sequence.append(("Long", self.long_break_min.get()))

    def start(self):
        if not self.sequence: self.build_sequence()
        if not self.running:
            mode, minutes = self.sequence[self.seq_index]
            self.update_visual_theme(mode)
            self.remaining = minutes * 60
            self.progress['maximum'] = self.remaining
            self.running = True
            self.paused = False
            self.tick()

    def pause_resume(self):
        if not self.running: return
        self.paused = not self.paused
        if self.paused:
            self.mode_label.config(text=f"{self.mode_label.cget('text')} (Paused)")
            if self.after_id: self.root.after_cancel(self.after_id)
        else:
            txt = self.mode_label.cget("text").replace(" (Paused)", "")
            self.mode_label.config(text=txt)
            self.tick()

    def skip(self):
        if self.after_id: self.root.after_cancel(self.after_id)
        self.seq_index = (self.seq_index + 1) % len(self.sequence)
        self.running = False
        self.start()

    def reset(self):
        if self.after_id: self.root.after_cancel(self.after_id)
        self.running = False
        self.paused = False
        self.seq_index = 0
        self.build_sequence()
        self.update_display_initial()

    def tick(self):
        if self.paused: return
        if self.remaining <= 0:
            # Sound alarm
            self.play_alarm()
            
            mode, minutes = self.sequence[self.seq_index]
            
            # Save note
            note = self.note_text.get().strip()
            self.record_session(mode, minutes, note)
            self.note_text.delete(0, tk.END)
            
            # Next
            self.seq_index = (self.seq_index + 1) % len(self.sequence)
            self.running = False
            self.start()
            
            messagebox.showinfo("Finished", f"{mode} time is up! Moved to next round.")
            return

        self.time_label.config(text=f"{self.remaining // 60:02d}:{self.remaining % 60:02d}")
        self.progress['value'] = self.progress['maximum'] - self.remaining
        self.remaining -= 1
        self.after_id = self.root.after(1000, self.tick)

    def record_session(self, mode, minutes, note):
        try:
            first_write = not RECORDS_PATH.exists()
            with open(RECORDS_PATH, "a", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                if first_write:
                    writer.writerow(["timestamp","mode","minutes","note"])
                ts = datetime.now().isoformat(sep=' ', timespec='seconds')
                writer.writerow([ts, mode, minutes, note])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_manual_note(self):
        note = self.note_text.get().strip()
        if note:
            self.record_session("Note", 0, note)
            self.note_text.delete(0, tk.END)
            messagebox.showinfo("Success", "Note saved.")

    def load_history_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not RECORDS_PATH.exists(): return
        try:
            with open(RECORDS_PATH, newline='', encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                rows = list(reader)
                for row in reversed(rows):
                    if len(row) >= 4:
                        self.tree.insert("", "end", values=row)
        except: pass

    def calculate_stats(self):
        if not RECORDS_PATH.exists(): return
        today_str = date.today().isoformat()
        total_mins, total_sess = 0, 0
        today_mins, today_sess = 0, 0

        try:
            with open(RECORDS_PATH, newline='', encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) < 3: continue
                    ts, mode, minutes, _ = row[:4]
                    if mode == "Work":
                        mins = int(minutes)
                        total_mins += mins
                        total_sess += 1
                        if ts.startswith(today_str):
                            today_mins += mins
                            today_sess += 1
            
            self.lbl_today_count.config(text=f"{today_sess} Sessions")
            self.lbl_today_time.config(text=f"{today_mins} min")
            self.lbl_total_count.config(text=f"{total_sess} Sessions")
            self.lbl_total_time.config(text=f"{total_mins//60}h {total_mins%60}min")
        except: pass

    def update_visual_theme(self, mode):
        text = f"{'🔥' if mode=='Work' else '☕'} {mode} ({self.seq_index+1}/{len(self.sequence)})"
        self.mode_label.config(text=text)
        color = "danger" if mode == "Work" else "success"
        self.time_label.configure(bootstyle=color)
        self.progress.configure(bootstyle=f"{color}-striped")

    def update_display_initial(self):
        if self.sequence:
            mode, minutes = self.sequence[0]
            self.update_visual_theme(mode)
            self.time_label.config(text=f"{minutes:02d}:00")

def on_close(root, app):
    if messagebox.askokcancel("Exit", "Do you want to quit?"):
        if app.after_id: root.after_cancel(app.after_id)
        root.destroy()

if __name__ == "__main__":
    app_window = ttk.Window(themename="flatly")
    app = AdvancedPomodoroApp(app_window)
    app_window.protocol("WM_DELETE_WINDOW", lambda: on_close(app_window, app))
    app_window.mainloop()