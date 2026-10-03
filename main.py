"""
Decision Spinner - a fun decision-making wheel built with Tkinter.

Run with:  python main.py
"""

import time
import math
import random
import tkinter as tk

# ---------------- Color theme (warm cream + coral / teal) ----------------
BG            = "#F4F1EC"   # app background (warm cream)
PANEL         = "#FFFFFF"   # cards & canvas (white)
PANEL_LIGHT   = "#F7F5F1"   # inputs & result area (soft cream)
TEXT          = "#2A2730"   # primary text (dark slate)
TEXT_DIM      = "#8A8595"   # muted text
ACCENT        = "#FF5A6E"   # primary: SPIN, active pill, pointer, rim
ACCENT_HOVER  = "#FF7A8A"
BTN           = "#ECE7DF"   # secondary buttons (soft beige)
BTN_HOVER     = "#E2DCD2"
SUCCESS       = "#2EC4B6"   # Add button (teal)
SUCCESS_HOVER = "#45D0C3"
RESULT        = "#0E9E8E"   # result text (deep teal)
BORDER        = "#E6E0D6"   # card borders (soft warm)
SHADOW        = "#D9D2C5"   # soft wheel shadow ring
DARK          = "#2A2730"   # dark text on light wheel slices

# Vibrant, cohesive slice colors (cycled around the wheel)
WHEEL_COLORS = [
    "#FF5A6E", "#FFB35C", "#FFD93D", "#A8E063", "#2EC4B6",
    "#4CC9F0", "#5A67D8", "#9B5DE5", "#F15BB5", "#FF8FAB",
    "#80ED99", "#FF9E5C", "#36C9C6", "#F72585",
]

# ---------------- Preset categories ----------------
CATEGORIES = {
    "🍕 Food":    ["Pizza", "Burger", "Biryani", "Pasta", "Shawarma"],
    "🎬 Movies":  ["Inception", "Interstellar", "Up", "Coco", "Joker"],
    "📚 Study":   ["Math", "Physics", "History", "Coding", "Art"],
    "🌤 Weekend": ["Sleep", "Hike", "Movies", "Gaming", "Outing"],
    "🎲 Custom":  [],
}

FONT_FAMILY = "Segoe UI"


class DecisionSpinner:
    def __init__(self, root):
        self.root = root
        self.root.title("Decision Spinner")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)      # maximize / resize enabled
        self.root.minsize(520, 360)

        # App state
        self.options = []
        self.history = []
        self.stats = {name: {} for name in CATEGORIES}   # per-category win counts
        self.current_category = "🍕 Food"
        self.rotation = 0.0          # current wheel rotation (degrees, clockwise)
        self.spinning = False

        # Wheel geometry
        self.canvas_size = 320
        self.cx = self.canvas_size / 2
        self.cy = self.canvas_size / 2
        self.radius = 138

        self._build_scroll_area()
        self._build_ui()
        self._load_category(self.current_category)
        self._center_window()

    # =================== SCROLLABLE AREA ===================
    def _build_scroll_area(self):
        """Create a scrollable container; all UI lives inside self.main."""
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.scroll_canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0, bd=0)
        self.vscroll = tk.Scrollbar(self.root, orient="vertical",
                                    command=self.scroll_canvas.yview)
        self.hscroll = tk.Scrollbar(self.root, orient="horizontal",
                                    command=self.scroll_canvas.xview)
        self.scroll_canvas.configure(yscrollcommand=self.vscroll.set,
                                     xscrollcommand=self.hscroll.set)

        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")
        self.vscroll.grid(row=0, column=1, sticky="ns")
        self.hscroll.grid(row=1, column=0, sticky="ew")

        self.main = tk.Frame(self.scroll_canvas, bg=BG)
        self.main_window = self.scroll_canvas.create_window(
            (0, 0), window=self.main, anchor="nw")

        self.main.bind("<Configure>", self._on_content_configure)
        self.scroll_canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel scrolling (Windows/Mac and Linux)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        self.root.bind_all("<Button-4>", self._on_mousewheel)
        self.root.bind_all("<Button-5>", self._on_mousewheel)

    def _on_content_configure(self, event=None):
        self._update_scroll_layout()

    def _on_canvas_configure(self, event=None):
        self._update_scroll_layout()

    def _update_scroll_layout(self):
        """Make content at least its natural size (or fill the window if bigger)
        and update the scrollable region."""
        cw = self.scroll_canvas.winfo_width()
        ch = self.scroll_canvas.winfo_height()
        rw = self.main.winfo_reqwidth()
        rh = self.main.winfo_reqheight()
        w = max(cw, rw)
        h = max(ch, rh)
        self.scroll_canvas.itemconfigure(self.main_window, width=w, height=h)
        self.scroll_canvas.configure(scrollregion=(0, 0, w, h))

    def _on_mousewheel(self, event):
        if self.scroll_canvas.yview() == (0.0, 1.0):
            return   # everything already visible, nothing to scroll
        if getattr(event, "num", None) == 4:
            d = -1
        elif getattr(event, "num", None) == 5:
            d = 1
        else:
            d = -1 if event.delta > 0 else 1
        self.scroll_canvas.yview_scroll(d, "units")

    # =================== UI BUILDING ===================
    def _build_ui(self):
        # Header
        header = tk.Frame(self.main, bg=BG)
        header.pack(fill="x", padx=30, pady=(14, 2))
        tk.Label(header, text="🎡  Decision Spinner", bg=BG, fg=TEXT,
                 font=(FONT_FAMILY, 26, "bold")).pack()
        tk.Label(header, text="Can't decide? Let the wheel pick for you!  🎯",
                 bg=BG, fg=TEXT_DIM, font=(FONT_FAMILY, 11)).pack(pady=(3, 0))

        # Category pills
        cat_wrap = tk.Frame(self.main, bg=BG)
        cat_wrap.pack(fill="x", padx=30, pady=(6, 8))
        self.cat_buttons = {}
        for name in CATEGORIES:
            b = tk.Button(cat_wrap, text=name, font=(FONT_FAMILY, 11, "bold"),
                          bg=BTN, fg=TEXT, activebackground=BTN, activeforeground=TEXT,
                          relief="flat", bd=0, padx=16, pady=9, cursor="hand2",
                          command=lambda n=name: self._load_category(n))
            b.pack(side="left", padx=5)
            self._add_hover(b, BTN, BTN_HOVER)
            self.cat_buttons[name] = b

        # Main content: wheel (left) + options (right)
        content = tk.Frame(self.main, bg=BG)
        content.pack(fill="both", expand=True, padx=30, pady=(0, 12))
        self._build_wheel_panel(content)
        self._build_options_panel(content)

    def _build_wheel_panel(self, parent):
        panel = tk.Frame(parent, bg=PANEL, bd=0,
                         highlightbackground=BORDER, highlightthickness=1)
        panel.pack(side="left", fill="both", expand=True, padx=(0, 14))

        self.canvas = tk.Canvas(panel, width=self.canvas_size, height=self.canvas_size,
                                bg=PANEL, highlightthickness=0, bd=0)
        self.canvas.pack(padx=20, pady=(14, 8))
        # Redraw once the canvas is mapped so every label shows up on first display.
        self.canvas.bind("<Map>", lambda e: self.draw_wheel())

        # Result card
        result_card = tk.Frame(panel, bg=PANEL_LIGHT, bd=0,
                               highlightbackground=BORDER, highlightthickness=1)
        result_card.pack(fill="x", padx=24, pady=(0, 8))
        self.result_label = tk.Label(result_card, text="Press SPIN to decide!",
                                     bg=PANEL_LIGHT, fg=TEXT_DIM,
                                     font=(FONT_FAMILY, 13), justify="center")
        self.result_label.pack(padx=18, pady=10)

        self.spin_button = tk.Button(panel, text="🎯   SPIN", font=(FONT_FAMILY, 18, "bold"),
                                     bg=ACCENT, fg="white", activebackground=ACCENT_HOVER,
                                     activeforeground="white", relief="flat", bd=0,
                                     width=16, pady=12, cursor="hand2",
                                     command=self.spin_wheel)
        self.spin_button.pack(pady=(2, 14))
        self._add_hover(self.spin_button, ACCENT, ACCENT_HOVER)

    def _build_options_panel(self, parent):
        panel = tk.Frame(parent, bg=PANEL, bd=0,
                         highlightbackground=BORDER, highlightthickness=1, width=300)
        panel.pack(side="right", fill="y", padx=(14, 0))
        panel.pack_propagate(False)

        self._section_title(panel, "OPTIONS")
        self.listbox = tk.Listbox(panel, bg=PANEL_LIGHT, fg=TEXT, selectbackground=ACCENT,
                                  selectforeground="white", relief="flat", bd=0,
                                  highlightbackground=BORDER, highlightthickness=1,
                                  font=(FONT_FAMILY, 11), activestyle="none", height=7)
        self.listbox.pack(fill="x", padx=18, pady=(0, 10))

        # Entry + Add
        entry_row = tk.Frame(panel, bg=PANEL)
        entry_row.pack(fill="x", padx=18)
        self.entry = tk.Entry(entry_row, bg=PANEL_LIGHT, fg=TEXT, insertbackground=TEXT,
                              relief="flat", font=(FONT_FAMILY, 11), bd=0,
                              highlightbackground=BORDER, highlightthickness=1)
        self.entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.entry.bind("<Return>", lambda e: self.add_option())
        add_btn = tk.Button(entry_row, text="Add", font=(FONT_FAMILY, 10, "bold"),
                            bg=SUCCESS, fg="white", relief="flat", bd=0, padx=14,
                            cursor="hand2", command=self.add_option)
        add_btn.pack(side="left", padx=(8, 0), ipady=7)
        self._add_hover(add_btn, SUCCESS, SUCCESS_HOVER)

        # Remove + Reset
        btn_row = tk.Frame(panel, bg=PANEL)
        btn_row.pack(fill="x", padx=18, pady=10)
        rm = tk.Button(btn_row, text="Remove", font=(FONT_FAMILY, 10, "bold"),
                       bg=BTN, fg=TEXT, relief="flat", bd=0, cursor="hand2",
                       command=self.remove_option)
        rm.pack(side="left", fill="x", expand=True, ipadx=4, ipady=7)
        rs = tk.Button(btn_row, text="Reset", font=(FONT_FAMILY, 10, "bold"),
                       bg=BTN, fg=TEXT, relief="flat", bd=0, cursor="hand2",
                       command=self.reset_options)
        rs.pack(side="left", padx=(8, 0), fill="x", expand=True, ipadx=4, ipady=7)
        self._add_hover(rm, BTN, BTN_HOVER)
        self._add_hover(rs, BTN, BTN_HOVER)

        # History
        self._section_title(panel, "RECENT RESULTS", pady=(8, 6))
        self.history_box = tk.Listbox(panel, bg=PANEL_LIGHT, fg=TEXT_DIM,
                                      selectbackground=BTN, selectforeground=TEXT,
                                      relief="flat", bd=0, highlightbackground=BORDER,
                                      highlightthickness=1, font=(FONT_FAMILY, 10),
                                      activestyle="none", height=5)
        self.history_box.pack(fill="x", padx=18, pady=(0, 8))

        clr = tk.Button(panel, text="Clear History", font=(FONT_FAMILY, 10),
                        bg=BTN, fg=TEXT_DIM, relief="flat", bd=0, cursor="hand2",
                        command=self.clear_history)
        clr.pack(padx=18, pady=(0, 8), ipadx=8, ipady=5)
        self._add_hover(clr, BTN, BTN_HOVER)

        # Clear Stats (resets the percentages shown on the wheel)
        clr_stats = tk.Button(panel, text="Clear Stats", font=(FONT_FAMILY, 10),
                              bg=BTN, fg=TEXT_DIM, relief="flat", bd=0, cursor="hand2",
                              command=self.clear_stats)
        clr_stats.pack(padx=18, pady=(0, 20), ipadx=8, ipady=5)
        self._add_hover(clr_stats, BTN, BTN_HOVER)

    def _section_title(self, parent, text, pady=(18, 8)):
        """Small accent-colored section header with a short underline bar."""
        wrap = tk.Frame(parent, bg=PANEL)
        wrap.pack(fill="x", padx=18, pady=pady)
        tk.Label(wrap, text=text, bg=PANEL, fg=TEXT,
                 font=(FONT_FAMILY, 12, "bold")).pack(side="left")
        tk.Frame(wrap, bg=ACCENT, height=2).pack(side="left", padx=8, ipadx=10, pady=6)

    # =================== HELPERS ===================
    def _add_hover(self, btn, normal, hover):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal))

    def _center_window(self):
        """Size the window to its content, but never bigger than the screen,
        then center it. Anything that doesn't fit can be scrolled."""
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        sb_w = self.vscroll.winfo_reqwidth()
        sb_h = self.hscroll.winfo_reqheight()

        want_w = self.main.winfo_reqwidth() + sb_w
        want_h = self.main.winfo_reqheight() + sb_h

        w = min(want_w, sw - 40)
        h = min(want_h, sh - 100)    # leave room for taskbar + title bar
        x = (sw - w) // 2
        y = max(10, (sh - h) // 2 - 20)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # =================== CATEGORIES ===================
    def _load_category(self, name):
        if self.spinning:
            return
        self.current_category = name
        self.options = list(CATEGORIES[name])
        # Highlight the active pill, dim the rest
        for n, b in self.cat_buttons.items():
            if n == name:
                b.config(bg=ACCENT)
                b.unbind("<Enter>"); b.unbind("<Leave>")
                self._add_hover(b, ACCENT, ACCENT_HOVER)
            else:
                b.config(bg=BTN)
                b.unbind("<Enter>"); b.unbind("<Leave>")
                self._add_hover(b, BTN, BTN_HOVER)
        self._refresh_listbox()
        self.draw_wheel()
        self._set_result_idle()

    def _refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for opt in self.options:
            self.listbox.insert(tk.END, opt)

    def _set_result_idle(self):
        if len(self.options) < 2:
            self.result_label.config(text="Add at least 2 options to spin! 🙃",
                                     fg=ACCENT, font=(FONT_FAMILY, 12, "bold"))
        else:
            self.result_label.config(text="Press SPIN to decide!", fg=TEXT_DIM,
                                     font=(FONT_FAMILY, 13))

    # =================== STATS ===================
    def _stat_text(self, option):
        """Percentage text shown under the option name on the wheel.
        Empty string until at least one spin has happened."""
        counts = self.stats[self.current_category]
        total = sum(counts.get(o, 0) for o in self.options)
        if total == 0:
            return ""
        return f"{counts.get(option, 0) / total * 100:.0f}%"

    def clear_stats(self):
        if self.spinning:
            return
        self.stats[self.current_category] = {}
        self.draw_wheel()

    # =================== OPTIONS ===================
    def add_option(self):
        if self.spinning:
            return
        val = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        if not val:
            return
        if val.lower() in (o.lower() for o in self.options):
            self.result_label.config(text=f"'{val}' already hai list mein!",
                                     fg=ACCENT, font=(FONT_FAMILY, 12, "bold"))
            return
        self.options.append(val)
        self._refresh_listbox()
        self.draw_wheel()
        self._set_result_idle()

    def remove_option(self):
        if self.spinning:
            return
        sel = self.listbox.curselection()
        if not sel:
            return
        del self.options[sel[0]]
        self._refresh_listbox()
        self.draw_wheel()
        self._set_result_idle()

    def reset_options(self):
        if self.spinning:
            return
        self.options = list(CATEGORIES[self.current_category])
        self._refresh_listbox()
        self.draw_wheel()
        self._set_result_idle()

    # =================== WHEEL DRAWING ===================
    def draw_wheel(self):
        """Redraw the whole wheel at the current rotation.

        Angle convention used everywhere in this class: CLOCKWISE from the
        3 o'clock position, in screen coordinates (y points down). Tkinter's
        create_arc uses counter-clockwise angles, so we convert only when
        calling create_arc.
        """
        self.canvas.delete("all")
        cx, cy, r = self.cx, self.cy, self.radius
        n = len(self.options)

        # Soft shadow ring + colorful rim around the wheel
        self.canvas.create_oval(cx - r - 11, cy - r - 11, cx + r + 11, cy + r + 11,
                                outline=SHADOW, width=5)
        self.canvas.create_oval(cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4,
                                outline=ACCENT, width=3)

        if n == 0:
            self.canvas.create_text(cx, cy, text="No options yet",
                                    fill=TEXT_DIM, font=(FONT_FAMILY, 12))
            self._draw_pointer()
            return

        slice_angle = 360 / n
        labels = []   # collect labels, draw them AFTER all slices

        # 1) Draw all slices first
        for i in range(n):
            # Clockwise start angle of this slice
            start_cw = i * slice_angle + self.rotation
            color = WHEEL_COLORS[i % len(WHEEL_COLORS)]

            # Convert clockwise -> Tk's counter-clockwise arc start
            tk_start = -(start_cw + slice_angle)
            self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                   start=tk_start, extent=slice_angle,
                                   fill=color, outline=PANEL, width=2, style="pieslice")

            # Prepare label (clockwise mid angle, half width of the slice)
            mid = start_cw + slice_angle / 2
            half = slice_angle / 2
            extra = self._stat_text(self.options[i])   # e.g. "40%" (or "")
            lines, fs, lx, ly = self._place_label(self.options[i], mid, half, r, extra)
            labels.append((lines, fs, lx, ly, color))

        # 2) Draw all labels on top so no slice can cover them
        for lines, fs, lx, ly, color in labels:
            self.canvas.create_text(lx, ly, text="\n".join(lines),
                                    fill=self._text_color_for(color),
                                    font=(FONT_FAMILY, fs, "bold"),
                                    justify="center")

        # Center hub
        self.canvas.create_oval(cx - 18, cy - 18, cx + 18, cy + 18,
                                fill=PANEL, outline=ACCENT, width=3)
        self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                                fill=ACCENT, outline="")
        # Fixed pointer at the top (drawn last so it sits on top)
        self._draw_pointer()

    # ----- label-fitting helpers -----
    def _in_wedge(self, x, y, theta, alpha, r_max):
        """True if point (x, y) lies inside the wedge (mid=theta, half-width=alpha)
        and within radius r_max of the wheel center."""
        dx, dy = x - self.cx, y - self.cy
        dist = math.hypot(dx, dy)
        if dist > r_max:
            return False
        if dist < 1e-6:
            return True
        ang = math.degrees(math.atan2(dy, dx)) % 360
        lo = (theta - alpha) % 360
        hi = (theta + alpha) % 360
        return lo <= ang <= hi if lo <= hi else (ang >= lo or ang <= hi)

    def _half_width(self, px, py, theta, alpha, r_max):
        """Largest horizontal half-width about (px, py) that stays in the wedge."""
        hw = 0.0
        while self._in_wedge(px + hw + 2, py, theta, alpha, r_max) and \
              self._in_wedge(px - (hw + 2), py, theta, alpha, r_max):
            hw += 2
            if hw > 220:
                break
        return hw

    def _box_in_wedge(self, px, py, w, h, theta, alpha, r_max):
        """True if a w x h box centered at (px, py) fits entirely in the wedge."""
        for sx in (-1, 1):
            for sy in (-1, 1):
                if not self._in_wedge(px + sx * w / 2, py + sy * h / 2,
                                      theta, alpha, r_max):
                    return False
        return True

    def _wrap_label(self, label, fs, max_w):
        """Split label into lines that fit max_w; single line if it can't wrap."""
        def wlen(s):
            return len(s) * fs * 0.7
        if wlen(label) <= max_w:
            return [label]
        words = label.split()
        if len(words) >= 2:
            best = None
            for k in range(1, len(words)):
                l1, l2 = " ".join(words[:k]), " ".join(words[k:])
                width = max(wlen(l1), wlen(l2))
                if best is None or width < best[0]:
                    best = (width, l1, l2)
            if best and best[0] <= max_w:
                return [best[1], best[2]]
        return [label]

    def _place_label(self, label, theta, alpha, r, extra=""):
        """Pick a font size, radius and wrap so the text fits inside its slice.
        'extra' is an optional extra line (the percentage) shown under the label.
        Returns (lines, font_size, x, y)."""
        r_max = r - 12          # keep clear of the rim
        inner = 26             # keep clear of the center hub
        a = math.radians(alpha)
        # The wedge's centroid radius is a natural "center" for the text.
        centroid = (2 * r * math.sin(a)) / (3 * a) if a > 0 else r * 0.6
        radii = []
        for cand in (centroid, 0.55 * r, 0.45 * r, 0.64 * r):
            if inner <= cand <= r_max and round(cand, 1) not in radii:
                radii.append(round(cand, 1))

        # Largest font first, then preferred radii -> biggest readable text.
        for fs in range(13, 6, -1):
            for rho in radii:
                px = self.cx + rho * math.cos(math.radians(theta))
                py = self.cy + rho * math.sin(math.radians(theta))
                max_w = max(8, 2 * self._half_width(px, py, theta, alpha, r_max) - 6)
                lines = self._wrap_label(label, fs, max_w)
                if extra:
                    lines = lines + [extra]
                box_w = max(len(l) for l in lines) * fs * 0.7
                box_h = len(lines) * fs * 1.25
                if self._box_in_wedge(px, py, box_w, box_h, theta, alpha, r_max):
                    return lines, fs, px, py

        # Fallback: smallest font, truncated to whatever width is available.
        rho = radii[0] if radii else 0.55 * r
        px = self.cx + rho * math.cos(math.radians(theta))
        py = self.cy + rho * math.sin(math.radians(theta))
        max_w = max(8, 2 * self._half_width(px, py, theta, alpha, r_max) - 6)
        max_chars = max(2, int(max_w / (7 * 0.7)) - 1)
        lines = [label[:max_chars] + "…"]
        if extra:
            lines.append(extra)
        return lines, 7, px, py

    def _text_color_for(self, hexcolor):
        """Dark text on light slices (e.g. yellow), white text on dark slices."""
        r = int(hexcolor[1:3], 16)
        g = int(hexcolor[3:5], 16)
        b = int(hexcolor[5:7], 16)
        return DARK if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "white"

    def _draw_pointer(self):
        cx = self.cx
        top = self.cy - self.radius
        self.canvas.create_polygon(cx, top + 24, cx - 14, top - 8, cx + 14, top - 8,
                                   fill=ACCENT, outline="white", width=2)

    # =================== SPIN LOGIC ===================
    def spin_wheel(self):
        if self.spinning:
            return
        if len(self.options) < 2:
            self._set_result_idle()
            return

        self.spinning = True
        self.spin_button.config(state="disabled", bg=BTN)
        self.result_label.config(text="Spinning… 🌀", fg=TEXT, font=(FONT_FAMILY, 13))

        n = len(self.options)
        slice_angle = 360 / n

        # 1) Randomly pick the winning option.
        target = random.randint(0, n - 1)

        # 2) Work out the final rotation that puts 'target' under the pointer.
        #    The pointer sits at the top = 270 deg in the clockwise system.
        #    Slice i covers [i*slice_angle, (i+1)*slice_angle) before rotation,
        #    so its center is (i + 0.5) * slice_angle. We solve for the rotation
        #    that makes (center + rotation) land on 270.
        jitter = random.uniform(-slice_angle * 0.3, slice_angle * 0.3)  # natural stop
        center = target * slice_angle + slice_angle / 2 + jitter
        delta = (270 - center) % 360                  # rotation (mod 360) hitting target
        step = (delta - self.rotation % 360) % 360    # forward distance to reach delta
        spins = random.randint(5, 8)                  # extra full turns for effect
        self.target_rotation = self.rotation + step + 360 * spins
        self.target_index = target

        # 3) Animate from current rotation to target_rotation (ease-out).
        self.start_rotation = self.rotation
        self.spin_start_time = time.perf_counter()
        self.spin_duration = 4200  # milliseconds
        self.animate_spin()

    def animate_spin(self):
        """Advance the wheel one frame using an ease-out curve, then schedule the next."""
        elapsed = (time.perf_counter() - self.spin_start_time) * 1000
        t = elapsed / self.spin_duration

        if t >= 1:
            # Finished: snap exactly to target and reveal the result.
            self.rotation = self.target_rotation
            self.draw_wheel()
            self.spinning = False
            self.spin_button.config(state="normal", bg=ACCENT)
            self.show_result()
            return

        # Ease-out cubic: fast at first, gradually slowing down.
        ease = 1 - (1 - t) ** 3
        self.rotation = self.start_rotation + (self.target_rotation - self.start_rotation) * ease
        self.draw_wheel()
        self.root.after(16, self.animate_spin)  # ~60 FPS, keeps the GUI responsive

    def show_result(self):
        result = self.options[self.target_index]
        self.result_label.config(text=f"🎉  Your decision is...\n{result}!",
                                 fg=RESULT, font=(FONT_FAMILY, 20, "bold"))
        # Update recent history (keep last 5)
        self.history.insert(0, result)
        self.history = self.history[:5]
        self.history_box.delete(0, tk.END)
        for h in self.history:
            self.history_box.insert(tk.END, h)

        # Update stats (count how many times this option was chosen)
        counts = self.stats[self.current_category]
        counts[result] = counts.get(result, 0) + 1
        self.draw_wheel()      # redraw so the new percentages show on the wheel

    def clear_history(self):
        self.history = []
        self.history_box.delete(0, tk.END)


def main():
    root = tk.Tk()
    DecisionSpinner(root)
    root.mainloop()


if __name__ == "__main__":
    main()