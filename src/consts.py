from pathlib import Path

from aqt import mw

ADDON_NAME = "Editor Highlighter"
ADDON_MODULE = mw.addonManager.addonFromModule(__name__)
ADDON_PATH = Path(__file__).parent
