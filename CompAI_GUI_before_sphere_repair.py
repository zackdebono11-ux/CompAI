import os
import sys
import time
import math
import queue
import signal
import threading
import subprocess
import tkinter as tk
from tkinter import ttk
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    Image = ImageDraw = ImageFont = ImageTk = None
    PIL_AVAILABLE = False

APP_VERSION = "0.15.0"
BASE_DIR = Path(__file__).resolve().parent
BACKEND = BASE_DIR / "AI.py"

BG = "#070b14"
PANEL = "#101827"
PANEL_2 = "#17243a"
BORDER = "#263f68"
ACCENT = "#55c8ff"
ACCENT_SOFT = "#168ff0"
ACCENT_DARK = "#174f91"
TEXT = "#eaf6ff"
MUTED = "#8da9ca"
ORANGE = "#ffc36b"
RED = "#ff6868"


class CompAIGUI:
    """CompAI's animated orb interface. The existing AI.py remains the command engine."""

    def __init__(self, root):
        self.root = root
        self.root.title(f"CompAI v{APP_VERSION}")
        self.root.geometry("1180x800")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG)

        self.output_queue = queue.Queue()
        self.process = None
        self.reader_thread = None
        self.closing = False
        self.wake_active = False
        self.visual_state = "idle"
        self.phase = 0.0
        self.pulse_phase = 0.0
        self.last_output_time = time.monotonic()

        self._build_style()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(70, self._drain_output)
        self.root.after(1000, self._update_metrics)
        self.root.after(65, self._animate_orb)
        self.root.after(250, self.start_backend)

    def _build_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Vertical.TScrollbar",
            background=PANEL_2,
            troughcolor=BG,
            bordercolor=BG,
            arrowcolor=MUTED,
        )

    def _build_ui(self):
        # Compact title/status bar
        header = tk.Frame(
            self.root, bg=PANEL, height=54,
            highlightbackground=BORDER, highlightthickness=1
        )
        header.pack(fill="x", padx=12, pady=(12, 6))
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=PANEL)
        brand.pack(side="left", padx=16, pady=7)
        tk.Label(
            brand, text="◈  CompAI", bg=PANEL, fg=ACCENT,
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w")
        tk.Label(
            brand, text=f"BLUE AI CORE  •  v{APP_VERSION}",
            bg=PANEL, fg=MUTED, font=("Segoe UI", 7, "bold")
        ).pack(anchor="w")

        self.connection_label = tk.Label(
            header, text="● STARTING", bg=PANEL, fg=ORANGE,
            font=("Segoe UI", 9, "bold")
        )
        self.connection_label.pack(side="right", padx=18)

        # Quick actions are deliberately small so the orb stays central.
        toolbar = tk.Frame(self.root, bg=BG)
        toolbar.pack(fill="x", padx=14, pady=(0, 5))
        actions = [
            ("VOICE", "voice"),
            ("APPS", "apps"),
            ("MONITOR", "monitor"),
            ("PROCESSES", "processes"),
            ("EMAIL SHARE", "share email"),
            ("NEARBY", "share nearby"),
            ("HELP", "help"),
        ]
        for label, command in actions:
            self._toolbar_button(
                toolbar, label, lambda c=command: self.send_command(c)
            )

        self.wake_button = tk.Button(
            toolbar, text="◉  WAKE MODE", command=self.toggle_wake,
            bg="#17345c", fg=ACCENT, activebackground="#24558b",
            activeforeground=TEXT, relief="flat", bd=0,
            font=("Segoe UI", 8, "bold"), cursor="hand2",
            padx=12, pady=7
        )
        self.wake_button.pack(side="right", padx=(4, 0))

        # Large animated orb stage
        stage = tk.Frame(
            self.root, bg=BG, highlightbackground="#142d50",
            highlightthickness=1
        )
        stage.pack(fill="both", expand=True, padx=14, pady=(2, 7))
        self.orb_canvas = tk.Canvas(
            stage, bg=BG, highlightthickness=0, bd=0
        )
        self.orb_canvas.pack(fill="both", expand=True)
        self.orb_canvas.bind("<Configure>", self._on_canvas_resize)

        # Compact live output panel
        output_panel = tk.Frame(
            self.root, bg=PANEL, height=132,
            highlightbackground=BORDER, highlightthickness=1
        )
        output_panel.pack(fill="x", padx=14, pady=(0, 7))
        output_panel.pack_propagate(False)

        output_head = tk.Frame(output_panel, bg=PANEL_2, height=25)
        output_head.pack(fill="x")
        output_head.pack_propagate(False)
        tk.Label(
            output_head, text="  LIVE CONSOLE", bg=PANEL_2, fg=ACCENT,
            font=("Segoe UI", 8, "bold")
        ).pack(side="left", pady=4)
        tk.Label(
            output_head, text="LOCAL SESSION  ", bg=PANEL_2, fg=MUTED,
            font=("Segoe UI", 7)
        ).pack(side="right", pady=4)

        text_frame = tk.Frame(output_panel, bg=PANEL)
        text_frame.pack(fill="both", expand=True, padx=8, pady=6)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        self.chat = tk.Text(
            text_frame, bg="#0b1220", fg=TEXT, insertbackground=ACCENT,
            selectbackground=ACCENT_DARK, relief="flat", wrap="word",
            padx=9, pady=6, font=("Consolas", 9), state="disabled"
        )
        self.chat.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(text_frame, command=self.chat.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.chat.configure(yscrollcommand=scroll.set)
        self.chat.tag_configure("system", foreground=ACCENT)
        self.chat.tag_configure("user", foreground="#8fc7ff")
        self.chat.tag_configure("muted", foreground=MUTED)
        self.chat.tag_configure("warning", foreground=ORANGE)

        self._append("CompAI orb interface v0.15.0\n", "system")
        self._append("Connecting to your existing CompAI engine…\n", "muted")

        # Command input
        entry_bar = tk.Frame(self.root, bg=BG)
        entry_bar.pack(fill="x", padx=14, pady=(0, 7))
        entry_bar.grid_columnconfigure(0, weight=1)
        self.entry = tk.Entry(
            entry_bar, bg="#101d31", fg=TEXT, insertbackground=ACCENT,
            relief="flat", font=("Segoe UI", 10),
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT
        )
        self.entry.grid(row=0, column=0, sticky="ew", ipady=10, padx=(0, 8))
        self.entry.insert(0, "Talk to CompAI — type a command…")
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<Return>", lambda _event: self.send_entry())

        self.send_btn = tk.Button(
            entry_bar, text="SEND  ➤", command=self.send_entry,
            bg=ACCENT_DARK, fg="white", activebackground=ACCENT,
            activeforeground=BG, relief="flat", bd=0,
            font=("Segoe UI", 9, "bold"), cursor="hand2",
            padx=20, pady=8
        )
        self.send_btn.grid(row=0, column=1)

        footer = tk.Frame(self.root, bg=BG, height=22)
        footer.pack(fill="x", padx=16, pady=(0, 5))
        footer.pack_propagate(False)
        self.footer_status = tk.Label(
            footer, text="● Initialising", bg=BG, fg=MUTED,
            font=("Segoe UI", 8)
        )
        self.footer_status.pack(side="left")
        self.metric_status = tk.Label(
            footer, text="CPU —   RAM —   DISK —   BATTERY —",
            bg=BG, fg=MUTED, font=("Consolas", 8)
        )
        self.metric_status.pack(side="right")

    def _toolbar_button(self, parent, label, callback):
        button = tk.Button(
            parent, text=label, command=callback, bg=PANEL,
            fg=TEXT, activebackground=PANEL_2, activeforeground=ACCENT,
            relief="flat", bd=0, font=("Segoe UI", 8, "bold"),
            cursor="hand2", padx=10, pady=7
        )
        button.pack(side="left", padx=(0, 4))

    def _clear_placeholder(self, _event=None):
        if self.entry.get().startswith("Talk to CompAI"):
            self.entry.delete(0, "end")

    def _append(self, value, tag=None):
        self.chat.configure(state="normal")
        self.chat.insert("end", value, tag or "")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    # ---------- Orb drawing and animation ----------

    def _on_canvas_resize(self, _event=None):
        self._draw_orb()

    
   
    def _draw_orb(self):
        """Draw a glowing, glass-like plasma sphere."""
        import time

        profile_start = time.perf_counter()
        profile = {}

        canvas = self.orb_canvas

        # Clear previous frame.
        stage_start = time.perf_counter()

        canvas.delete("all")
        self._orb_text_images = []

        width = max(canvas.winfo_width(), 400)
        height = max(canvas.winfo_height(), 300)

        cx = width / 2
        cy = height / 2 - 18
        radius = min(width * 0.19, height * 0.37, 190)
        radius = max(radius, 105)

        state = self.visual_state

        if state == "error":
            glow = "#ff777d"
        elif state == "listening":
            glow = "#76eaff"
        else:
            glow = "#d18cff"

        profile["Canvas setup"] = time.perf_counter() - stage_start

        # Background stars.
        stage_start = time.perf_counter()

        for i in range(42):
            x = (i * 173 + 41) % int(width)
            y = (i * 97 + 23) % int(height)
            size = 1 if i % 4 else 2

            canvas.create_oval(
                x, y, x + size, y + size,
                fill="#26334c",
                outline=""
            )

        profile["Background stars"] = time.perf_counter() - stage_start

        # Rear lettering.
        stage_start = time.perf_counter()

        self._draw_wrapped_word(
            canvas, cx, cy, radius, behind=True
        )

        profile["Rear text"] = time.perf_counter() - stage_start

        # Generate the plasma sphere.
        if PIL_AVAILABLE:
            stage_start = time.perf_counter()

            orb = self._make_energy_sphere(
                max(300, int(radius * 2.55))
            )

            profile["Sphere generation"] = time.perf_counter() - stage_start

            # Convert the image for Tkinter.
            stage_start = time.perf_counter()

            self._orb_photo = ImageTk.PhotoImage(orb)

            profile["Image conversion"] = time.perf_counter() - stage_start

            # Display sphere.
            stage_start = time.perf_counter()

            canvas.create_image(
                cx, cy,
                image=self._orb_photo,
                anchor="center"
            )

            profile["Sphere canvas drawing"] = time.perf_counter() - stage_start

        else:
            stage_start = time.perf_counter()

            canvas.create_oval(
                cx-radius, cy-radius,
                cx+radius, cy+radius,
                fill="#251239",
                outline="#d18cff",
                width=3
            )

            profile["Sphere canvas drawing"] = time.perf_counter() - stage_start

        # Front lettering.
        stage_start = time.perf_counter()

        self._draw_wrapped_word(
            canvas, cx, cy, radius, behind=False
        )

        profile["Front text"] = time.perf_counter() - stage_start

        # Status labels.
        stage_start = time.perf_counter()

        labels = {
            "idle": "●  SYSTEM STANDBY",
            "listening": "◉  LISTENING",
            "processing": "◌  PROCESSING",
            "error": "●  ATTENTION REQUIRED"
        }

        canvas.create_text(
            cx, cy + radius * 1.18,
            text=labels.get(state, "●  SYSTEM STANDBY"),
            fill=glow,
            font=("Segoe UI", 9, "bold")
        )

        canvas.create_text(
            cx, cy + radius * 1.29,
            text="BLUE AI CORE  •  SECURE DESKTOP SESSION",
            fill="#8194b5",
            font=("Segoe UI", 7)
        )

        profile["Status labels"] = time.perf_counter() - stage_start

        # Print profiling results every 30 frames.
        total = time.perf_counter() - profile_start

        if not hasattr(self, "_profile_counter"):
            self._profile_counter = 0

        self._profile_counter += 1

        if self._profile_counter >= 30:
            print("\n===== COMPAI RENDER PROFILE =====")

            for name, duration in profile.items():
                print(f"{name}: {duration * 1000:.2f} ms")

            print(f"TOTAL: {total * 1000:.2f} ms")
            print("=================================\n")

            self._profile_counter = 0

    def _draw_wrapped_word(self, canvas, cx, cy, radius, behind):
        """Render CompAI text wrapped around the rotating sphere."""

        import math
        from PIL import Image, ImageDraw, ImageFont, ImageTk

        word = "CompAI"
        spacing = 0.245

        rotation = self.phase * 0.65
        cos_rotation = math.cos(rotation)
        sin_rotation = math.sin(rotation)

        surface_radius = 0.445 * max(300, int(radius * 2.55))
        font_size = max(22, int(radius * 0.19))

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        for index, character in enumerate(word):
            horizontal = (
                index - (len(word) - 1) / 2
            ) * spacing

            x3 = 0.82 * math.sin(horizontal)
            y3 = 0.0
            z3 = 0.82 * math.cos(horizontal)

            rotated_x = x3 * cos_rotation - z3 * sin_rotation
            rotated_z = x3 * sin_rotation + z3 * cos_rotation

            if behind and rotated_z >= 0:
                continue

            if not behind and rotated_z < 0:
                continue

            x = cx + rotated_x * surface_radius
            y = cy - y3 * surface_radius

            depth_scale = max(0.12, abs(rotated_z))

            letter_font_size = max(
                9,
                int(font_size * (0.72 + 0.28 * abs(rotated_z)))
            )

            try:
                letter_font = ImageFont.truetype(
                    "arial.ttf", letter_font_size
                )
            except OSError:
                letter_font = ImageFont.load_default()

            bbox = letter_font.getbbox(character)
            width = max(1, bbox[2] - bbox[0] + 24)
            height = max(1, bbox[3] - bbox[1] + 24)

            letter = Image.new(
                "RGBA", (width, height), (0, 0, 0, 0)
            )

            draw = ImageDraw.Draw(letter)

            draw.text(
                (14, 15),
                character,
                font=letter_font,
                fill=(0, 0, 0, 150)
            )

            draw.text(
                (12, 12),
                character,
                font=letter_font,
                fill=(225, 245, 255, 245),
                stroke_width=1,
                stroke_fill=(100, 190, 255, 220)
            )

            new_width = max(
                2,
                int(letter.width * max(0.18, depth_scale))
            )

            letter = letter.resize(
                (new_width, letter.height),
                Image.Resampling.LANCZOS
            )

            tilt = -math.degrees(
                math.atan2(rotated_x, max(0.15, rotated_z))
            ) * 0.12

            letter = letter.rotate(
                tilt,
                resample=Image.Resampling.BICUBIC,
                expand=True
            )

            image = ImageTk.PhotoImage(letter)
            self._orb_text_images.append(image)

            canvas.create_image(
                x, y,
                image=image,
                tags="orb_text"
            )

    def _make_energy_sphere(self, size):




    

   

   
        
   
     def _make_energy_sphere(self, size):
        """Render a detailed plasma sphere with cached glass effects."""
        from PIL import Image, ImageDraw, ImageFilter

        phase = self.phase

        quality = 1.35
        small = max(400, int(size * quality))
        scale = small / 420
        center = small / 2
        radius = small * 0.445

        # Calculate rotation once per frame.
        rotation = phase * 0.65
        cos_rotation = math.cos(rotation)
        sin_rotation = math.sin(rotation)

        # ==========================================
        # STATIC GLASS CACHE
        # ==========================================

        cache = getattr(self, "_orb_static_cache", None)

        if cache is None or cache["size"] != small:

            base = Image.new(
                "RGBA", (small, small), (0, 0, 0, 0)
            )

            # Dark glass body.
            body = Image.new(
                "RGBA", (small, small), (0, 0, 0, 0)
            )
            bd = ImageDraw.Draw(body)

            bd.ellipse(
                (center-radius, center-radius,
                 center+radius, center+radius),
                fill=(13, 5, 29, 255),
                outline=(126, 111, 255, 230),
                width=max(2, int(3 * scale))
            )

            base = Image.alpha_composite(base, body)

            # Coloured glass rim.
            rim = Image.new(
                "RGBA", (small, small), (0, 0, 0, 0)
            )
            rd = ImageDraw.Draw(rim)

            rd.arc(
                (center-radius, center-radius,
                 center+radius, center+radius),
                190, 300,
                fill=(255, 105, 65, 245),
                width=max(2, int(5 * scale))
            )

            rd.arc(
                (center-radius, center-radius,
                 center+radius, center+radius),
                300, 55,
                fill=(100, 205, 255, 255),
                width=max(2, int(5 * scale))
            )

            rd.arc(
                (center-radius, center-radius,
                 center+radius, center+radius),
                55, 190,
                fill=(224, 82, 255, 210),
                width=max(2, int(4 * scale))
            )

            rim_glow = rim.filter(
                ImageFilter.GaussianBlur(max(2, int(5 * scale)))
            )

            base = Image.alpha_composite(base, rim_glow)
            base = Image.alpha_composite(base, rim)

            # Glossy reflections.
            highlights = Image.new(
                "RGBA", (small, small), (0, 0, 0, 0)
            )
            hd = ImageDraw.Draw(highlights)

            hd.arc(
                (center-radius*.88, center-radius*.88,
                 center+radius*.88, center+radius*.88),
                210, 265,
                fill=(255, 235, 255, 210),
                width=max(2, int(3 * scale))
            )

            highlights = highlights.filter(
                ImageFilter.GaussianBlur(max(1, int(2 * scale)))
            )

            base = Image.alpha_composite(base, highlights)

            # Spherical clipping mask.
            mask = Image.new("L", (small, small), 0)
            md = ImageDraw.Draw(mask)

            md.ellipse(
                (center-radius+1, center-radius+1,
                 center+radius-1, center+radius-1),
                fill=255
            )

            self._orb_static_cache = {
                "size": small,
                "base": base,
                "mask": mask
            }

        # Reuse cached glass artwork.
        base = self._orb_static_cache["base"].copy()
        mask = self._orb_static_cache["mask"]

        # ==========================================
        # ANIMATED ENERGY RIBBONS
        # ==========================================

        palette = [
            (255, 75, 25),
            (255, 143, 45),
            (255, 50, 130),
            (218, 55, 255),
            (116, 91, 255),
            (77, 210, 255),
            (255, 110, 190)
        ]

        energy = Image.new(
            "RGBA", (small, small), (0, 0, 0, 0)
        )
        ed = ImageDraw.Draw(energy)

        for strand in range(7):
            points = []
            count = 220
            offset = strand * 0.89

            for j in range(count):
                t = j / (count - 1) * math.tau

                angle = (
                    t * (1.0 + (strand % 3) * 0.16)
                    + offset
                )

                latitude = (
                    0.47 * math.sin(
                        t * (1.4 + strand * 0.07) + offset
                    )
                    + 0.13 * math.sin(t * 2.5 + offset)
                )

                x3 = 0.82 * math.sin(angle) * math.cos(latitude)
                y3 = 0.82 * math.sin(latitude)
                z3 = 0.82 * math.cos(angle) * math.cos(latitude)

                rotated_x = (
                    x3 * cos_rotation - z3 * sin_rotation
                )

                rotated_z = (
                    x3 * sin_rotation + z3 * cos_rotation
                )

                points.append((
                    center + rotated_x * radius,
                    center + y3 * radius,
                    rotated_z
                ))

            colour = palette[strand % len(palette)]

            thickness = max(
                2, int((7 + strand % 3) * scale)
            )

            for j in range(1, len(points)):
                x1, y1, z1 = points[j - 1]
                x2, y2, z2 = points[j]

                depth = (z1 + z2) / 2

                if depth <= 0.025:
                    continue

                alpha = int(85 + depth * 170)

                ed.line(
                    (x1, y1, x2, y2),
                    fill=(*colour, int(alpha * 0.18)),
                    width=thickness * 2
                )

                ed.line(
                    (x1, y1, x2, y2),
                    fill=(*colour, alpha),
                    width=thickness
                )

                ed.line(
                    (x1, y1, x2, y2),
                    fill=(255, 222, 248, min(255, alpha)),
                    width=max(1, thickness // 3)
                )

        # ==========================================
        # FINE ENERGY TRAILS
        # ==========================================

        fine = Image.new(
            "RGBA", (small, small), (0, 0, 0, 0)
        )
        fd = ImageDraw.Draw(fine)

        for strand in range(2):
            points = []

            for j in range(200):
                t = j / 199 * math.tau

                angle = t * 1.7 + strand * 1.5
                latitude = 0.57 * math.sin(t * 1.8 + strand)

                x3 = 0.85 * math.sin(angle) * math.cos(latitude)
                y3 = 0.85 * math.sin(latitude)
                z3 = 0.85 * math.cos(angle) * math.cos(latitude)

                rotated_x = (
                    x3 * cos_rotation - z3 * sin_rotation
                )

                rotated_z = (
                    x3 * sin_rotation + z3 * cos_rotation
                )

                points.append((
                    center + rotated_x * radius,
                    center + y3 * radius,
                    rotated_z
                ))

            for j in range(1, len(points)):
                x1, y1, z1 = points[j - 1]
                x2, y2, z2 = points[j]

                depth = (z1 + z2) / 2

                if depth <= 0.025:
                    continue

                alpha = int(100 + depth * 150)
                colour = palette[(strand + 2) % len(palette)]

                fd.line(
                    (x1, y1, x2, y2),
                    fill=(*colour, min(255, alpha)),
                    width=max(1, int(2 * scale))
                )

        # Add the fine trails to the main energy layer.
        energy = Image.alpha_composite(energy, fine)

        # ==========================================
        # ENERGY BLOOM AND SPHERICAL CLIPPING
        # ==========================================

        bloom = energy.filter(
            ImageFilter.GaussianBlur(max(1, int(2 * scale)))
        )

        energy = Image.alpha_composite(bloom, energy)

        energy.putalpha(
            Image.composite(
                energy.getchannel("A"),
                Image.new("L", (small, small), 0),
                mask
            )
        )

        # Combine animated energy with cached glass.
        base = Image.alpha_composite(base, energy)

        # ==========================================
        # FINAL IMAGE
        # ==========================================

        result = base.resize(
            (size, size),
            Image.Resampling.LANCZOS
        )

        result = result.filter(
            ImageFilter.UnsharpMask(
                radius=0.8,
                percent=110,
                threshold=4
            )
        )

        return result


        if not PIL_AVAILABLE:
            if not behind:
                canvas.create_text(
                    cx, cy,
                    text="CompAI",
                    fill="#ffffff",
                    font=("Segoe UI", 25, "bold")
                )
            return
        

        word = "CompAI"
        font_size = max(22, int(radius * 0.19))
                # Cache original letter images between animation frames.
        if not hasattr(self, "_orb_glyph_cache"):
            self._orb_glyph_cache = {}

        try:
            font = ImageFont.truetype("segoeuib.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        # Synchronise the lettering with the plasma sphere.
        rotation = -self.phase * 0.65

        # Distance between individual letters around the sphere.
        spacing = 0.235

        for i, char in enumerate(word):

            local_angle = (
                (i - (len(word) - 1) / 2) * spacing
            )
            
            # Use exactly the same 3D rotation as the plasma ribbons.
            x3 = 0.88 * math.sin(local_angle)
            z3 = 0.88 * math.cos(local_angle)

            rotated_x = (
                x3 * math.cos(rotation)
                - z3 * math.sin(rotation)
            )

            depth = (
                x3 * math.sin(rotation)
                + z3 * math.cos(rotation)
            )

            angle = local_angle - rotation

            is_behind = depth <= 0.025

            # Preserve the existing two-layer drawing system.
            if is_behind != behind:
                continue


            x = cx + rotated_x * radius

            # Follow the curvature of the spherical surface.
            y = cy + radius * 0.035 * (1 - depth)

            facing = abs(depth)

            # Compress letters as they turn away from the viewer.
            scale_x = 0.10 + 0.90 * (facing ** 0.85)
            scale_y = 0.84 + 0.16 * facing

            # Reuse cached letter artwork instead of drawing it every frame.
            cache_key = (char, font_size, is_behind)

            glyph = self._orb_glyph_cache.get(cache_key)

            if glyph is None:
                probe = Image.new(
                    "RGBA",
                    (font_size * 3, font_size * 2),
                    (0, 0, 0, 0)
                )

                probe_draw = ImageDraw.Draw(probe)

                bbox = probe_draw.textbbox(
                    (0, 0),
                    char,
                    font=font,
                    stroke_width=2
                )

                glyph_width = max(3, bbox[2] - bbox[0] + 18)
                glyph_height = max(3, bbox[3] - bbox[1] + 18)

                glyph = Image.new(
                    "RGBA",
                    (glyph_width, glyph_height),
                    (0, 0, 0, 0)
                )

                draw = ImageDraw.Draw(glyph)

                ox = 8 - bbox[0]
                oy = 7 - bbox[1]

                if is_behind:
                    draw.text(
                        (ox + 3, oy + 4),
                        char,
                        font=font,
                        fill=(8, 4, 25, 150),
                        stroke_width=3,
                        stroke_fill=(75, 45, 125, 160)
                    )

                    draw.text(
                        (ox, oy),
                        char,
                        font=font,
                        fill=(105, 90, 170, 115),
                        stroke_width=2,
                        stroke_fill=(125, 85, 190, 140)
                    )

                else:
                    draw.text(
                        (ox + 3, oy + 4),
                        char,
                        font=font,
                        fill=(12, 3, 28, 235),
                        stroke_width=4,
                        stroke_fill=(35, 12, 65, 240)
                    )

                    draw.text(
                        (ox, oy),
                        char,
                        font=font,
                        fill=(244, 235, 255, 255),
                        stroke_width=3,
                        stroke_fill=(235, 95, 255, 255)
                    )

                    draw.line(
                        (ox + 2, oy + 2, ox + 10, oy + 2),
                        fill=(255, 255, 255, 230),
                        width=2
                    )

                self._orb_glyph_cache[cache_key] = glyph

            # Work on a copy so the cached original stays unchanged.
            glyph = glyph.copy()


           
            # Apply spherical perspective.
            glyph = glyph.resize(
                (
                    max(2, int(glyph.width * scale_x)),
                    max(2, int(glyph.height * scale_y))
                ),
                Image.Resampling.LANCZOS
            )

            # Slightly tilt each letter around the sphere.
            tilt = -math.sin(angle) * 17

            glyph = glyph.rotate(
                tilt,
                resample=Image.Resampling.BICUBIC,
                expand=True
            )

            photo = ImageTk.PhotoImage(glyph)
            self._orb_text_images.append(photo)

            canvas.create_image(
                x,
                y,
                image=photo,
                anchor="center"
            )


    


    

    
    
    
    def _animate_orb(self):
        if self.closing:
            return

        start_time = time.perf_counter()

        speed = 0.075 if self.visual_state == "idle" else 0.16

        if self.visual_state == "listening":
            speed = 0.22

        self.phase += speed
        self.pulse_phase += 0.12

        self._draw_orb()

        elapsed = time.perf_counter() - start_time

        if not hasattr(self, "_fps_counter"):
            self._fps_counter = 0
            self._fps_timer = time.perf_counter()

        self._fps_counter += 1

        if time.perf_counter() - self._fps_timer >= 2:
            fps = self._fps_counter / (
                time.perf_counter() - self._fps_timer
            )

            print(
                f"CompAI rendering: {fps:.1f} FPS | "
                f"{elapsed * 1000:.1f} ms/frame"
            )

            self._fps_counter = 0
            self._fps_timer = time.perf_counter()

        self.root.after(1, self._animate_orb)

    def _set_visual_state(self, state):
        self.visual_state = state
        self.last_output_time = time.monotonic()
        self._draw_orb()

    # ---------- Existing CompAI backend connection ----------

    def start_backend(self):
        if not BACKEND.exists():
            self._append("ERROR: AI.py was not found beside CompAI_GUI.py.\n", "warning")
            self.connection_label.config(text="● ENGINE NOT FOUND", fg=ORANGE)
            self._set_visual_state("error")
            return

        flags = 0
        if os.name == "nt":
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW

        try:
            self.process = subprocess.Popen(
                [sys.executable, "-u", str(BACKEND)],
                cwd=str(BASE_DIR),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=0,
                creationflags=flags,
            )
            self.connection_label.config(text="● CONNECTED", fg=ACCENT)
            self.footer_status.config(text="● CompAI engine connected", fg=ACCENT)
            self.reader_thread = threading.Thread(
                target=self._reader, daemon=True
            )
            self.reader_thread.start()
        except Exception as exc:
            self._append(f"Could not start CompAI: {exc}\n", "warning")
            self.connection_label.config(text="● OFFLINE", fg=ORANGE)
            self._set_visual_state("error")

    def _reader(self):
        try:
            while self.process and self.process.stdout:
                char = self.process.stdout.read(1)
                if char == "":
                    break
                self.output_queue.put(char)
        except Exception as exc:
            self.output_queue.put(f"\n[Output reader error: {exc}]\n")
        self.output_queue.put("\n[CompAI engine stopped]\n")

    def _drain_output(self):
        if self.closing:
            return
        pieces = []
        try:
            while True:
                pieces.append(self.output_queue.get_nowait())
        except queue.Empty:
            pass

        if pieces:
            output = "".join(pieces)
            self._append(output)

            lower = output.lower()
            if any(word in lower for word in (
                "error:", "not found", "failed", "could not"
            )):
                self._set_visual_state("error")
            elif any(word in lower for word in (
                "listening", "say 'hey computer'", "say hey computer"
            )):
                self._set_visual_state("listening")
            elif any(word in lower for word in (
                "processing", "collecting", "measuring", "starting"
            )):
                self._set_visual_state("processing")
            elif "wake mode stopped" in lower or "wake listening stopped" in lower:
                self._set_visual_state("idle")

        if self.visual_state in ("processing", "error"):
            if time.monotonic() - self.last_output_time > 5:
                self._set_visual_state("idle")

        self.root.after(70, self._drain_output)

    def send_command(self, command):
        if not self.process or self.process.poll() is not None:
            self._append(
                "CompAI is not running. Restart the app to reconnect.\n",
                "warning"
            )
            self._set_visual_state("error")
            return
        try:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
            self._append(f"\nYou: {command}\n", "user")
            self.footer_status.config(text=f"● Sent: {command}", fg=ACCENT)
            self._set_visual_state("processing")
        except Exception as exc:
            self._append(f"Could not send command: {exc}\n", "warning")
            self._set_visual_state("error")

    def send_entry(self):
        value = self.entry.get().strip()
        if not value or value.startswith("Talk to CompAI"):
            return
        self.entry.delete(0, "end")
        self.send_command(value)

    def toggle_wake(self):
        if not self.wake_active:
            self.send_command("wake on")
            self.wake_active = True
            self.wake_button.config(
                text="■  STOP WAKE", bg="#173b65", fg="#ffd08a"
            )
            self.footer_status.config(
                text="● Wake mode requested — say ‘Hey computer’", fg=ACCENT
            )
            self._set_visual_state("listening")
        else:
            # Keep the same stop behaviour as the original GUI.
            try:
                if self.process and os.name == "nt":
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                elif self.process:
                    self.process.send_signal(signal.SIGINT)
            except Exception as exc:
                self._append(f"Could not stop wake mode: {exc}\n", "warning")

            self.wake_active = False
            self.wake_button.config(
                text="◉  WAKE MODE", bg="#17345c", fg=ACCENT
            )
            self.footer_status.config(
                text="● Wake mode stop requested", fg=MUTED
            )
            self._set_visual_state("idle")

    # ---------- Small live system readout ----------

    def _update_metrics(self):
        if self.closing:
            return
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            drive = os.environ.get("SystemDrive", "C:") + "\\"
            disk = psutil.disk_usage(drive).percent
            battery_obj = psutil.sensors_battery()
            battery = f"{battery_obj.percent:.0f}%" if battery_obj else "N/A"
            self.metric_status.config(
                text=f"CPU {cpu:.0f}%   RAM {ram:.0f}%   DISK {disk:.0f}%   BATTERY {battery}"
            )
        except Exception:
            self.metric_status.config(text="CPU —   RAM —   DISK —   BATTERY —")
        self.root.after(3000, self._update_metrics)

    def close(self):
        self.closing = True
        try:
            if self.process and self.process.poll() is None:
                try:
                    self.process.stdin.write("exit\n")
                    self.process.stdin.flush()
                    self.process.wait(timeout=2)
                except Exception:
                    self.process.terminate()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    CompAIGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
