"""
Keyboard visualizer component for TypeMaster.
Provides a real-time virtual keyboard highlighting the next target key and suggesting the optimal finger.
"""
import tkinter as tk
import customtkinter as ctk
from services.i18n_service import t
from ui.theme import THEMES

# Map characters and symbols to their physical key caps on a US English layout
# Map characters and symbols to their physical key caps on a US English layout
KEY_MAP = {
    '~': '`', '`': '`',
    '1': '1', '!': '1',
    '2': '2', '@': '2',
    '3': '3', '#': '3',
    '4': '4', '$': '4',
    '5': '5', '%': '5',
    '6': '6', '^': '6',
    '7': '7', '&': '7',
    '8': '8', '*': '8',
    '9': '9', '(': '9',
    '0': '0', ')': '0',
    '-': '-', '_': '-',
    '=': '=', '+': '=',
    
    'q': 'Q', 'Q': 'Q',
    'w': 'W', 'W': 'W',
    'e': 'E', 'E': 'E',
    'r': 'R', 'R': 'R',
    't': 'T', 'T': 'T',
    'y': 'Y', 'Y': 'Y',
    'u': 'U', 'U': 'U',
    'i': 'I', 'I': 'I',
    'o': 'O', 'O': 'O',
    'p': 'P', 'P': 'P',
    '[': '[', '{': '[',
    ']': ']', '}': ']',
    '\\': '\\', '|': '\\',
    
    'a': 'A', 'A': 'A',
    's': 'S', 'S': 'S',
    'd': 'D', 'D': 'D',
    'f': 'F', 'F': 'F',
    'g': 'G', 'G': 'G',
    'h': 'H', 'H': 'H',
    'j': 'J', 'J': 'J',
    'k': 'K', 'K': 'K',
    'l': 'L', 'L': 'L',
    ';': ';', ':': ';',
    "'": "'", '"': "'",
    
    'z': 'Z', 'Z': 'Z',
    'x': 'X', 'X': 'X',
    'c': 'C', 'C': 'C',
    'v': 'V', 'V': 'V',
    'b': 'B', 'B': 'B',
    'n': 'N', 'N': 'N',
    'm': 'M', 'M': 'M',
    ',': ',', '<': ',',
    '.': '.', '>': '.',
    '/': '/', '?': '/',
    
    ' ': 'SPACE', '\n': 'ENTER',
    
    # Russian Cyrillic JCUKEN mapping
    'ё': '`', 'Ё': '`',
    'й': 'Q', 'Й': 'Q',
    'ц': 'W', 'Ц': 'W',
    'у': 'E', 'У': 'E',
    'к': 'R', 'К': 'R',
    'е': 'T', 'Е': 'T',
    'н': 'Y', 'Н': 'Y',
    'г': 'U', 'Г': 'U',
    'ш': 'I', 'Ш': 'I',
    'щ': 'O', 'Щ': 'O',
    'з': 'P', 'З': 'P',
    'х': '[', 'Х': '[',
    'ъ': ']', 'Ъ': ']',
    'ф': 'A', 'Ф': 'A',
    'ы': 'S', 'Ы': 'S',
    'в': 'D', 'В': 'D',
    'а': 'F', 'А': 'F',
    'п': 'G', 'П': 'G',
    'р': 'H', 'Р': 'H',
    'о': 'J', 'О': 'J',
    'л': 'K', 'Л': 'K',
    'д': 'L', 'Д': 'L',
    'ж': ';', 'Ж': ';',
    'э': "'", 'Э': "'",
    'я': 'Z', 'Я': 'Z',
    'ч': 'X', 'Ч': 'X',
    'с': 'C', 'С': 'C',
    'м': 'V', 'М': 'V',
    'и': 'B', 'И': 'B',
    'т': 'N', 'Т': 'N',
    'ь': 'M', 'Ь': 'M',
    'б': ',', 'Б': ',',
    'ю': '.', 'Ю': '.',
    '№': '3'
}

# Mapping characters to specific recommended fingers (using key names matching i18n_service)
FINGER_MAP = {
    # Left Pinky
    '`': 'finger_left_pinky', '~': 'finger_left_pinky',
    '1': 'finger_left_pinky', '!': 'finger_left_pinky',
    'q': 'finger_left_pinky', 'Q': 'finger_left_pinky',
    'a': 'finger_left_pinky', 'A': 'finger_left_pinky',
    'z': 'finger_left_pinky', 'Z': 'finger_left_pinky',
    'ё': 'finger_left_pinky', 'Ё': 'finger_left_pinky',
    'й': 'finger_left_pinky', 'Й': 'finger_left_pinky',
    'ф': 'finger_left_pinky', 'Ф': 'finger_left_pinky',
    'я': 'finger_left_pinky', 'Я': 'finger_left_pinky',
    
    # Left Ring
    '2': 'finger_left_ring', '@': 'finger_left_ring',
    'w': 'finger_left_ring', 'W': 'finger_left_ring',
    's': 'finger_left_ring', 'S': 'finger_left_ring',
    'x': 'finger_left_ring', 'X': 'finger_left_ring',
    'ц': 'finger_left_ring', 'Ц': 'finger_left_ring',
    'ы': 'finger_left_ring', 'Ы': 'finger_left_ring',
    'ч': 'finger_left_ring', 'Ч': 'finger_left_ring',
    
    # Left Middle
    '3': 'finger_left_middle', '#': 'finger_left_middle',
    'e': 'finger_left_middle', 'E': 'finger_left_middle',
    'd': 'finger_left_middle', 'D': 'finger_left_middle',
    'c': 'finger_left_middle', 'C': 'finger_left_middle',
    '№': 'finger_left_middle',
    'у': 'finger_left_middle', 'У': 'finger_left_middle',
    'в': 'finger_left_middle', 'В': 'finger_left_middle',
    'с': 'finger_left_middle', 'С': 'finger_left_middle',
    
    # Left Index
    '4': 'finger_left_index', '$': 'finger_left_index',
    '5': 'finger_left_index', '%': 'finger_left_index',
    'r': 'finger_left_index', 'R': 'finger_left_index',
    't': 'finger_left_index', 'T': 'finger_left_index',
    'f': 'finger_left_index', 'F': 'finger_left_index',
    'g': 'finger_left_index', 'G': 'finger_left_index',
    'v': 'finger_left_index', 'V': 'finger_left_index',
    'b': 'finger_left_index', 'B': 'finger_left_index',
    'к': 'finger_left_index', 'К': 'finger_left_index',
    'е': 'finger_left_index', 'Е': 'finger_left_index',
    'а': 'finger_left_index', 'А': 'finger_left_index',
    'п': 'finger_left_index', 'П': 'finger_left_index',
    'м': 'finger_left_index', 'М': 'finger_left_index',
    'и': 'finger_left_index', 'И': 'finger_left_index',
    
    # Thumbs (Spacebar)
    ' ': 'finger_thumb',
    
    # Right Index
    '6': 'finger_right_index', '^': 'finger_right_index',
    '7': 'finger_right_index', '&': 'finger_right_index',
    'y': 'finger_right_index', 'Y': 'finger_right_index',
    'u': 'finger_right_index', 'U': 'finger_right_index',
    'h': 'finger_right_index', 'H': 'finger_right_index',
    'j': 'finger_right_index', 'J': 'finger_right_index',
    'n': 'finger_right_index', 'N': 'finger_right_index',
    'm': 'finger_right_index', 'M': 'finger_right_index',
    'н': 'finger_right_index', 'Н': 'finger_right_index',
    'г': 'finger_right_index', 'Г': 'finger_right_index',
    'р': 'finger_right_index', 'Р': 'finger_right_index',
    'о': 'finger_right_index', 'О': 'finger_right_index',
    'т': 'finger_right_index', 'Т': 'finger_right_index',
    'ь': 'finger_right_index', 'Ь': 'finger_right_index',
    
    # Right Middle
    '8': 'finger_right_middle', '*': 'finger_right_middle',
    'i': 'finger_right_middle', 'I': 'finger_right_middle',
    'k': 'finger_right_middle', 'K': 'finger_right_middle',
    ',': 'finger_right_middle', '<': 'finger_right_middle',
    'ш': 'finger_right_middle', 'Ш': 'finger_right_middle',
    'л': 'finger_right_middle', 'Л': 'finger_right_middle',
    'б': 'finger_right_middle', 'Б': 'finger_right_middle',
    
    # Right Ring
    '9': 'finger_right_ring', '(': 'finger_right_ring',
    'o': 'finger_right_ring', 'O': 'finger_right_ring',
    'l': 'finger_right_ring', 'L': 'finger_right_ring',
    '.': 'finger_right_ring', '>': 'finger_right_ring',
    'щ': 'finger_right_ring', 'Щ': 'finger_right_ring',
    'д': 'finger_right_ring', 'Д': 'finger_right_ring',
    'ю': 'finger_right_ring', 'Ю': 'finger_right_ring',
    
    # Right Pinky
    '0': 'finger_right_pinky', ')': 'finger_right_pinky',
    '-': 'finger_right_pinky', '_': 'finger_right_pinky',
    '=': 'finger_right_pinky', '+': 'finger_right_pinky',
    'p': 'finger_right_pinky', 'P': 'finger_right_pinky',
    '[': 'finger_right_pinky', '{': 'finger_right_pinky',
    ']': 'finger_right_pinky', '}': 'finger_right_pinky',
    '\\': 'finger_right_pinky', '|': 'finger_right_pinky',
    ';': 'finger_right_pinky', ':': 'finger_right_pinky',
    "'": 'finger_right_pinky', '"': 'finger_right_pinky',
    '/': 'finger_right_pinky', '?': 'finger_right_pinky',
    '\n': 'finger_right_pinky',
    'з': 'finger_right_pinky', 'З': 'finger_right_pinky',
    'х': 'finger_right_pinky', 'Х': 'finger_right_pinky',
    'ъ': 'finger_right_pinky', 'Ъ': 'finger_right_pinky',
    'ж': 'finger_right_pinky', 'Ж': 'finger_right_pinky',
    'э': 'finger_right_pinky', 'Э': 'finger_right_pinky'
}

# Left-hand typed characters list to help decide shift finger
LEFT_HAND_CHARS = set("`~1!2@3#4$5%qQwWeErRtTfasdDFgGzZxXcCvVbBёЁйЙцЦуУкКеЕфФыЫвВаАпПяЯчЧсСмМиИ")

RU_LABELS = {
    "`": "Ё", "1": "1 !", "2": "2 \"", "3": "3 №", "4": "4 ;",
    "5": "5 %", "6": "6 :", "7": "7 ?", "8": "8 *", "9": "9 (", "0": "0 )",
    "Q": "Й", "W": "Ц", "E": "У", "R": "К", "T": "Е", "Y": "Н", "U": "Г", "I": "Ш", "O": "Щ", "P": "З",
    "[": "Х", "]": "Ъ", "A": "Ф", "S": "Ы", "D": "В", "F": "А", "G": "П", "H": "Р", "J": "О", "K": "Л",
    "L": "Д", ";": "Ж", "'": "Э", "Z": "Я", "X": "Ч", "C": "С", "V": "М", "B": "И", "N": "Т", "M": "Ь",
    ",": "Б", ".": "Ю", "/": ". ,"
}
EN_LABELS = {
    "`": "` ~", "1": "1 !", "2": "2 @", "3": "3 #", "4": "4 $",
    "5": "5 %", "6": "6 ^", "7": "7 &", "8": "8 *", "9": "9 (", "0": "0 )",
    "Q": "Q", "W": "W", "E": "E", "R": "R", "T": "T", "Y": "Y", "U": "U", "I": "I", "O": "O", "P": "P",
    "[": "[ {", "]": "] }", "A": "A", "S": "S", "D": "D", "F": "F", "G": "G", "H": "H", "J": "J", "K": "K",
    "L": "L", ";": "; :", "'": "' \"", "Z": "Z", "X": "X", "C": "C", "V": "V", "B": "B", "N": "N", "M": "M",
    ",": ", <", ".": ". >", "/": "/ ?"
}

class KeyboardVisualizer(ctk.CTkFrame):
    """
    Virtual keyboard visual tutor rendering.
    Highlights next keys + opposite shifts when required, shows a Finger Canvas (Hands Guide),
    and animates physical key presses in real time.
    """
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller
        self.current_theme = getattr(controller, "current_theme", "dark")
        self.practice_language = "English"
        
        self.key_widgets = {}
        self.finger_shapes = {}
        self.highlighted_keys = []
        self.next_char = None
        
        self._setup_ui()
        
    def set_practice_language(self, lang):
        self.practice_language = lang
        self.update_key_labels()
        
    def update_key_labels(self):
        is_russian = False
        if hasattr(self, "practice_language") and self.practice_language:
            is_russian = self.practice_language.lower() in ("russian", "ruscha", "rus")
            
        labels_map = RU_LABELS if is_russian else EN_LABELS
        for k_id, widget in self.key_widgets.items():
            if k_id in labels_map:
                widget.configure(text=labels_map[k_id])
                
    def _setup_ui(self):
        # 1. Feedback/Tip Info Label
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(fill=tk.X, pady=(0, 2))
        
        self.tip_lbl = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=("Segoe UI", 12, "bold")
        )
        self.tip_lbl.pack(anchor="center")
        
        # 1.5. Visual Hand Canvas
        theme_colors = THEMES.get(self.current_theme, THEMES["dark"])
        self.hand_canvas = tk.Canvas(
            self,
            width=300,
            height=100,
            highlightthickness=0,
            bg=theme_colors["bg"]
        )
        self.hand_canvas.pack(anchor="center", pady=(0, 5))
        
        # 2. Keyboard frame
        self.kbd_container = ctk.CTkFrame(self)
        self.kbd_container.pack(anchor="center", padx=10, pady=5)
        
        # Build Rows
        row_layouts = [
            # Row 1: Esc/Function rows are skipped. Main numbers
            [("`", "` ~", 32), ("1", "1 !", 32), ("2", "2 @", 32), ("3", "3 #", 32), ("4", "4 $", 32),
             ("5", "5 %", 32), ("6", "6 ^", 32), ("7", "7 &", 32), ("8", "8 *", 32), ("9", "9 (", 32),
             ("0", "0 )", 32), ("-", "- _", 32), ("=", "= +", 32), ("BACKSPACE", "← Backspace", 75)],
            
            # Row 2
            [("TAB", "Tab ↹", 50), ("Q", "Q", 32), ("W", "W", 32), ("E", "E", 32), ("R", "R", 32),
             ("T", "T", 32), ("Y", "Y", 32), ("U", "U", 32), ("I", "I", 32), ("O", "O", 32),
             ("P", "P", 32), ("[", "[ {", 32), ("]", "] }", 32), ("\\", "\\ |", 50)],
            
            # Row 3
            [("CAPS", "Caps", 56), ("A", "A", 32), ("S", "S", 32), ("D", "D", 32), ("F", "F", 32),
             ("G", "G", 32), ("H", "H", 32), ("J", "J", 32), ("K", "K", 32), ("L", "L", 32),
             (";", "; :", 32), ("'", "' \"", 32), ("ENTER", "Enter ↵", 66)],
            
            # Row 4
            [("LSHIFT", "Shift ⇧", 76), ("Z", "Z", 32), ("X", "X", 32), ("C", "C", 32), ("V", "V", 32),
             ("B", "B", 32), ("N", "N", 32), ("M", "M", 32), (",", ", <", 32), (".", ". >", 32),
             ("/", "/ ?", 32), ("RSHIFT", "Shift ⇧", 76)],
             
            # Row 5
            [("SPACE", "Spacebar", 260)]
        ]
        
        for r_idx, row in enumerate(row_layouts):
            row_frame = ctk.CTkFrame(self.kbd_container, fg_color="transparent")
            row_frame.pack(fill=tk.X, pady=2, padx=4)
            for k_id, k_txt, width in row:
                key_lbl = ctk.CTkLabel(
                    row_frame,
                    text=k_txt,
                    width=width,
                    height=32,
                    corner_radius=6,
                    font=("Segoe UI", 10, "bold")
                )
                key_lbl.pack(side=tk.LEFT, padx=2)
                self.key_widgets[k_id] = key_lbl
                
        self.apply_theme(self.current_theme)

    def _draw_hands(self):
        self.hand_canvas.delete("all")
        theme_colors = THEMES.get(self.current_theme, THEMES["dark"])
        
        # Color palettes
        canvas_bg = theme_colors["bg"]
        palm_color = theme_colors["card_bg"]
        border_color = theme_colors["border"]
        finger_color = self._get_normal_finger_fg()
        
        self.hand_canvas.configure(bg=canvas_bg)
        
        # Left Hand Palm (Kaft)
        self.hand_canvas.create_polygon(
            20, 80, 30, 50, 95, 50, 105, 80, 80, 95, 35, 95,
            fill=palm_color, outline=border_color, width=1.5, tags="left_palm"
        )
        
        # Left Hand Fingers
        # Pinky
        self.finger_shapes["finger_left_pinky"] = self.hand_canvas.create_line(
            35, 50, 35, 20, width=9, capstyle="round", fill=finger_color
        )
        # Ring
        self.finger_shapes["finger_left_ring"] = self.hand_canvas.create_line(
            50, 47, 50, 10, width=9, capstyle="round", fill=finger_color
        )
        # Middle
        self.finger_shapes["finger_left_middle"] = self.hand_canvas.create_line(
            65, 45, 65, 5, width=9, capstyle="round", fill=finger_color
        )
        # Index
        self.finger_shapes["finger_left_index"] = self.hand_canvas.create_line(
            80, 47, 80, 12, width=9, capstyle="round", fill=finger_color
        )
        # Thumb
        self.finger_shapes["finger_left_thumb"] = self.hand_canvas.create_line(
            95, 60, 115, 43, width=9, capstyle="round", fill=finger_color
        )
        
        # Right Hand Palm (Kaft)
        self.hand_canvas.create_polygon(
            195, 80, 205, 50, 270, 50, 280, 80, 265, 95, 220, 95,
            fill=palm_color, outline=border_color, width=1.5, tags="right_palm"
        )
        
        # Right Hand Fingers
        # Thumb
        self.finger_shapes["finger_right_thumb"] = self.hand_canvas.create_line(
            205, 60, 185, 43, width=9, capstyle="round", fill=finger_color
        )
        # Index
        self.finger_shapes["finger_right_index"] = self.hand_canvas.create_line(
            220, 47, 220, 12, width=9, capstyle="round", fill=finger_color
        )
        # Middle
        self.finger_shapes["finger_right_middle"] = self.hand_canvas.create_line(
            235, 45, 235, 5, width=9, capstyle="round", fill=finger_color
        )
        # Ring
        self.finger_shapes["finger_right_ring"] = self.hand_canvas.create_line(
            250, 47, 250, 10, width=9, capstyle="round", fill=finger_color
        )
        # Pinky
        self.finger_shapes["finger_right_pinky"] = self.hand_canvas.create_line(
            265, 50, 265, 20, width=9, capstyle="round", fill=finger_color
        )

    def highlight_key(self, char):
        """
        Main interface method. Highlights next key cap and recommended finger on visual hands.
        """
        self.next_char = char
        
        # Clean current highlighted keys
        for k_id in self.highlighted_keys:
            if k_id in self.key_widgets:
                self.key_widgets[k_id].configure(
                    fg_color=self._get_normal_key_bg(),
                    text_color=self._get_normal_key_fg()
                )
        self.highlighted_keys.clear()
        
        # Reset finger lines color in Hand Canvas
        normal_finger_color = self._get_normal_finger_fg()
        for f_shape in self.finger_shapes.values():
            self.hand_canvas.itemconfig(f_shape, fill=normal_finger_color)
        
        if not char:
            self.tip_lbl.configure(text="")
            return
            
        # Get target key cap map identifier
        k_id = KEY_MAP.get(char)
        if k_id:
            self.highlighted_keys.append(k_id)
            
            # Determine if Shift needs highlighting
            needs_shift = False
            if len(char) == 1:
                shifted_symbols = '~!@#$%^&*()_+{}|:"<>?'
                needs_shift = char.isupper() or char in shifted_symbols
                
            if needs_shift:
                # Symmetrical shift recommendation
                if char in LEFT_HAND_CHARS:
                    self.highlighted_keys.append("RSHIFT")
                else:
                    self.highlighted_keys.append("LSHIFT")
            
            theme_colors = THEMES.get(self.current_theme, THEMES["dark"])
            accent = theme_colors["accent"]
            
            # Highlight target physical key widgets
            for hkey in self.highlighted_keys:
                if hkey in self.key_widgets:
                    self.key_widgets[hkey].configure(
                        fg_color=accent,
                        text_color=theme_colors.get("accent_fg", "#14151f")
                    )
            
            # Highlight Tutor recommended finger
            finger_key = FINGER_MAP.get(char, "finger_right_pinky")
            if finger_key == "finger_thumb":
                # Spacebar -> Highlight both thumbs cooperatively
                if "finger_left_thumb" in self.finger_shapes:
                    self.hand_canvas.itemconfig(self.finger_shapes["finger_left_thumb"], fill=accent)
                if "finger_right_thumb" in self.finger_shapes:
                    self.hand_canvas.itemconfig(self.finger_shapes["finger_right_thumb"], fill=accent)
            else:
                if finger_key in self.finger_shapes:
                    self.hand_canvas.itemconfig(self.finger_shapes[finger_key], fill=accent)
            
            # Update recommendation label
            finger_name = t(finger_key)
            display_char = char
            if char == '\n':
                display_char = "Enter"
            elif char == ' ':
                display_char = "Space"
                
            self.tip_lbl.configure(
                text=t("helper_next_key").format(display_char, finger_name),
                text_color=accent
            )
        else:
            self.tip_lbl.configure(text=t("practice_start_instruction"))

    def visualize_press(self, char):
        """
        Highlight the key physically pressed by the user temporarily.
        """
        k_id = KEY_MAP.get(char)
        if not k_id:
            if char in self.key_widgets:
                k_id = char
            else:
                k_id = KEY_MAP.get(char.lower())
                
        if k_id and k_id in self.key_widgets:
            widget = self.key_widgets[k_id]
            
            # Set a transient pressed style
            press_color = "#10b981"
            if self.current_theme == "cyberpunk":
                press_color = "#ff007f"
                
            widget.configure(
                fg_color=press_color,
                text_color="#ffffff" if self.current_theme != "cyberpunk" else "#050515"
            )
            
            # Revert back after 100ms
            self.after(100, lambda k=k_id: self.restore_key_color(k))

    def restore_key_color(self, k_id):
        """
        Revert the key color back to active highlight or normal states.
        """
        if k_id not in self.key_widgets:
            return
            
        theme_colors = THEMES.get(self.current_theme, THEMES["dark"])
        widget = self.key_widgets[k_id]
        
        if k_id in self.highlighted_keys:
            widget.configure(
                fg_color=theme_colors["accent"],
                text_color=theme_colors.get("accent_fg", "#14151f")
            )
        else:
            widget.configure(
                fg_color=self._get_normal_key_bg(),
                text_color=self._get_normal_key_fg()
            )

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme_colors = THEMES.get(theme_name, THEMES["dark"])
        self.update_key_labels()
        
        self.kbd_container.configure(
            fg_color=theme_colors["card_bg"],
            border_color=theme_colors["border"],
            border_width=1
        )
        
        # Redraw normal keys
        normal_bg = self._get_normal_key_bg()
        normal_fg = self._get_normal_key_fg()
        for k_id, widget in self.key_widgets.items():
            if k_id in self.highlighted_keys:
                widget.configure(
                    fg_color=theme_colors["accent"],
                    text_color=theme_colors.get("accent_fg", "#14151f")
                )
            else:
                widget.configure(
                    fg_color=normal_bg,
                    text_color=normal_fg
                )
                
        # Re-draw visual hands on the Canvas mapping to new themes
        self._draw_hands()
                
        # Update text labels
        if self.next_char:
            self.highlight_key(self.next_char)
        else:
            self.tip_lbl.configure(
                text=t("practice_start_instruction"),
                text_color=theme_colors["fg"]
            )

    def _get_normal_finger_fg(self):
        if self.current_theme == "cyberpunk":
            return "#ff007f" # Cyberpunk neon pink guide lines
        elif self.current_theme == "light":
            return "#cbd5e1"
        else:
            return "#3d3e4e" # Slate-blue gray for dark theme

    def _get_normal_key_bg(self):
        if self.current_theme == "light":
            return "#f3f4f6"
        elif self.current_theme == "cyberpunk":
            return "#101035"
        else:
            return "#242530"

    def _get_normal_key_fg(self):
        theme_colors = THEMES.get(self.current_theme, THEMES["dark"])
        if self.current_theme == "cyberpunk":
            return "#a100ff"
        else:
            return theme_colors["fg"]
