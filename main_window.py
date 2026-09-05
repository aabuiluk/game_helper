"""Main Qt window: pick a Stellaris save and toggle Ironman."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from overlay_widget import CheatOverlay
from stellaris_saves import (
    SaveInfo,
    SaveScanResult,
    convert_save,
    copy_save_to_desktop,
    format_save,
    inspect_save,
    save_display_name,
    scan_saves,
    stellaris_running,
)

WINDOW_STYLE = """
QMainWindow, QWidget#Central {
    background: #101820;
    color: #e8f0f0;
}
QLabel#Title {
    color: #d7f3f3;
    font-size: 22px;
    font-weight: 700;
}
QLabel#Subtitle {
    color: #8fb4b8;
    font-size: 13px;
}
QTableWidget {
    background: #0c141c;
    color: #e8f0f0;
    gridline-color: #1e3340;
    border: 1px solid #2a4a52;
    border-radius: 8px;
    selection-background-color: #1d4e52;
    selection-color: #ffffff;
}
QHeaderView::section {
    background: #16232c;
    color: #9fd8d8;
    padding: 8px;
    border: none;
    border-right: 1px solid #1e3340;
    font-weight: 600;
}
QPushButton {
    background: #1b3a42;
    color: #e8f4f4;
    border: 1px solid #4aa0a0;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
}
QPushButton:hover {
    background: #24545c;
}
QPushButton:disabled {
    color: #6a8080;
    border-color: #2a4044;
}
QPushButton#Danger {
    border-color: #c9a24a;
    color: #ffe7a8;
}
QPushButton#Safe {
    border-color: #6ee0a0;
    color: #c8ffd8;
}
QPushButton#OverlayBtn[active="true"] {
    background: #24545c;
    border-color: #6ee0e0;
}
QStatusBar {
    color: #8fb4b8;
    background: #0c141c;
}
"""


class ConvertWorker(QThread):
    succeeded = Signal(object, object)
    failed = Signal(str)

    def __init__(self, path: Path, enable_ironman: bool) -> None:
        super().__init__()
        self.path = path
        self.enable_ironman = enable_ironman

    def run(self) -> None:
        try:
            target, backup = convert_save(self.path, self.enable_ironman)
            self.succeeded.emit(target, backup)
        except Exception as error:
            self.failed.emit(str(error))


class SaveScanWorker(QThread):
    succeeded = Signal(object)
    failed = Signal(str)

    def run(self) -> None:
        try:
            self.succeeded.emit(scan_saves())
        except Exception as error:
            self.failed.emit(str(error))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Stellaris Ironman Helper")
        self.resize(880, 560)
        self.setStyleSheet(WINDOW_STYLE)
        self._saves: list[SaveInfo] = []
        self._worker: ConvertWorker | None = None
        self._scan_worker: SaveScanWorker | None = None
        self._pending_select: Path | None = None
        self._rescan_requested = False
        self.overlay = CheatOverlay(extra_button="Світи 78")
        self.overlay.closed.connect(self._on_overlay_closed)

        central = QWidget()
        central.setObjectName("Central")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 18, 20, 12)
        layout.setSpacing(12)

        title = QLabel("Stellaris Ironman Helper")
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel(
            "Закрий Stellaris. Зніми Ironman → консоль/чити → збережи → Увімкни Ironman. "
            "При поверненні хелпер скидає cheated_on_save і відновлює блок ачівок."
        )
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Імперія", "Дата в грі", "Режим", "Файл змінено", "Файл"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemSelectionChanged.connect(self._update_buttons)
        layout.addWidget(self.table, 1)

        buttons = QHBoxLayout()
        self.refresh_button = QPushButton("Оновити список")
        self.refresh_button.clicked.connect(lambda: self.reload_saves())
        buttons.addWidget(self.refresh_button)

        self.copy_desktop_button = QPushButton("Копія на Desktop")
        self.copy_desktop_button.clicked.connect(self._copy_to_desktop)
        buttons.addWidget(self.copy_desktop_button)

        self.overlay_button = QPushButton("Віджет читів")
        self.overlay_button.setObjectName("OverlayBtn")
        self.overlay_button.setCheckable(True)
        self.overlay_button.clicked.connect(self._toggle_overlay)
        buttons.addWidget(self.overlay_button)
        buttons.addStretch()

        self.unlock_button = QPushButton("Вимкнути Ironman")
        self.unlock_button.setObjectName("Safe")
        self.unlock_button.clicked.connect(lambda: self._convert(False))
        buttons.addWidget(self.unlock_button)

        self.lock_button = QPushButton("Увімкнути Ironman")
        self.lock_button.setObjectName("Danger")
        self.lock_button.clicked.connect(lambda: self._convert(True))
        buttons.addWidget(self.lock_button)
        layout.addLayout(buttons)

        status = QStatusBar()
        self.setStatusBar(status)
        self.reload_saves()

    def selected_save(self) -> SaveInfo | None:
        rows = self.table.selectionModel().selectedRows() if self.table.selectionModel() else []
        if not rows:
            return None
        index = rows[0].row()
        if 0 <= index < len(self._saves):
            return self._saves[index]
        return None

    def reload_saves(self, select_path: Path | None = None) -> None:
        if select_path is not None and not isinstance(select_path, Path):
            select_path = None
        self._pending_select = select_path
        if self._scan_worker is not None and self._scan_worker.isRunning():
            self._rescan_requested = True
            self.statusBar().showMessage("Сканую сейви…")
            return
        self._start_save_scan()

    def _start_save_scan(self) -> None:
        self.refresh_button.setEnabled(False)
        self.statusBar().showMessage("Сканую сейви…")
        self._scan_worker = SaveScanWorker()
        self._scan_worker.succeeded.connect(self._on_saves_scanned)
        self._scan_worker.failed.connect(self._on_saves_scan_failed)
        self._scan_worker.finished.connect(self._on_saves_scan_finished)
        self._scan_worker.start()

    def _on_saves_scanned(self, result: SaveScanResult) -> None:
        select_path = self._pending_select
        self._pending_select = None
        self._saves = result.saves
        self.table.setRowCount(len(self._saves))
        selected_row = 0
        for row, save in enumerate(self._saves):
            if save.ironman and save.cheated:
                mode = "Ironman · чити"
            elif save.ironman:
                mode = "Ironman"
            elif save.cheated:
                mode = "звичайний · чити"
            else:
                mode = "звичайний"
            values = (
                save.empire,
                save.date,
                mode,
                save.modified.strftime("%Y-%m-%d %H:%M"),
                save_display_name(save.path),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 2:
                    if save.cheated:
                        item.setForeground(QColor("#f0a08c"))
                    elif save.ironman:
                        item.setForeground(QColor("#f0d78c"))
                    else:
                        item.setForeground(QColor("#8fe0b0"))
                item.setData(Qt.ItemDataRole.UserRole, str(save.path))
                self.table.setItem(row, column, item)
            if select_path is not None and save.path.resolve() == select_path.resolve():
                selected_row = row
        if self._saves:
            self.table.selectRow(selected_row)
            message = f"Оновлено: {len(self._saves)} сейв(ів)."
            if result.skipped:
                message += f" Пропущено {len(result.skipped)} файл(ів) — закрий Stellaris або дочекайся збереження."
            self.statusBar().showMessage(message)
        else:
            roots = "\n".join(str(root) for root in result.roots) or str(Path.home() / "Documents/Paradox Interactive/Stellaris/save games")
            self.statusBar().showMessage("Сейви не знайдені.")
            QMessageBox.information(
                self,
                "Сейви не знайдені",
                "У папках збережень немає .sav / .zip / папок gamestate+meta "
                "(ironman_backups не показуємо).\n\n"
                f"Перевір:\n{roots}",
            )
        self._update_buttons()

    def _on_saves_scan_failed(self, message: str) -> None:
        self._pending_select = None
        self._saves = []
        self.table.setRowCount(0)
        self.statusBar().showMessage(f"Не вдалося прочитати сейви: {message}")
        QMessageBox.warning(self, "Помилка", f"Не вдалося прочитати сейви:\n\n{message}")
        self._update_buttons()

    def _on_saves_scan_finished(self) -> None:
        if self._rescan_requested:
            self._rescan_requested = False
            self._start_save_scan()
            return
        self.refresh_button.setEnabled(True)
        self._update_buttons()

    def _update_buttons(self) -> None:
        save = self.selected_save()
        busy = self._worker is not None and self._worker.isRunning()
        self.unlock_button.setEnabled(bool(save) and save.ironman and not busy)
        can_lock = bool(save) and ((not save.ironman) or save.cheated) and not busy
        self.lock_button.setEnabled(can_lock)
        if save and save.ironman and save.cheated:
            self.lock_button.setText("Повернути ачівки")
        else:
            self.lock_button.setText("Увімкнути Ironman")
        self.copy_desktop_button.setEnabled(bool(save) and not busy)

    def _copy_to_desktop(self) -> None:
        save = self.selected_save()
        if save is None:
            QMessageBox.warning(self, "Немає сейву", "Обери збереження зі списку.")
            return
        if stellaris_running():
            answer = QMessageBox.question(
                self,
                "Stellaris запущена",
                "Гра може дописувати сейв — копія може вийти пошкодженою.\nВсе одно скопіювати?",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        try:
            dest = copy_save_to_desktop(save.path)
        except Exception as error:
            QMessageBox.critical(self, "Помилка", str(error))
            self.statusBar().showMessage(str(error))
            return
        self.statusBar().showMessage(f"Скопійовано на Desktop: {dest.name}")
        QMessageBox.information(self, "Готово", f"Копія збереження:\n{dest}")

    def _toggle_overlay(self, checked: bool) -> None:
        if checked:
            self.overlay.show()
            self.overlay.raise_()
        else:
            self.overlay.hide()
        self.overlay_button.setProperty("active", checked)
        self.overlay_button.style().unpolish(self.overlay_button)
        self.overlay_button.style().polish(self.overlay_button)

    def _on_overlay_closed(self) -> None:
        self.overlay_button.setChecked(False)
        self.overlay_button.setProperty("active", False)
        self.overlay_button.style().unpolish(self.overlay_button)
        self.overlay_button.style().polish(self.overlay_button)

    def _convert(self, enable_ironman: bool) -> None:
        save = self.selected_save()
        if save is None:
            QMessageBox.warning(self, "Немає сейву", "Обери збереження зі списку.")
            return
        try:
            save = inspect_save(save.path)
        except Exception as error:
            QMessageBox.critical(self, "Помилка", str(error))
            return

        if stellaris_running():
            answer = QMessageBox.question(
                self,
                "Stellaris запущена",
                "Схоже, Stellaris зараз відкрита. Вона може перезаписати сейв.\nВсе одно продовжити?",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        if enable_ironman and save.ironman and save.cheated:
            prompt = (
                "Сейв уже Ironman, але після консолі стоїть cheated_on_save=yes — "
                "Steam через це не дає ачівки.\n\n"
                f"{format_save(save)}\n\n"
                "Скинути позначку читів і повернути блок achievement?\n"
                "Буде зроблена копія в ironman_backups."
            )
        elif enable_ironman:
            prompt = (
                "Увімкнути Ironman і повернути ачівки?\n\n"
                f"{format_save(save)}\n\n"
                "Буде скинуто cheated_on_save і відновлено блок achievement. "
                "Копія — в ironman_backups."
            )
        else:
            prompt = (
                "Вимкнути Ironman (щоб відкрилась консоль)?\n\n"
                f"{format_save(save)}\n\n"
                "Буде зроблена копія в ironman_backups."
            )
        confirm = QMessageBox.question(self, "Підтвердження", prompt)
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self._worker = ConvertWorker(save.path, enable_ironman)
        self._worker.succeeded.connect(self._on_converted)
        self._worker.failed.connect(self._on_convert_failed)
        self._worker.finished.connect(self._on_convert_finished)
        self.statusBar().showMessage("Конвертую сейв…")
        self._worker.start()
        self._update_buttons()

    def _on_convert_finished(self) -> None:
        self._worker = None
        self._update_buttons()

    def _on_converted(self, target: Path, backup: Path) -> None:
        self.reload_saves(select_path=target)
        info = inspect_save(target)
        mode = "Ironman" if info.ironman else "звичайний"
        eligibility = "ачівки знову дозволені" if not info.cheated else "ачівки все ще заблоковані"
        self.statusBar().showMessage(f"Готово: {target.name}. Копія: {backup.name}")
        QMessageBox.information(
            self,
            "Готово",
            f"Сейв тепер {mode}, {eligibility}.\n\n{target}\n\nРезервна копія:\n{backup}",
        )

    def _on_convert_failed(self, message: str) -> None:
        QMessageBox.critical(self, "Помилка", message)
        self.statusBar().showMessage(message)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.overlay.shutdown()
        super().closeEvent(event)
