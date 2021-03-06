import logging
import os

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate import const as climate_const
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS

from constants import DOMAIN
from worcester_bosch_wave.wave_thermo import WaveThermostat

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info):
    serial_number = config['serial_number']
    access_code = config['access_code']
    password = config['password']

    _LOGGER.error('Could not connect to Worcester Wave')

    # States are in the format DOMAIN.OBJECT_ID.
    hass.states.set('hello_world.Hello_World', 'Works!')

    # Return boolean to indicate that initialization was successfully.
    return True


class WorcesterWaveEntity(ClimateEntity):
    # Implement one of these methods.

    def __init__(self):
        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_hvac_modes = [
            climate_const.HVAC_MODE_OFF,
            climate_const.HVAC_MODE_HEAT,
            climate_const.HVAC_MODE_AUTO,
        ]
        self._attr_target_temperature_step = 0.5

        self.wave = WaveThermostat(
            serial_number=os.environ.get('WAVE_SERIAL_NUMBER'),
            access_code=os.environ.get('WAVE_ACCESS_CODE'),
            password=os.environ.get('WAVE_PASSWORD'),
        )

    @property
    def name(self):
        """Name of the entity."""
        return 'Worcester Bosch Wave Thermostat'

    @property
    def hvac_action(self) -> str | None:
        # TODO: Implement
        return self._attr_hvac_action

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        self.wave.status.update()
        self._attr_current_temperature = self.wave.status.current_temp
        return super().current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        self.wave.status.update()
        self._attr_target_temperature = self.wave.status.set_point
        return super().target_temperature

    @property
    def target_temperature_step(self) -> float | None:
        """Return the supported step of target temperature."""
        return self._attr_target_temperature_step

    @property
    def target_temperature_high(self) -> float | None:
        """Return the highbound target temperature we try to reach.

        Requires SUPPORT_TARGET_TEMPERATURE_RANGE.
        """
        return self._attr_target_temperature_high

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode, e.g., home, away, temp.

        Requires SUPPORT_PRESET_MODE.
        """
        return self._attr_preset_mode

    @property
    def preset_modes(self) -> list[str] | None:
        """Return a list of available preset modes.

        Requires SUPPORT_PRESET_MODE.
        """
        return self._attr_preset_modes

    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        target_temp_high = kwargs.get(climate_const.ATTR_TARGET_TEMP_HIGH)
        self.wave.set_temperature(target_temp_high)

    def set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        raise NotImplementedError()

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        if hasattr(self, 'turn_on'):
            await self.hass.async_add_executor_job(self.turn_on)  # type: ignore[attr-defined]
            return

        # Fake turn on
        for mode in (HVAC_MODE_HEAT_COOL, HVAC_MODE_HEAT, HVAC_MODE_COOL):
            if mode not in self.hvac_modes:
                continue
            await self.async_set_hvac_mode(mode)
            break

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        if hasattr(self, 'turn_off'):
            await self.hass.async_add_executor_job(self.turn_off)  # type: ignore[attr-defined]
            return

        # Fake turn off
        if HVAC_MODE_OFF in self.hvac_modes:
            await self.async_set_hvac_mode(HVAC_MODE_OFF)

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return self._attr_supported_features

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        if not hasattr(self, '_attr_min_temp'):
            return convert_temperature(
                DEFAULT_MIN_TEMP, TEMP_CELSIUS, self.temperature_unit
            )
        return self._attr_min_temp

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        if not hasattr(self, '_attr_max_temp'):
            return convert_temperature(
                DEFAULT_MAX_TEMP, TEMP_CELSIUS, self.temperature_unit
            )
        return self._attr_max_temp
