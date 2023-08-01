from __future__ import annotations

from anki.utils import no_bundled_libs
from aqt.main import AnkiQt
from aqt.qt import *
from aqt.utils import askUser, restoreGeom, saveGeom

from .. import consts
from ..config import Config
from ..terms import Term, terms_dict_to_list, terms_list_to_dict

if qtmajor > 5:
    from ..forms.config_qt6 import Ui_Dialog
else:
    from ..forms.config_qt5 import Ui_Dialog  # type: ignore


def open_file(file: str) -> None:
    with no_bundled_libs():
        QDesktopServices.openUrl(QUrl.fromLocalFile(file))


class ConfigDialog(QDialog):
    geom_key = f"{consts.ADDON_MODULE}_config"

    def __init__(self, mw: AnkiQt, parent: QWidget, config: Config):
        self.mw = mw
        self.config = config
        self.dirty = False
        super().__init__(parent, Qt.WindowType.Window)
        self.setup_ui()

    def setup_ui(self) -> None:
        self.form = Ui_Dialog()
        self.form.setupUi(self)
        restoreGeom(self, self.geom_key)
        self.setWindowTitle(f"{consts.ADDON_NAME} - Configuration")
        self.form.persist_heighlights.setChecked(self.config["persistent"])

        terms = terms_dict_to_list(self.config["terms"])
        self.form.terms.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.form.terms.verticalHeader().hide()
        self.form.terms.setRowCount(len(terms))
        for i, term in enumerate(terms):
            self.init_row(i, term)
        qconnect(self.form.terms.itemChanged, self.on_term_item_changed)
        for i in range(self.form.terms.columnCount()):
            self.form.terms.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Stretch
            )

        qconnect(self.form.persist_heighlights.toggled, self.on_persistence_toggled)
        qconnect(self.form.new_term.clicked, self.on_new_term)
        # TODO: trigger on Delete key too
        qconnect(self.form.delete_term.clicked, self.on_delete_term)
        qconnect(self.form.edit_styles.clicked, self.on_edit_styles)
        qconnect(self.form.save.clicked, self.on_save)
        self.form.save.setShortcut(QKeySequence("Ctrl+Return"))

    def init_row(self, i: int, term: Term) -> None:
        self.form.terms.setItem(i, 0, QTableWidgetItem(term.text))
        self.form.terms.setItem(i, 1, QTableWidgetItem(term.classes))
        flags_item = QTableWidgetItem(term.flags)
        self.set_regex_item_flags(flags_item)
        if term.is_regex:
            flags_item.setCheckState(Qt.CheckState.Checked)
        else:
            flags_item.setCheckState(Qt.CheckState.Unchecked)
        self.form.terms.setItem(i, 2, flags_item)

    def on_persistence_toggled(self) -> None:
        self.dirty = True

    def set_regex_item_flags(self, item: QTableWidgetItem) -> None:
        flag = (
            Qt.ItemFlag.ItemIsEditable
            if item.checkState() == Qt.CheckState.Checked
            else Qt.ItemFlag.NoItemFlags
        )
        item.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | flag
        )

    def on_term_item_changed(self, item: QTableWidgetItem) -> None:
        self.dirty = True
        if item.column() == 2:
            self.form.terms.blockSignals(True)
            self.set_regex_item_flags(item)
            self.form.terms.blockSignals(False)

    def on_new_term(self) -> None:
        self.form.terms.setRowCount(self.form.terms.rowCount() + 1)
        self.init_row(self.form.terms.rowCount() - 1, Term("", "", False, ""))

    def on_delete_term(self) -> None:
        self.dirty = True
        # TODO: remove all selected rows
        if self.form.terms.selectedIndexes():
            last_index = self.form.terms.selectedIndexes()[-1]
            self.form.terms.removeRow(last_index.row())

    def save(self) -> None:
        terms: list[Term] = []
        for row in range(self.form.terms.rowCount()):
            term_item = self.form.terms.item(row, 0)
            term_text = term_item.text()
            if not term_text.strip():
                continue
            classes_item = self.form.terms.item(row, 1)
            classes = classes_item.text()
            flags_item = self.form.terms.item(row, 2)
            flags = flags_item.text()
            is_regex = flags_item.checkState() == Qt.CheckState.Checked
            terms.append(Term(term_text, classes, is_regex, flags))
        self.config["persistent"] = self.form.persist_heighlights.isChecked()
        self.config["terms"] = terms_list_to_dict(terms)

    def on_edit_styles(self) -> None:
        open_file(str(consts.ADDON_PATH / "user_files" / "highlight.css"))

    def on_save(self) -> None:
        self.save()
        self.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        saveGeom(self, self.geom_key)
        if self.dirty:
            if askUser("Save changes?", self, title=consts.ADDON_NAME):
                self.save()
        return super().closeEvent(event)
