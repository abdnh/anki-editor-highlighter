from __future__ import annotations

from anki import hooks
from anki.notes import Note
from aqt import gui_hooks, mw
from aqt.editor import Editor
from aqt.webview import WebContent
from bs4 import BeautifulSoup


def highlight(editor: Editor) -> None:
    config = mw.addonManager.getConfig(__name__)
    patterns = config["patterns"]
    editor.web.eval("highlighter.highlight(%s)" % patterns)


def inject_scripts(web_content: WebContent, context: object | None) -> None:
    if not isinstance(context, Editor):
        return
    web_base = f"/_addons/{mw.addonManager.addonFromModule(__name__)}/web"
    web_content.js.append(f"{web_base}/highlighter.js")
    web_content.js.append(f"{web_base}/vendor/mark.min.js")


def on_note_will_flush(note: Note) -> None:
    for key, value in note.items():
        soup = BeautifulSoup(value, "html.parser")
        for el in soup.select("[data-markjs]"):
            el.unwrap()
        note[key] = soup.decode_contents()


gui_hooks.editor_did_load_note.append(highlight)
gui_hooks.webview_will_set_content.append(inject_scripts)
hooks.note_will_flush.append(on_note_will_flush)
mw.addonManager.setWebExports(__name__, r"(web|user_files)/.*")
