from __future__ import annotations

from anki import hooks
from anki.notes import Note
from aqt import gui_hooks, mw
from aqt.clayout import CardLayout
from aqt.editor import Editor
from aqt.reviewer import Reviewer
from aqt.webview import WebContent
from bs4 import BeautifulSoup

try:
    from aqt.browser.previewer import Previewer
except ImportError:
    from aqt.previewer import Previewer  # type: ignore

from .config import Config
from .gui.config import ConfigDialog

config = Config(mw.addonManager)


def highlight(editor: Editor) -> None:
    terms = config["terms"]
    editor.web.eval("highlighter.highlight(%s)" % terms)


def inject_scripts(web_content: WebContent, context: object | None) -> None:
    web_base = f"/_addons/{mw.addonManager.addonFromModule(__name__)}/web"
    if isinstance(context, Editor):
        web_content.js.append(f"{web_base}/highlighter.js")
        web_content.js.append(f"{web_base}/vendor/mark.min.js")
    if isinstance(context, (Reviewer, Previewer, CardLayout)):
        web_content.css.append(
            f"/_addons/{mw.addonManager.addonFromModule(__name__)}/user_files/highlight.css"
        )


def on_note_will_flush(note: Note) -> None:
    if not config["persistent"]:
        for key, value in note.items():
            soup = BeautifulSoup(value, "html.parser")
            for el in soup.select("[data-markjs]"):
                el.unwrap()
            note[key] = soup.decode_contents()


def on_config() -> None:
    ConfigDialog(mw, mw, config).exec()


gui_hooks.editor_did_load_note.append(highlight)
gui_hooks.webview_will_set_content.append(inject_scripts)
hooks.note_will_flush.append(on_note_will_flush)
mw.addonManager.setWebExports(__name__, r"(web|user_files)/.*")
mw.addonManager.setConfigAction(__name__, on_config)
