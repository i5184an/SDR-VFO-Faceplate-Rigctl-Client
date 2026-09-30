import sys
import math
import socket
from PyQt5.QtCore import Qt, QPointF, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QGridLayout, QStackedWidget, QSizePolicy, QTextEdit
)

# ==================== 1. DISPLAY FREQUENZIMETRO AMBRATO RETROILLUMINATO ====================
class DigitalFrequencyDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.frequency = 10000000  # Default sui 10 MHz (WWV / Tempo campione)
        self.buffer_text = ""

    def set_frequency(self, freq):
        self.frequency = freq
        self.buffer_text = ""
        self.update()

    def set_buffer(self, buf):
        self.buffer_text = buf
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Sfondo retroilluminato ambrato stile apparecchio professionale vintage
        amber_grad = QRadialGradient(w / 2, h / 2, max(w, h))
        amber_grad.setColorAt(0, QColor("#ffb020"))
        amber_grad.setColorAt(1, QColor("#d98200"))
        painter.setBrush(QBrush(amber_grad))
        painter.setPen(QPen(QColor("#734300"), 2))
        painter.drawRoundedRect(2, 2, w - 4, h - 4, 8, 8)

        # Calcolo frequenza corrente per metri e band plan dettagliato
        f_val = self.frequency if not self.buffer_text else int(self.buffer_text.replace('.', '').replace(',', '') or 0)
        if f_val <= 0: f_val = 1
        f_MHz = f_val / 1_000_000.0
        wavelength = 299.792458 / f_MHz
        
        # Formattazione lunghezza d'onda
        if wavelength >= 1000:
            wl_str = f"{wavelength/1000:.2f} km"
        else:
            wl_str = f"{wavelength:.2f} m"

        # --- BAND PLAN PROFESSIONALE ESTESO (SWL / Utility / Ham / Time / Volmet) ---
        band = "HF Spectrum"
        
        # 1. Stazioni di Tempo e Frequenza Campione (WWV, WWVH, CHU, RWM, BPM, JJY) ± 1.5 kHz
        time_freqs_kHz = [2500, 3330, 5000, 7850, 10000, 14670, 15000, 20000, 25000]
        is_time_signal = any(abs(f_val - (t * 1000)) < 1500 for t in time_freqs_kHz)

        # 2. Frequenze di chiamata e soccorso DSC Marittimo
        dsc_freqs_kHz = [2187.5, 4207.5, 6312.0, 8414.5, 12577.0, 16804.5, 18898.5, 22374.5, 25208.5]
        is_dsc = any(abs(f_val - (d * 1000)) < 1500 for d in dsc_freqs_kHz)

        # 3. Frequenze Volmet Aeronautici (Meteo HF)
        volmet_freqs_kHz = [2864, 3413, 3453, 4675, 5450, 5505, 5574, 6604, 6673, 8828, 8861, 10051, 11282, 13270, 13282, 17904]
        is_volmet = any(abs(f_val - (v * 1000)) < 1500 for v in volmet_freqs_kHz)

        # 4. Canali HFDL (HF Data Link) comuni
        hfdl_channels = [3455000, 4660000, 5547000, 6535000, 8933000, 10081000, 11336000, 13303000, 17907000, 21954000]
        is_hfdl = any(abs(f_val - ch) < 2000 for ch in hfdl_channels)

        if is_time_signal:
            band = "Time & Freq Standard (WWV/CHU/RWM)"
        elif is_dsc:
            band = "Maritime HF DSC (Distress/Calling)"
        elif is_volmet:
            band = "Aeronautical VOLMET (Weather)"
        elif is_hfdl or (11.280 <= f_MHz <= 11.380) or (13.290 <= f_MHz <= 13.340):
            band = "Aeronautical HFDL (Data Link)"
        elif f_val < 0.3:
            if 0.1357 <= f_MHz <= 0.1378:
                band = "LF Ham (2200m)"
            elif 0.518 <= f_MHz <= 0.518:
                band = "Navtex (518 kHz)"
            else:
                band = "LF / VLF Spectrum"
        elif 0.3 <= f_MHz < 3.0:
            if 0.5265 <= f_MHz <= 1.6065:
                band = "AM Broadcast (MW)"
            elif 1.8 <= f_MHz <= 2.0:
                band = "160m Ham"
            elif 2.065 <= f_MHz <= 2.107:
                band = "Marine HF Telephony"
            elif 2.170 <= f_MHz <= 2.194:
                band = "Marine HF Distress / Calling"
            elif 2.30 <= f_MHz <= 2.495:
                band = "120m SW Broadcast"
            elif 2.850 <= f_MHz <= 3.150:
                band = "Aeronautical HF Voice"
            elif 3.20 <= f_MHz <= 3.40:
                band = "90m SW Broadcast"
            elif 3.400 <= f_MHz <= 3.500:
                band = "Aeronautical HF En-route"
            else:
                band = "MF / Medium Wave Utility"
        elif 3.0 <= f_MHz < 30.0:
            if (3.400 <= f_MHz <= 3.500) or (4.650 <= f_MHz <= 4.700) or (5.450 <= f_MHz <= 5.730) or \
               (6.525 <= f_MHz <= 6.685) or (8.815 <= f_MHz <= 9.040) or (11.275 <= f_MHz <= 11.400) or \
               (13.260 <= f_MHz <= 13.360) or (17.900 <= f_MHz <= 17.970) or (21.924 <= f_MHz <= 22.000):
                band = "Aeronautical HF En-route / Voice"
            elif (4.063 <= f_MHz <= 4.438) or (6.200 <= f_MHz <= 6.525) or (8.100 <= f_MHz <= 8.815) or \
                 (12.230 <= f_MHz <= 13.200) or (16.360 <= f_MHz <= 17.410) or (18.780 <= f_MHz <= 18.900) or \
                 (22.000 <= f_MHz <= 22.855) or (25.070 <= f_MHz <= 25.120):
                band = "Maritime HF Mobile / RTTY"
            elif 3.5 <= f_MHz <= 3.8:
                band = "80m Ham"
            elif 3.9 <= f_MHz <= 4.0:
                band = "75m SWBC / Ham"
            elif 5.3515 <= f_MHz <= 5.3665:
                band = "60m Ham"
            elif 7.0 <= f_MHz <= 7.2:
                band = "40m Ham"
            elif 10.1 <= f_MHz <= 10.15:
                band = "30m Ham"
            elif 14.0 <= f_MHz <= 14.35:
                band = "20m Ham"
            elif 18.068 <= f_MHz <= 18.168:
                band = "17m Ham"
            elif 21.0 <= f_MHz <= 21.45:
                band = "15m Ham"
            elif 24.89 <= f_MHz <= 24.99:
                band = "12m Ham"
            elif 26.965 <= f_MHz <= 27.405:
                band = "CB Radio (27 MHz)"
            elif 28.0 <= f_MHz <= 29.7:
                band = "10m Ham"
            elif 4.75 <= f_MHz <= 5.06:
                band = "60m SW Broadcast"
            elif 5.90 <= f_MHz <= 6.20:
                band = "49m SW Broadcast"
            elif 7.2 <= f_MHz <= 7.45:
                band = "40m SW Broadcast"
            elif 9.40 <= f_MHz <= 9.90:
                band = "31m SW Broadcast"
            elif 11.60 <= f_MHz <= 12.10:
                band = "25m SW Broadcast"
            elif 13.57 <= f_MHz <= 13.87:
                band = "22m SW Broadcast"
            elif 15.10 <= f_MHz <= 15.80:
                band = "19m SW Broadcast"
            elif 17.48 <= f_MHz <= 17.90:
                band = "16m SW Broadcast"
            elif 18.90 <= f_MHz <= 19.02:
                band = "15m SW Broadcast"
            elif 21.45 <= f_MHz <= 21.85:
                band = "13m SW Broadcast"
            elif 25.60 <= f_MHz <= 26.10:
                band = "11m SW Broadcast"
            else:
                band = "Shortwave Utility / Numbers / RTTY"
        elif 30.0 <= f_MHz < 300.0:
            if 50.0 <= f_MHz <= 54.0:
                band = "6m Ham (VHF)"
            elif 70.0 <= f_MHz <= 70.5:
                band = "4m Ham (VHF)"
            elif 87.5 <= f_MHz <= 108.0:
                band = "FM Broadcast"
            elif 108.0 <= f_MHz <= 137.0:
                band = "Aviation (Air Band VHF)"
            elif 137.0 <= f_MHz <= 138.0:
                band = "Weather Satellites (APT)"
            elif 144.0 <= f_MHz <= 146.0:
                band = "2m Ham (VHF)"
            elif 156.0 <= f_MHz <= 174.0:
                band = "Nautical / Marine VHF"
            elif 146.0 <= f_MHz <= 174.0:
                band = "VHF Commercial / PMR"
            else:
                band = "VHF Spectrum"
        elif 300.0 <= f_MHz <= 3000.0:
            if 430.0 <= f_MHz <= 440.0:
                band = "70cm Ham (UHF)"
            elif 446.0 <= f_MHz <= 446.2:
                band = "PMR446 (Licence-Free)"
            elif 400.0 <= f_MHz <= 470.0:
                band = "UHF Commercial / PMR"
            elif 1240.0 <= f_MHz <= 1300.0:
                band = "23cm Ham (UHF)"
            else:
                band = "UHF Spectrum"
        else:
            band = "Microwave Spectrum"

        info_text = f"{wl_str} — {band}"

        # 1. SCRITTA SUPERIORE (Caratteri neri fini)
        info_font = QFont("Consolas", max(8, int(h * 0.20)), QFont.Normal)
        painter.setFont(info_font)
        painter.setPen(QPen(QColor("#111111"), 1))
        painter.drawText(QRectF(0, 3, w, h * 0.3), Qt.AlignCenter, info_text)

        # 2. STRINGA FREQUENZA PRINCIPALE (Caratteri neri fini)
        if self.buffer_text:
            text_to_show = f"{self.buffer_text} Hz"
        else:
            formatted = f"{self.frequency:,}".replace(",", ".")
            text_to_show = f"{formatted} Hz"

        freq_font_size = max(13, int(h * 0.38))
        freq_font = QFont("Consolas", freq_font_size, QFont.Normal)
        painter.setFont(freq_font)

        freq_rect = QRectF(0, h * 0.28, w, h * 0.68)
        painter.setPen(QPen(QColor("#111111"), 1))
        painter.drawText(freq_rect, Qt.AlignCenter, text_to_show)


# ==================== 2. DIAL ROTATIVO VFO ====================
class RotaryDialWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(130, 130)
        self.setMaximumSize(160, 160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dial_angle = 0.0
        self.is_dragging = False
        self.last_mouse_angle = 0.0
        self.on_rotate_callback = None

    def get_mouse_angle(self, event):
        center = QPointF(self.width() / 2, self.height() / 2)
        pos = event.pos()
        return math.degrees(math.atan2(pos.y() - center.y(), pos.x() - center.x()))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.last_mouse_angle = self.get_mouse_angle(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            current_angle = self.get_mouse_angle(event)
            delta = current_angle - self.last_mouse_angle
            if delta > 180: delta -= 360
            if delta < -180: delta += 360
            self.last_mouse_angle = current_angle
            self.dial_angle = (self.dial_angle + delta) % 360
            if self.on_rotate_callback:
                self.on_rotate_callback(delta)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def wheelEvent(self, event):
        delta = 10 if event.angleDelta().y() > 0 else -10
        self.dial_angle = (self.dial_angle + delta) % 360
        if self.on_rotate_callback:
            self.on_rotate_callback(10 if event.angleDelta().y() > 0 else -10)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        outer_radius = min(cx, cy) - 4

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.dial_angle)

        skirt_grad = QRadialGradient(-10, -10, outer_radius)
        skirt_grad.setColorAt(0, QColor("#565a5e"))
        skirt_grad.setColorAt(0.6, QColor("#31363b"))
        skirt_grad.setColorAt(1, QColor("#1a1d20"))
        painter.setBrush(QBrush(skirt_grad))
        painter.setPen(QPen(QColor("#111"), 1.5))
        painter.drawEllipse(QPointF(0, 0), outer_radius, outer_radius)

        for i in range(40):
            deg = i * 9
            rad = math.radians(deg)
            is_major = (i % 5 == 0)
            tick_len = max(4, int(outer_radius * 0.12)) if is_major else max(2, int(outer_radius * 0.06))
            painter.setPen(QPen(QColor("#ff003b" if is_major else "#aaa"), 1.2 if is_major else 0.7))
            painter.drawLine(QPointF((outer_radius - 2) * math.cos(rad), (outer_radius - 2) * math.sin(rad)),
                             QPointF((outer_radius - 2 - tick_len) * math.cos(rad), (outer_radius - 2 - tick_len) * math.sin(rad)))
        painter.restore()
        
        knob_r = outer_radius - max(10, int(outer_radius * 0.28))
        knob_grad = QRadialGradient(cx - 4, cy - 4, knob_r)
        knob_grad.setColorAt(0, QColor("#3d4248"))
        knob_grad.setColorAt(1, QColor("#1f2328"))
        painter.setBrush(QBrush(knob_grad))
        painter.setPen(QPen(QColor("#111"), 1.5))
        painter.drawEllipse(QPointF(cx, cy), knob_r, knob_r)

        painter.setPen(QPen(QColor("#ff003b"), 2.5, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(int(cx), int(cy - outer_radius - 2), int(cx), int(cy - outer_radius + 4))


# ==================== 3. FINESTRA PRINCIPALE FACEPLATE ====================
class UnifiedRadioFaceplateApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_frequency = 10000000  # Default 10 MHz (WWV)
        self.current_step = 100
        self.current_mode = "USB"
        self.input_buffer = ""
        self.is_pinned = True
        self.sock = None

        self.init_ui()
        self.apply_theme("Dark") # Tema predefinito
        
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(250)
        self.poll_timer.timeout.connect(self.poll_cat_status)
        self.init_tcp()

    def log_diag(self, message):
        if hasattr(self, 'diag_box'):
            self.diag_box.append(message)

    def init_ui(self):
        self.setWindowTitle("SDR++ VFO Faceplate (Rigctl CAT)")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        # A. HEADER SUPERIORE (Stato TCP & Pin)
        top_header = QHBoxLayout()
        self.pin_btn = QPushButton("📌")
        self.pin_btn.setFixedSize(24, 22)
        self.pin_btn.clicked.connect(self.toggle_pin)
        top_header.addWidget(self.pin_btn)

        self.tab_main_btn = QPushButton("SDR++ VFO")
        self.tab_main_btn.setCheckable(True)
        self.tab_main_btn.setChecked(True)
        self.tab_main_btn.clicked.connect(lambda: self.switch_tab(0))
        top_header.addWidget(self.tab_main_btn)

        self.tab_setup_btn = QPushButton("Setup TCP")
        self.tab_setup_btn.setCheckable(True)
        self.tab_setup_btn.clicked.connect(lambda: self.switch_tab(1))
        top_header.addWidget(self.tab_setup_btn)

        top_header.addStretch()

        self.live_lbl = QLabel("● TCP LIVE")
        self.live_lbl.setStyleSheet("color: #34d399; font-size: 10px; font-weight: bold;")
        top_header.addWidget(self.live_lbl)
        main_layout.addLayout(top_header)

        # B. DISPLAY FREQUENZIMETRO AMBRATO
        self.freq_display_widget = DigitalFrequencyDisplay()
        main_layout.addWidget(self.freq_display_widget)

        # C. STACK PRINCIPALE (Console VFO / Setup)
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # --- VIEW 0: MAIN VFO CONSOLE ---
        main_view = QWidget()
        main_vbox = QVBoxLayout(main_view)
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(4)

        # Manopola VFO Rotativa al centro
        self.rotary_dial = RotaryDialWidget()
        self.rotary_dial.on_rotate_callback = self.handle_dial_rotation
        dial_container = QHBoxLayout()
        dial_container.addStretch()
        dial_container.addWidget(self.rotary_dial)
        dial_container.addStretch()
        main_vbox.addLayout(dial_container)

        # Griglia Modi di Emissione
        mode_grid = QGridLayout()
        mode_grid.setSpacing(3)
        self.mode_buttons = {}
        modes_list = [
            ("USB", 0, 0), ("LSB", 0, 1), ("AM", 0, 2), ("FM", 0, 3), ("WFM", 0, 4),
            ("DSB", 1, 0), ("CW", 1, 1), ("RAW", 1, 2), ("DSD", 1, 3), ("OLD DSD", 1, 4)
        ]
        for m_val, r, c in modes_list:
            btn = QPushButton(m_val)
            btn.setCheckable(True)
            if m_val == "USB": btn.setChecked(True)
            btn.clicked.connect(lambda checked, val=m_val: self.set_mode(val))
            mode_grid.addWidget(btn, r, c)
            self.mode_buttons[m_val] = btn
        main_vbox.addLayout(mode_grid)

        # Pulsanti Step di sintonia
        step_layout = QHBoxLayout()
        step_layout.setSpacing(3)
        self.step_buttons = {}
        for s_val, s_text in [(1, "1 Hz"), (10, "10 Hz"), (100, "100 Hz"), (1000, "1 kHz"), (5000, "5 kHz"), (10000, "10 kHz")]:
            btn = QPushButton(s_text)
            btn.setCheckable(True)
            if s_val == 100: btn.setChecked(True)
            btn.clicked.connect(lambda checked, val=s_val: self.set_step(val))
            step_layout.addWidget(btn)
            self.step_buttons[s_val] = btn
        main_vbox.addLayout(step_layout)

        # Tastierino numerico per inserimento diretto frequenza
        keypad_layout = QGridLayout()
        keypad_layout.setSpacing(3)
        keys = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2), ('C', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('⌫', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('.', 2, 3),
            ('0', 3, 0)
        ]
        for key_text, r, c in keys:
            btn = QPushButton(key_text)
            btn.setFont(QFont("Consolas", 9, QFont.Bold))
            if key_text in ['C', '⌫', '.']:
                btn.setObjectName("special_key")
            btn.clicked.connect(lambda checked, t=key_text: self.press_key(t))
            if key_text == '0':
                keypad_layout.addWidget(btn, 3, 0, 1, 2)
            else:
                keypad_layout.addWidget(btn, r, c)

        set_btn = QPushButton("SET FREQ")
        set_btn.setObjectName("set_freq_btn")
        set_btn.clicked.connect(lambda: self.press_key('SET'))
        keypad_layout.addWidget(set_btn, 3, 2, 1, 2)

        main_vbox.addLayout(keypad_layout)
        self.stack.addWidget(main_view)

        # --- VIEW 1: SETUP TCP & TEMI ---
        setup_view = QWidget()
        setup_vbox = QVBoxLayout(setup_view)
        setup_vbox.setSpacing(6)

        setup_vbox.addWidget(QLabel("IP Address (SDR++ Rigctl Server) & Port:"))
        ip_port_layout = QHBoxLayout()
        self.ip_input = QLineEdit("127.0.0.1")
        self.port_input = QLineEdit("12345")
        self.port_input.setMaximumWidth(80)
        ip_port_layout.addWidget(self.ip_input)
        ip_port_layout.addWidget(self.port_input)
        setup_vbox.addLayout(ip_port_layout)

        connect_btn = QPushButton("🔌 Riconnetti TCP Rigctl")
        connect_btn.setObjectName("accent_btn")
        connect_btn.clicked.connect(self.init_tcp)
        setup_vbox.addWidget(connect_btn)

        # Sezione Selezione Temi SDR++
        setup_vbox.addWidget(QLabel("Seleziona Tema Grafico (SDR++):"))
        theme_layout = QGridLayout()
        theme_layout.setSpacing(3)
        self.theme_buttons = {}
        themes = [
            ("Dark", 0, 0), ("Army Green", 0, 1), ("Deep Blue", 1, 0),
            ("Light", 1, 1), ("Marine Grey", 2, 0)
        ]
        for t_name, r, c in themes:
            t_btn = QPushButton(t_name)
            t_btn.setCheckable(True)
            if t_name == "Dark": t_btn.setChecked(True)
            t_btn.clicked.connect(lambda checked, name=t_name: self.apply_theme(name))
            theme_layout.addWidget(t_btn, r, c)
            self.theme_buttons[t_name] = t_btn
        setup_vbox.addLayout(theme_layout)

        setup_vbox.addWidget(QLabel("Log Diagnostico di Connessione:"))
        self.diag_box = QTextEdit()
        self.diag_box.setReadOnly(True)
        setup_vbox.addWidget(self.diag_box)

        setup_vbox.addStretch()
        self.stack.addWidget(setup_view)

    def apply_theme(self, theme_name):
        for name, btn in self.theme_buttons.items():
            btn.setChecked(name == theme_name)

        if theme_name == "Army Green":
            qss = """
                QMainWindow { background-color: #252b24; }
                QWidget { color: #d4dccd; font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 10px; }
                QPushButton { background-color: #364034; border: 1px solid #4a5745; border-radius: 3px; padding: 4px; color: #d4dccd; }
                QPushButton:hover { background-color: #788a6d; color: #252b24; border-color: #93a886; font-weight: bold; }
                QPushButton:checked { background-color: #1e241c; border: 1px solid #93a886; color: #93a886; font-weight: bold; }
                QPushButton#special_key { background-color: #1e241c; color: #93a886; }
                QPushButton#set_freq_btn, QPushButton#accent_btn { background-color: #788a6d; color: #252b24; font-weight: bold; font-family: 'Consolas'; }
                QLineEdit, QTextEdit { background-color: #1a2018; border: 1px solid #364034; color: #93a886; font-family: 'Consolas'; padding: 3px; border-radius: 3px; }
            """
        elif theme_name == "Deep Blue":
            qss = """
                QMainWindow { background-color: #0b1329; }
                QWidget { color: #e2e8f0; font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 10px; }
                QPushButton { background-color: #1e293b; border: 1px solid #334155; border-radius: 3px; padding: 4px; color: #e2e8f0; }
                QPushButton:hover { background-color: #3b82f6; color: #ffffff; border-color: #3b82f6; font-weight: bold; }
                QPushButton:checked { background-color: #0f172a; border: 1px solid #3b82f6; color: #60a5fa; font-weight: bold; }
                QPushButton#special_key { background-color: #0f172a; color: #60a5fa; }
                QPushButton#set_freq_btn, QPushButton#accent_btn { background-color: #3b82f6; color: #ffffff; font-weight: bold; font-family: 'Consolas'; }
                QLineEdit, QTextEdit { background-color: #050b18; border: 1px solid #1e293b; color: #60a5fa; font-family: 'Consolas'; padding: 3px; border-radius: 3px; }
            """
        elif theme_name == "Light":
            qss = """
                QMainWindow { background-color: #f1f5f9; }
                QWidget { color: #1e293b; font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 10px; }
                QPushButton { background-color: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 3px; padding: 4px; color: #1e293b; }
                QPushButton:hover { background-color: #3b82f6; color: #ffffff; border-color: #3b82f6; font-weight: bold; }
                QPushButton:checked { background-color: #cbd5e1; border: 1px solid #3b82f6; color: #1d4ed8; font-weight: bold; }
                QPushButton#special_key { background-color: #cbd5e1; color: #1d4ed8; }
                QPushButton#set_freq_btn, QPushButton#accent_btn { background-color: #2563eb; color: #ffffff; font-weight: bold; font-family: 'Consolas'; }
                QLineEdit, QTextEdit { background-color: #ffffff; border: 1px solid #cbd5e1; color: #1d4ed8; font-family: 'Consolas'; padding: 3px; border-radius: 3px; }
            """
        elif theme_name == "Marine Grey":
            qss = """
                QMainWindow { background-color: #222831; }
                QWidget { color: #eeeeee; font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 10px; }
                QPushButton { background-color: #393e46; border: 1px solid #4e5d6c; border-radius: 3px; padding: 4px; color: #eeeeee; }
                QPushButton:hover { background-color: #00adb5; color: #222831; border-color: #00adb5; font-weight: bold; }
                QPushButton:checked { background-color: #2b3038; border: 1px solid #00adb5; color: #00adb5; font-weight: bold; }
                QPushButton#special_key { background-color: #2b3038; color: #00adb5; }
                QPushButton#set_freq_btn, QPushButton#accent_btn { background-color: #00adb5; color: #222831; font-weight: bold; font-family: 'Consolas'; }
                QLineEdit, QTextEdit { background-color: #1b1f24; border: 1px solid #393e46; color: #00adb5; font-family: 'Consolas'; padding: 3px; border-radius: 3px; }
            """
        else: # Dark (Default)
            qss = """
                QMainWindow { background-color: #1a1d20; }
                QWidget { color: #eff0f1; font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 10px; }
                QPushButton { background-color: #31363b; border: 1px solid #555; border-radius: 3px; padding: 4px; color: #eff0f1; }
                QPushButton:hover { background-color: #ff003b; color: #1a1d20; border-color: #ff003b; font-weight: bold; }
                QPushButton:checked { background-color: #232629; border: 1px solid #ff003b; color: #ff003b; font-weight: bold; }
                QPushButton#special_key { background-color: #232629; color: #ff003b; }
                QPushButton#set_freq_btn, QPushButton#accent_btn { background-color: #ff003b; color: #ffffff; font-weight: bold; font-family: 'Consolas'; }
                QLineEdit, QTextEdit { background-color: #111417; border: 1px solid #31363b; color: #ff003b; font-family: 'Consolas'; padding: 3px; border-radius: 3px; }
            """

        self.setStyleSheet(qss)

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📌")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.pin_btn.setText("📍")
        self.show()

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.tab_main_btn.setChecked(index == 0)
        self.tab_setup_btn.setChecked(index == 1)

    def set_step(self, step_val):
        self.current_step = step_val
        for s, btn in self.step_buttons.items():
            btn.setChecked(s == step_val)

    def set_mode(self, mode_val):
        self.current_mode = mode_val
        for m, btn in self.mode_buttons.items():
            btn.setChecked(m == mode_val)
        self.send_tcp_mode(mode_val)

    def handle_dial_rotation(self, delta):
        self.current_frequency += int(delta * (self.current_step * 0.2))
        self.freq_display_widget.set_frequency(self.current_frequency)
        self.send_tcp_frequency()

    def update_display_buffer(self):
        if not self.input_buffer:
            self.freq_display_widget.set_frequency(self.current_frequency)
        else:
            self.freq_display_widget.set_buffer(self.input_buffer)

    def press_key(self, val):
        if val == 'C':
            self.input_buffer = ""
            self.update_display_buffer()
            return
        if val == '⌫':
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
            self.update_display_buffer()
            return
        if val == 'SET':
            if self.input_buffer:
                try:
                    clean_str = self.input_buffer.replace('.', '').replace(',', '')
                    self.current_frequency = int(clean_str)
                    self.send_tcp_frequency()
                except ValueError:
                    pass
                self.input_buffer = ""
            self.freq_display_widget.set_frequency(self.current_frequency)
            return

        self.input_buffer += val
        self.update_display_buffer()

    def init_tcp(self):
        ip = self.ip_input.text().strip()
        try:
            port = int(self.port_input.text())
        except ValueError:
            port = 12345

        self.log_diag(f"Tentativo connessione Rigctl a {ip}:{port}...")
        try:
            if self.sock:
                self.sock.close()
            self.sock = socket.create_connection((ip, port), timeout=1.5)
            self.live_lbl.setText("● TCP LIVE")
            self.live_lbl.setStyleSheet("color: #34d399; font-size: 10px; font-weight: bold;")
            self.log_diag("✅ Connessione TCP Rigctl stabilita con successo!")
            self.poll_timer.start()
        except Exception as e:
            self.sock = None
            self.live_lbl.setText("● TCP OFFLINE")
            self.live_lbl.setStyleSheet("color: #e74c3c; font-size: 10px; font-weight: bold;")
            self.log_diag(f"❌ Errore connessione: {e}")

    def poll_cat_status(self):
        if self.sock:
            try:
                self.sock.sendall(b"f\n")
                response = self.sock.recv(64)
                if response:
                    freq_str = response.decode('ascii', errors='ignore').strip()
                    if freq_str.isdigit():
                        new_freq = int(freq_str)
                        if new_freq != self.current_frequency and not self.input_buffer:
                            self.current_frequency = new_freq
                            self.freq_display_widget.set_frequency(self.current_frequency)
            except socket.timeout:
                pass
            except Exception as e:
                self.sock = None
                self.live_lbl.setText("● TCP OFFLINE")
                self.live_lbl.setStyleSheet("color: #e74c3c; font-size: 10px; font-weight: bold;")
                self.log_diag(f"❌ Disconnessione dal server Rigctl: {e}")

    def send_tcp_frequency(self):
        if not self.sock:
            return
        try:
            cmd = f"F {self.current_frequency}\n"
            self.sock.sendall(cmd.encode('ascii'))
        except Exception as e:
            self.log_diag(f"❌ Errore invio frequenza: {e}")

    def send_tcp_mode(self, mode):
        if not self.sock:
            return
        try:
            cmd = f"M {mode} 0\n"
            self.sock.sendall(cmd.encode('ascii'))
            self.log_diag(f"📤 Modo impostato: {mode}")
        except Exception as e:
            self.log_diag(f"❌ Errore invio modo {mode}: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UnifiedRadioFaceplateApp()
    window.show()
    sys.exit(app.exec_())