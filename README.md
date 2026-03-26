# Pylontech Force H3X – Home Assistant Modbus Integration

A Home Assistant Modbus TCP integration for the **Pylontech Force H3X** hybrid inverter, based on the official Pylontech Modbus protocol documentation (V1.2, 2025-08-11).

> Developed and tested by a real Force H3X owner. Contributions welcome.

---

## Features

- Real-time PV power per string (3 inputs)
- Grid power, voltage and current per phase (3-phase)
- Battery SOC, power, voltage, current
- BMS data: SOH, cell voltages, temperature, cycle count
- Lifetime energy totals: PV production, grid import/export, battery charged/discharged
- EMS mode control (Self-Consumption, Backup, Off-Grid, Feed-in Priority, User Mode)
- Charge/discharge power setpoint (User Mode)
- Full compatibility with the HA **Energy Dashboard**

---

## Requirements

- Home Assistant 2024.x or newer
- Pylontech Force H3X inverter with LAN port connected to your local network
- No Solarman dongle required – direct Modbus TCP connection

---

## Installation

### 1. Set a static IP on the inverter

Use the Pylontech app to assign a fixed IP address to the FH3X LAN port.  
Default factory IP: `172.22.184.210`, port `502`.

It is strongly recommended to either set a static IP in the app or reserve the IP via your router's DHCP settings.

### 2. Copy the config file

Copy `pylon_fh3x_modbus.yaml` to your HA config directory:

```
/config/pylon_fh3x_modbus.yaml
```

### 3. Edit the IP address

Open the file and set the correct IP address on the `host:` line:

```yaml
host: 192.168.1.XXX   # replace with your inverter's IP
```

### 4. Add to configuration.yaml

```yaml
modbus: !include pylon_fh3x_modbus.yaml
```

### 5. Restart Home Assistant

After restarting, all entities will appear under the `pylon_fh3x` device.

---

## Energy Dashboard Setup

Go to **Settings → Dashboards → Energy** and configure:

| Field | Entity |
|---|---|
| Grid consumption | `sensor.fh3x_total_grid_import` |
| Grid return | `sensor.fh3x_total_grid_export` |
| Solar production | `sensor.fh3x_pv_total_energy` |
| Battery charged | `sensor.fh3x_total_battery_charged` |
| Battery discharged | `sensor.fh3x_total_battery_discharged` |

---

## Technical Details

### Why `input_type: holding` for 30xxx registers?

The FH3X uses Modbus **function code 03** (FC03, holding registers) for all registers, including the 30xxx range. Using `input_type: input` (FC04) will return errors.

### Why no `swap: word` for 32-bit values?

The FH3X transmits 32-bit values in big-endian byte order (high word first), which is the Modbus standard. HA's `swap: word` would reverse the words and produce incorrect values.

### Why `float32` for energy totals?

The inverter stores lifetime energy totals (kWh) as IEEE 754 float32 values directly in engineering units. No scaling is needed.

### Slave addresses

| Slave | Content |
|---|---|
| 1 | BMS registers (`0x1400` base address for ESS1) |
| 2 | Inverter registers (30xxx read-only, 40xxx read/write) |

---

## Troubleshooting

**"Failed to connect"**  
→ Check the IP address and make sure the LAN cable is connected. The inverter must be powered on.

**Transaction ID mismatch errors in logs**  
→ Increase `message_wait_milliseconds` (e.g. to `200` or `500`).

**Sensors show `unavailable` after HA restart**  
→ The `delay: 30` setting waits 30 seconds before polling. This is intentional to prevent boot hangs while the network is not yet ready.

**BMS sensors show `unavailable`**  
→ BMS registers (slave 1) are only available when the battery is actively communicating. If the battery is in sleep mode they may not respond.

**Energy totals not updating**  
→ These sensors have `scan_interval: 60`. Wait at least one minute after startup.

---

## Fault & Warning Code Reference

The `FH3X Fault Code` and `FH3X Warning Code` sensors return bitmask values.  
See **Appendix VIII** and **Appendix IX** of the Pylontech FH3X Modbus Protocol documentation for the full bit definitions (MCU fault, relay fault, grid missing, BMS communication fail, etc.).

---

## Contributing

If you find register errors, have additional registers to add, or test on a different firmware version, please open an issue or pull request.

Known gaps / things to verify:
- Grid power per phase (30186/30188/30190) — may require firmware with parallel mode enabled
- EPS/backup output registers (30172+)
- Second ESS battery (ESS2 base address TBD)

---

## License

MIT License — free to use, modify and share.
