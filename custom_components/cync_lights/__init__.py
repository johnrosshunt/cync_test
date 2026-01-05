"""The Cync Room Lights integration."""
from __future__ import annotations

import ssl

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .cync_hub import CyncHub

PLATFORMS: list[str] = ["light","binary_sensor","switch","fan"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Cync Room Lights from a config entry."""
    # Pre-load SSL context to avoid blocking I/O in event loop
    # The pycync library calls ssl.create_default_context() in async methods
    await hass.async_add_executor_job(ssl.create_default_context)

    hass.data.setdefault(DOMAIN, {})
    remove_options_update_listener = entry.add_update_listener(options_update_listener)
    hub = CyncHub(entry.data, entry.options, remove_options_update_listener)
    hass.data[DOMAIN][entry.entry_id] = hub
    hub.start_tcp_client()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def options_update_listener(
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry
):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hub = hass.data[DOMAIN][entry.entry_id]
    hub.remove_options_update_listener()
    hub.disconnect()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
