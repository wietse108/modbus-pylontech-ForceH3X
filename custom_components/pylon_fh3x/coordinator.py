"""DataUpdateCoordinator for Pylontech Force H3X."""
import asyncio
import logging
import struct
from datetime import timedelta

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

# =========================================================
# Helper functions for Modbus decoding
# =========================================================
def get_16bit_uint(regs, idx):
    return regs[idx]

def get_16bit_int(regs, idx):
    return struct.unpack('>h', struct.pack('>H', regs[idx]))[0]

def get_32bit_int(regs, idx):
    return struct.unpack('>i', struct.pack('>HH', regs[idx], regs[idx+1]))[0]

def get_32bit_float(regs, idx):
    return struct.unpack('>f', struct.pack('>HH', regs[idx], regs[idx+1]))[0]


async def _modbus_read(client, address, count, target_id):
    """Wrapper om pymodbus versie-verschillen af te vangen."""
    try:
        return await client.read_holding_registers(address=address, count=count, slave=target_id)
    except TypeError:
        pass
    try:
        return await client.read_holding_registers(address=address, count=count, unit=target_id)
    except TypeError:
        pass
    return await client.read_holding_registers(address=address, count=count, device_id=target_id)


class PylontechCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Modbus data from the inverter."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        self.client = AsyncModbusTcpClient(host=host, port=port, timeout=5)
        self.host = host
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def safe_read(self, address, count, slave):
        """Voert een lees-actie uit met een verplichte rustpauze voor de omvormer."""
        # 100ms pause)
        await asyncio.sleep(0.1) 
        res = await _modbus_read(self.client, address, count, slave)
        if res.isError():
            _LOGGER.warning("Fout bij lezen adres %s (Slave %s): %s", address, slave, res)
            return None
        return res.registers

    async def _async_update_data(self):
        """Fetch data from the inverter via Modbus."""
        try:
            if not self.client.connected:
                await self.client.connect()

            data = {}

            # =========================================================
            # SLAVE 2 (inverter) - 
            # =========================================================
            
            # AC & Grid Power (30100 - 30101 en 30108 - 30109)
            r_ac = await self.safe_read(30100, 2, 2)
            if r_ac: data["ac_total_power"] = get_32bit_int(r_ac, 0)
            
            r_grid = await self.safe_read(30108, 2, 2)
            if r_grid: data["grid_total_power"] = get_32bit_int(r_grid, 0)

            # Inverter Status (30115)
            r_status = await self.safe_read(30115, 1, 2)
            if r_status: data["inverter_status"] = get_16bit_uint(r_status, 0)

            # PV Spanning & Stroom (30119 t/m 30124)
            r_pv = await self.safe_read(30119, 6, 2)
            if r_pv:
                data["pv1_voltage"] = get_16bit_uint(r_pv, 0) * 0.1
                data["pv1_current"] = get_16bit_uint(r_pv, 1) * 0.1
                data["pv2_voltage"] = get_16bit_uint(r_pv, 2) * 0.1
                data["pv2_current"] = get_16bit_uint(r_pv, 3) * 0.1
                data["pv3_voltage"] = get_16bit_uint(r_pv, 4) * 0.1
                data["pv3_current"] = get_16bit_uint(r_pv, 5) * 0.1

            # PV Power & Energy (30127 t/m 30130)
            r_pv_tot = await self.safe_read(30127, 4, 2)
            if r_pv_tot:
                data["pv_total_power"] = get_32bit_int(r_pv_tot, 0)
                data["pv_total_energy"] = get_32bit_float(r_pv_tot, 2)

            # Grid Voltages & Freq (30131 t/m 30140)
            r_grid_v = await self.safe_read(30131, 10, 2)
            if r_grid_v:
                data["grid_voltage_r"] = get_16bit_uint(r_grid_v, 0) * 0.1
                data["grid_voltage_s"] = get_16bit_uint(r_grid_v, 2) * 0.1
                data["grid_voltage_t"] = get_16bit_uint(r_grid_v, 4) * 0.1
                data["ac_frequency"] = get_16bit_uint(r_grid_v, 9) * 0.01

            # Temperature (30146)
            r_temp = await self.safe_read(30146, 2, 2)
            if r_temp: 
                data["inverter_temperature"] = get_16bit_int(r_temp, 0) * 0.1
                data["heatsink_temperature"] = get_16bit_int(r_temp, 1) * 0.1


            # Grid Energy In/Out (30156 t/m 30159)
            r_grid_e = await self.safe_read(30156, 4, 2)
            if r_grid_e:
                data["total_grid_import"] = get_32bit_float(r_grid_e, 0)
                data["total_grid_export"] = get_32bit_float(r_grid_e, 2)

            # Battery Status, Power, Voltage, Current (30161 t/m 30165)
            r_batt = await self.safe_read(30161, 5, 2)
            if r_batt:
                data["battery_status"] = get_16bit_uint(r_batt, 0)
                data["battery_power"] = get_32bit_int(r_batt, 1)
                data["battery_voltage"] = get_16bit_uint(r_batt, 3) * 0.1
                data["battery_current"] = get_16bit_int(r_batt, 4) * 0.1

            # Load Power (30172)
            r_load = await self.safe_read(30172, 2, 2)
            if r_load: data["eps_power"] = get_32bit_int(r_load, 0)

            # Battery Energy (30174 t/m 30177)
            r_batt_e = await self.safe_read(30174, 4, 2)
            if r_batt_e:
                data["total_battery_charge"] = get_32bit_float(r_batt_e, 0)
                data["total_battery_discharge"] = get_32bit_float(r_batt_e, 2)

            # SOC & CT Currents (30182 t/m 30185)
            r_soc = await self.safe_read(30182, 4, 2)
            if r_soc:
                data["battery_soc"] = get_16bit_uint(r_soc, 0)


            # =========================================================
            # SLAVE 2 (inverter) - EMS Settings 
            # =========================================================
            r_ems = await self.safe_read(40901, 7, 2)
            if r_ems:
                # 40901 is S16 (Signed), dus get_16bit_int gebruiken!
                data["charge_discharge_power"] = get_16bit_int(r_ems, 0)
                
                # De rest is U16 (Unsigned)
                data["charge_limit_soc"] = get_16bit_uint(r_ems, 1) #40902
                data["discharge_limit_soc"] = get_16bit_uint(r_ems, 2) #40903
                data["ems_mode"] = str(get_16bit_uint(r_ems, 6)) #40907


            #heatpump 
            r_hp = await self.safe_read(40848, 1, 2)
            if r_hp:
                data["heat_pump"] = get_16bit_uint(r_hp, 0)

            
            # =========================================================
            # SLAVE 1 (BMS) - Volgens documentatie Appendix I
            # =========================================================
            
            # BMS Voltage (5123 / 0x1403)
            r_bms_v = await self.safe_read(5123, 1, 1)
            if r_bms_v: data["bms_voltage"] = get_16bit_uint(r_bms_v, 0) * 0.1

            # BMS Temp, SOC, Cycles (5126 / 0x1406 t/m 0x1408)
            r_bms_t = await self.safe_read(5126, 3, 1)
            if r_bms_t:
                data["bms_temperature"] = get_16bit_int(r_bms_t, 0) * 0.1
                data["bms_soc"] = get_16bit_uint(r_bms_t, 1)
                data["bms_cycles"] = get_16bit_uint(r_bms_t, 2)

            # BMS Cell Volts (5136 / 0x1410 t/m 0x1411)
            r_bms_cv = await self.safe_read(5136, 2, 1)
            if r_bms_cv:
                data["bms_cell_voltage_max"] = get_16bit_uint(r_bms_cv, 0) * 0.001
                data["bms_cell_voltage_min"] = get_16bit_uint(r_bms_cv, 1) * 0.001

            # BMS SOH (5152 / 0x1420)
            r_bms_soh = await self.safe_read(5152, 1, 1)
            if r_bms_soh: data["bms_soh"] = get_16bit_uint(r_bms_soh, 0)

            # Controleer of we überhaupt iets hebben binnengekregen
            if not data:
                raise UpdateFailed("Geen data ontvangen van omvormer. Timeout of apparaat reageert niet.")

            return data

        except ModbusException as err:
            raise UpdateFailed(f"Fout in Modbus communicatie: {err}")
        except Exception as err:
            raise UpdateFailed(f"Onverwachte fout: {err}")

    async def async_write_register(self, address: int, value: int, slave: int = 2) -> bool:
        """Schrijf een waarde naar een holding register op de omvormer."""
        try:
            if not self.client.connected:
                await self.client.connect()

            # Pymodbus write_register functie (gebruikt standaard Function Code 06)
            # Voor nieuwere pymodbus versies proberen we slave, unit, en device_id af te vangen
            try:
                res = await self.client.write_register(address=address, value=value, slave=slave)
            except TypeError:
                try:
                    res = await self.client.write_register(address=address, value=value, unit=slave)
                except TypeError:
                    res = await self.client.write_register(address=address, value=value, device_id=slave)

            if res.isError():
                _LOGGER.error("Fout bij het schrijven naar register %s: %s", address, res)
                return False

            _LOGGER.info("Succesvol %s geschreven naar register %s", value, address)
            
            # Vraag direct na het schrijven een nieuwe data-update aan, 
            # zodat je dashboard direct de nieuwe status laat zien!
            await self.async_request_refresh()
            return True

        except Exception as err:
            _LOGGER.error("Onverwachte fout bij schrijven naar Modbus: %s", err)
            return False