# SDR-VFO-Faceplate-Rigctl-Client
An advanced virtual control panel (Faceplate) developed in Python and PyQt5 to control SDR++ in real time via the Rigctl network protocol. Designed with shortwave listeners (SWL), broadcasting enthusiasts, and radio amateurs in mind.
## 🚀 Key Features

* **Retro Backlit Frequency Display (Amber):** Professional vintage receiver aesthetic with dynamic wavelength indication and integrated band analysis.
* **Extended & Detailed Band Plan:** Automatic real-time recognition of:
  * Standard time and frequency stations (WWV, WWVH, CHU, RWM, BPM, JJY).
  * Aeronautical VOLMET frequencies (HF Weather).
  * HFDL (HF Data Link) channels and En-route traffic.
  * Amateur radio bands (LF to UHF) and international broadcasting (SWBC).
  * Maritime HF DSC distress/calling channels and Navtex.
* **Rotary VFO Knob:** Ultra-smooth tuning control via mouse dragging or scroll wheel, with configurable frequency steps (1 Hz, 10 Hz, 100 Hz, 1 kHz, 5 kHz, 10 kHz).
* **Direct Numeric Keypad:** Fast frequency entry with dedicated `SET`, clear, and backspace keys.
* **Emission Mode Management:** Quick selection of USB, LSB, AM, FM, WFM, DSB, CW, RAW, and DSD directly from the panel.
* **Customizable Themes:** 5 built-in color palettes to match your workflow style:
  * *Dark* (Default)
  * *Army Green*
  * *Deep Blue*
  * *Light*
  * *Marine Grey*
* **Always on Top (Pin Mode):** Compact and flexible window with an optional Always-on-Top toggle (`📌`).

---

## 📋 System Requirements

* **Python 3.8 or higher**
* **PyQt5** library

```bash
pip install PyQt5
```

---

## ⚙️ Quick Start Guide

1. Launch **SDR++** on your computer and make sure to enable the **Rigctl Server** module (default port: `12345`).
2. Clone this repository or download the main script:
   ```bash
   git clone https://github.com/i5184an/sdrpp-vfo-faceplate.git
   cd sdrpp-vfo-faceplate
   ```
3. Run the application:
   ```bash
   python sdrpp_faceplate.py
   ```
4. From the **Setup TCP** tab, verify the Rigctl server IP address and port, then click **Reconnect TCP Rigctl**.

---

## 🖥️ Interface Overview

The layout is split into two main tabs accessible from the top header:
* **SDR++ VFO:** The main operational control panel (Display, Rotary VFO, Modes, Steps, and Keypad).
* **Setup TCP & Themes:** Network connection settings, real-time diagnostic logs, and graphic theme selector.

---

## 🤝 Contributions & Feedback

Contributions, bug reports, and feature requests are always welcome! Feel free to open a *Pull Request* or an *Issue* on the GitHub repository.

## 📄 License
Distributed under the **MIT** License. See `LICENSE` for more information.

<img width="1908" height="1079" alt="SDR++ tuning knob" src="https://github.com/user-attachments/assets/72f4c1dc-a8b8-4d48-8525-440e9f2982b2" />
