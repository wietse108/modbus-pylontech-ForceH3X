# Pylontech Force H3X Integration for Home Assistant

![HACS Custom](https://img.shields.io/badge/HACS-Custom_Repository-orange.svg?style=for-the-badge)
![Version](https://img.shields.io/badge/version-0.1.0-blue.svg?style=for-the-badge)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)

A fully native, UI-configurable Home Assistant custom integration for the **Pylontech Force H3X** inverter and BMS system. 

Say goodbye to complex, manual Modbus YAML configurations! This integration connects directly to your inverter over Modbus TCP, utilizing smart chunk-reading to poll dozens of registers efficiently without overloading the inverter's WiFi dongle.

---

## ✨ Features

- **UI Config Flow:** Set up your inverter in seconds via the Home Assistant integrations page. No YAML required!
- **Smart Chunk Polling:** Reads all required data from both the Inverter (Slave 2) and the BMS (Slave 1) in highly optimized, delay-spaced blocks to prevent Modbus timeouts.
- **Auto-Discovery:** Automatically creates and groups all sensors under a single Device in your dashboard.
- **Energy Dashboard Ready:** All energy/power sensors are configured with the correct `state_class` and `device_class` to work out-of-the-box with the Home Assistant Energy Dashboard.
- **Resilient Connection:** Built-in auto-reconnect and error handling.

## 📊 Included Sensors

This integration pulls comprehensive data from both the Inverter and the internal Battery Management System (BMS):

* **🌞 Solar (PV):** Voltage, Current, and Power for PV1, PV2, and PV3, plus Total PV Energy.
* **⚡ Grid & AC:** Grid Import/Export, AC Total Power, Load Power, Phase Voltages (R/S/T), AC Frequency, and Total Grid Energy.
* **🔋 Battery (Inverter perspective):** Charge/Discharge Power, Voltage, Current, SOC, and Total Charge/Discharge Energy.
* **🧠 BMS (Internal):** Cell Voltage Max/Min, BMS Temperature, BMS SOC, State of Health (SOH), and total battery cycles.
* **🛠️ Status:** Inverter Status, Battery Status, and internal temperatures.

---

## 🚀 Installation

### Option 1: Via HACS (Recommended)
This integration is easily installable via the [Home Assistant Community Store (HACS)](https://hacs.xyz/).

1. Open Home Assistant and navigate to **HACS** > **Integrations**.
2. Click the three dots (`...`) in the top right corner and select **Custom repositories**.
3. Paste the URL of this GitHub repository.
4. Select **Integration** as the category and click **Add**.
5. Close the popup, search for **Pylontech Force H3X** in HACS, and click **Download**.
6. **Restart Home Assistant.**

### Option 2: Manual Installation
1. Download the latest release from this repository.
2. Copy the `custom_components/pylon_fh3x` folder into your Home Assistant `custom_components` directory.
3. **Restart Home Assistant.**

---

## ⚙️ Configuration

1. In Home Assistant, go to **Settings** > **Devices & Services**.
2. Click the **+ Add Integration** button in the bottom right.
3. Search for **Pylontech Force H3X**.
4. Enter the **IP Address** of your inverter and the **Port** (default is `502`).
5. Click **Submit**. Your sensors will appear immediately!

> **⚠️ Important Notice regarding Modbus TCP:** > Modbus TCP usually allows only **one active connection at a time**. If you have an old YAML Modbus configuration in your `configuration.yaml` or another script reading from the inverter, you MUST disable/remove it and restart Home Assistant before adding this integration. Otherwise, the connection will be refused.

---

## 🔮 Roadmap
- [x] Read Inverter Holding Registers (Power, Voltage, Energy)
- [x] Read BMS Registers (Cell voltages, Temperatures, SOH)
- [ ] Add `switch` and `number` platforms to enable writing to the inverter (e.g., changing work modes, setting charge limits).

## 🐛 Troubleshooting & Support
If the integration fails to connect, check your Home Assistant logs (`home-assistant.log`). 
Common issues:
- `Connection refused`: Another device or script is already connected to the inverter's Modbus port.
- `Timeout`: Poor WiFi signal to the inverter dongle.

Feel free to open an issue on this repository if you encounter any bugs!

---
*Disclaimer: This is a community-built integration and is not officially affiliated with or endorsed by Pylontech.*