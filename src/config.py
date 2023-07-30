from __future__ import annotations

from typing import Any

from aqt.addons import AddonManager


class Config:
    def __init__(self, addon_manager: AddonManager):
        self.addon_manager = addon_manager
        self._config = addon_manager.getConfig(__name__)
        addon_manager.setConfigUpdatedAction(__name__, self._config_updated_action)

    def _config_updated_action(self, new_config: dict) -> None:
        self._config.update(new_config)

    def _write(self) -> None:
        self.addon_manager.writeConfig(__name__, self._config)

    def __getitem__(self, key: str) -> Any:
        return self._config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._config[key] = value
        self._write()

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
