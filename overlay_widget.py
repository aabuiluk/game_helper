"""Always-on-top semi-transparent overlay with Stellaris cheat codes."""

from __future__ import annotations

from PySide6.QtCore import Qt, QPoint, QTimer, Signal
from PySide6.QtGui import QColor, QGuiApplication, QMouseEvent, QShowEvent, QHideEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSizeGrip,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from cheats import HARVEST_RESOURCES, SPECIAL_WINDOW_CHEATS, Cheat, HarvestResource, filter_cheats
from overlay_pin import pin_overlay
from run_scripts import install_run_scripts, run_command

OVERLAY_STYLE = """
QWidget#CheatOverlayWindow {
    background: transparent;
}
QFrame#CheatOverlay {
    background: rgba(10, 18, 26, 230);
    border: 1px solid rgba(90, 196, 196, 160);
    border-radius: 10px;
}
QWidget#TitleBar {
    background: rgba(16, 32, 42, 230);
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}
QLabel#TitleLabel {
    color: #d7f3f3;
    font-size: 13px;
    font-weight: 600;
}
QLabel#HintLabel {
    color: #8fb4b8;
    font-size: 11px;
}
QLabel#CopiedLabel {
    color: #7dffb3;
    font-size: 11px;
}
QLineEdit {
    background: rgba(8, 16, 22, 200);
    color: #e8f4f4;
    border: 1px solid #3a6a70;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: #2a7a7a;
}
QListWidget {
    background: rgba(8, 16, 22, 160);
    color: #e8f4f4;
    border: none;
    outline: none;
    font-size: 12px;
}
QListWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(58, 106, 112, 80);
}
QListWidget::item:hover {
    background: rgba(70, 170, 170, 45);
}
QListWidget::item:selected {
    background: rgba(70, 170, 170, 80);
}
QPushButton {
    background: rgba(28, 58, 66, 220);
    color: #d7f3f3;
    border: 1px solid #4aa0a0;
    border-radius: 6px;
    padding: 4px 10px;
}
QPushButton:hover {
    background: rgba(42, 90, 98, 230);
}
QComboBox {
    background: rgba(8, 16, 22, 220);
    color: #e8f4f4;
    border: 1px solid #3a6a70;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 24px;
}
QComboBox:hover {
    border-color: #4aa0a0;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox QAbstractItemView {
    background: #0c141c;
    color: #e8f4f4;
    border: 1px solid #3a6a70;
    selection-background-color: #1d4e52;
    outline: none;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #2a4a52;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 12px;
    height: 12px;
    margin: -4px 0;
    background: #6ee0e0;
    border-radius: 6px;
}
QSizeGrip {
    width: 16px;
    height: 16px;
}
QMenuBar {
    background: rgba(12, 28, 36, 230);
    color: #d7f3f3;
    font-size: 12px;
    padding: 2px 4px;
    border-bottom: 1px solid rgba(90, 196, 196, 80);
}
QMenuBar::item {
    padding: 4px 10px;
    background: transparent;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background: rgba(70, 170, 170, 70);
}
QMenu {
    background: #0c141c;
    color: #e8f4f4;
    border: 1px solid #3a6a70;
}
QMenu::item {
    padding: 6px 18px;
}
QMenu::item:selected {
    background: #1d4e52;
}
QFrame#HarvestBox {
    background: rgba(16, 36, 44, 220);
    border: 1px solid rgba(90, 196, 196, 160);
    border-radius: 8px;
    padding: 8px;
}
QLabel#HarvestTitle {
    color: #d7f3f3;
    font-size: 12px;
    font-weight: 600;
}
"""


class _TitleBar(QWidget):
    def __init__(self, parent: QWidget, title: str = "Чити Stellaris", extra_button: str | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self._drag_offset: QPoint | None = None
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 8, 8)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("TitleLabel")
        layout.addWidget(title_label)
        layout.addStretch()

        self.extra_button: QPushButton | None = None
        if extra_button:
            self.extra_button = QPushButton(extra_button)
            layout.addWidget(self.extra_button)

        opacity_label = QLabel("прозорість")
        opacity_label.setStyleSheet("color: #8fb4b8; font-size: 11px;")
        layout.addWidget(opacity_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(40, 100)
        self.opacity_slider.setValue(82)
        self.opacity_slider.setFixedWidth(90)
        layout.addWidget(self.opacity_slider)

        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(28, 24)
        layout.addWidget(self.close_button)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            self._drag_offset = event.globalPosition().toPoint() - window.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)


class CheatOverlay(QWidget):
    closed = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str = "Чити Stellaris",
        cheats: tuple[Cheat, ...] | None = None,
        extra_button: str | None = None,
        hint: str | None = None,
        place_on_screen: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("CheatOverlayWindow")
        self.setWindowTitle(title)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._force_close = False
        self._cheat_source = cheats
        self._special: CheatOverlay | None = None
        self.setMinimumSize(420, 360)
        self.resize(500, 660)
        self.setStyleSheet(OVERLAY_STYLE)
        self.setWindowOpacity(0.82)

        root = QVBoxLayout(self)
        root.setContentsMargins(1, 1, 1, 1)
        root.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("CheatOverlay")
        root.addWidget(frame)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = _TitleBar(self, title, extra_button=extra_button)
        self.title_bar.close_button.clicked.connect(self.hide)
        self.title_bar.opacity_slider.valueChanged.connect(self._set_opacity)
        if self.title_bar.extra_button is not None:
            self.title_bar.extra_button.clicked.connect(self._open_special)
        layout.addWidget(self.title_bar)

        self.menu_bar = QMenuBar()
        self.menu_bar.setNativeMenuBar(False)
        self._build_run_menu()
        layout.addWidget(self.menu_bar)

        body = QVBoxLayout()
        body.setContentsMargins(10, 8, 10, 8)
        body.setSpacing(8)
        layout.addLayout(body)

        hint = QLabel(
            hint
            or (
                "Клік по команді копіює її. Run-файли — на початку списку. "
                "Якщо віджет зникає в грі — Windowed або Borderless."
            )
        )
        hint.setObjectName("HintLabel")
        hint.setWordWrap(True)
        body.addWidget(hint)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Пошук: minerals, флот, планета…")
        self.search.textChanged.connect(self._rebuild_list)
        body.addWidget(self.search)

        harvest = QFrame()
        harvest.setObjectName("HarvestBox")
        harvest_layout = QVBoxLayout(harvest)
        harvest_layout.setContentsMargins(0, 0, 0, 0)
        harvest_layout.setSpacing(4)
        harvest_label = QLabel(
            "4. Орбітальні депозити — вибери зірку / астероїд / планету"
            if cheats is not None
            else "Добувати з орбіти — вибери зірку / астероїд / планету"
        )
        harvest_label.setObjectName("HarvestTitle")
        harvest_label.setWordWrap(True)
        harvest_layout.addWidget(harvest_label)
        harvest_row = QHBoxLayout()
        harvest_row.setSpacing(6)
        self.harvest_resource = QComboBox()
        self.harvest_resource.setMinimumWidth(180)
        self._fill_harvest_resources()
        self.harvest_resource.currentIndexChanged.connect(self._sync_harvest_amounts)
        harvest_row.addWidget(self.harvest_resource, 1)
        self.harvest_amount = QComboBox()
        self.harvest_amount.setFixedWidth(72)
        harvest_row.addWidget(self.harvest_amount)
        copy_harvest = QPushButton("Копіювати")
        copy_harvest.clicked.connect(self._copy_harvest)
        harvest_row.addWidget(copy_harvest)
        harvest_layout.addLayout(harvest_row)
        self.harvest_hint = QLabel("")
        self.harvest_hint.setObjectName("HintLabel")
        self.harvest_hint.setWordWrap(True)
        harvest_layout.addWidget(self.harvest_hint)
        body.addWidget(harvest)
        self._sync_harvest_amounts()

        self.list_widget = QListWidget()
        self.list_widget.setWordWrap(True)
        self.list_widget.setSpacing(2)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        body.addWidget(self.list_widget, 1)

        footer = QHBoxLayout()
        self.copied_label = QLabel(" ")
        self.copied_label.setObjectName("CopiedLabel")
        footer.addWidget(self.copied_label, 1)
        grip = QSizeGrip(self)
        footer.addWidget(grip, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        body.addLayout(footer)

        self._keep_top_timer = QTimer(self)
        self._keep_top_timer.setInterval(400)
        self._keep_top_timer.timeout.connect(self._keep_above_game)
        self._expanded_item: QListWidgetItem | None = None
        self._variant_items: list[QListWidgetItem] = []
        self._search_query = ""

        self._rebuild_list()
        if place_on_screen:
            self._place_on_screen()
        self._auto_install_run_scripts()

    def _keep_above_game(self) -> None:
        if self.isVisible():
            pin_overlay(self, bring_front=False)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        pin_overlay(self)
        self._keep_top_timer.start()

    def hideEvent(self, event: QHideEvent) -> None:
        self._keep_top_timer.stop()
        super().hideEvent(event)

    def _set_opacity(self, value: int) -> None:
        self.setWindowOpacity(max(0.4, value / 100))

    def _place_on_screen(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        self.move(geo.right() - self.width() - 24, geo.top() + 80)

    def _build_run_menu(self) -> None:
        run_menu = self.menu_bar.addMenu("Run")
        install_action = run_menu.addAction("Встановити файли у Stellaris")
        install_action.triggered.connect(self._install_run_scripts)
        if self._cheat_source is None:
            worlds = self.menu_bar.addMenu("Світи 78")
            open_action = worlds.addAction("Відкрити окреме вікно")
            open_action.triggered.connect(self._open_special)
        else:
            self._build_orbit_menu()

    def _build_orbit_menu(self) -> None:
        orbit = self.menu_bar.addMenu("Орбіта")
        for command, title in (
            (run_command("orbital_resources_300.txt"), "Mining 300"),
            (run_command("orbital_resources_3000.txt"), "Mining 3000"),
            (run_command("orbital_energy_10000.txt"), "Енергія 10000"),
            (run_command("orbital_energy_100000.txt"), "Енергія 100000"),
            (run_command("orbital_science_500.txt"), "Science 500×3"),
            (run_command("orbital_science_5000.txt"), "Science 5000×3"),
            (run_command("orbital_special_mining_100.txt"), "Спец. mining 100"),
            (run_command("orbital_special_mining_1000.txt"), "Спец. mining 1000"),
            (run_command("orbital_special_research_100.txt"), "Спец. research 100"),
            (run_command("orbital_special_research_1000.txt"), "Спец. research 1000"),
        ):
            action = orbit.addAction(title)
            action.setToolTip(command)
            action.triggered.connect(lambda _checked=False, cmd=command: self._copy_command(cmd))
        orbit.addSeparator()
        last_category = ""
        for resource in HARVEST_RESOURCES:
            if resource.category != last_category:
                if last_category:
                    orbit.addSeparator()
                last_category = resource.category
            amount = resource.amounts[-1] if resource.amounts else None
            command = resource.command(amount)
            action = orbit.addAction(f"{resource.category}: {resource.label}")
            action.setToolTip(command)
            action.triggered.connect(lambda _checked=False, cmd=command: self._copy_command(cmd))

    def _open_special(self) -> None:
        if self._cheat_source is not None:
            return
        if self._special is None:
            self._special = CheatOverlay(
                title="Світи 78",
                cheats=SPECIAL_WINDOW_CHEATS,
                hint=(
                    "1 Гея  2 Еку  3 Специфічні технології  4 Run · Орбітальні депозити "
                    "(300 / science 500 / спец mining / спец research)  "
                    "5 Трейти попів (add_trait_species 357 …; debugtooltip на расу). "
                    "Комбо зверху — як у базовому віджеті."
                ),
                place_on_screen=False,
            )
            self._special.resize(460, 580)
            geo = self.frameGeometry()
            self._special.move(max(24, geo.left() - self._special.width() - 12), geo.top())
        self._special.show()
        self._special.raise_()
        pin_overlay(self._special)

    def _auto_install_run_scripts(self) -> None:
        try:
            dest, count = install_run_scripts()
        except Exception:
            return
        self.copied_label.setText(f"Run-файли ({count}) → {dest}")

    def _install_run_scripts(self) -> None:
        try:
            dest, count = install_run_scripts()
        except Exception as error:
            QMessageBox.warning(self, "Run-файли", str(error))
            return
        self.copied_label.setText(f"Встановлено {count} файлів у {dest}")
        QMessageBox.information(
            self,
            "Run-файли",
            f"Скопійовано {count} файлів у\n{dest}\n\nУ консолі Stellaris: run filename.txt",
        )

    def _parent_text(self, cheat: Cheat, opened: bool) -> str:
        arrow = "▾" if opened else "▸"
        extra = f"  ({len(cheat.variants)})" if cheat.variants else ""
        return f"{arrow}  {cheat.command}{extra}\n{cheat.title} — {cheat.description}"

    def _leaf_text(self, cheat: Cheat) -> str:
        return f"{cheat.command}\n{cheat.title} — {cheat.description}"

    def _variant_text(self, cheat: Cheat) -> str:
        detail = f" — {cheat.description}" if cheat.description else ""
        return f"    {cheat.command}\n    {cheat.title}{detail}"

    def _rebuild_list(self, query: str = "") -> None:
        self._expanded_item = None
        self._variant_items = []
        self._search_query = query
        self.list_widget.clear()
        cheats = filter_cheats(query, self._cheat_source)
        current_category = ""
        auto_expand: list[Cheat] = []
        for cheat in cheats:
            if cheat.category != current_category:
                current_category = cheat.category
                header = QListWidgetItem(f"▸  {current_category}")
                header.setFlags(Qt.ItemFlag.NoItemFlags)
                header.setForeground(Qt.GlobalColor.cyan)
                header.setData(Qt.ItemDataRole.UserRole + 1, "header")
                self.list_widget.addItem(header)
            if cheat.variants:
                item = QListWidgetItem(self._parent_text(cheat, opened=False))
                item.setData(Qt.ItemDataRole.UserRole, cheat)
                item.setData(Qt.ItemDataRole.UserRole + 1, "parent")
                item.setToolTip("Клік відкриває всі варіанти")
                self.list_widget.addItem(item)
                if query.strip():
                    auto_expand.append(cheat)
            else:
                item = QListWidgetItem(self._leaf_text(cheat))
                item.setData(Qt.ItemDataRole.UserRole, cheat)
                item.setData(Qt.ItemDataRole.UserRole + 1, "leaf")
                item.setToolTip(f"{cheat.command}\n\n{cheat.description}")
                self.list_widget.addItem(item)
        if not cheats:
            empty = QListWidgetItem("Нічого не знайдено")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(empty)
        if auto_expand:
            for cheat in auto_expand:
                parent = self._find_parent_item(cheat)
                if parent is not None:
                    self._expand_parent(parent, cheat)

    def _find_parent_item(self, cheat: Cheat) -> QListWidgetItem | None:
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            if item is None:
                continue
            if item.data(Qt.ItemDataRole.UserRole + 1) == "parent":
                stored = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(stored, Cheat) and stored.command == cheat.command and stored.title == cheat.title:
                    return item
        return None

    def _collapse(self) -> None:
        for variant_item in self._variant_items:
            row = self.list_widget.row(variant_item)
            if row >= 0:
                self.list_widget.takeItem(row)
        self._variant_items = []
        if self._expanded_item is not None:
            cheat = self._expanded_item.data(Qt.ItemDataRole.UserRole)
            if isinstance(cheat, Cheat):
                self._expanded_item.setText(self._parent_text(cheat, opened=False))
        self._expanded_item = None

    def _expand_parent(self, parent: QListWidgetItem, cheat: Cheat) -> None:
        if self._expanded_item is parent:
            return
        self._collapse()
        parent.setText(self._parent_text(cheat, opened=True))
        row = self.list_widget.row(parent)
        for offset, variant in enumerate(cheat.variants, start=1):
            item = QListWidgetItem(self._variant_text(variant))
            item.setData(Qt.ItemDataRole.UserRole, variant)
            item.setData(Qt.ItemDataRole.UserRole + 1, "variant")
            item.setForeground(QColor("#c8fff6"))
            item.setToolTip(f"{variant.command}\n\n{variant.description}")
            self.list_widget.insertItem(row + offset, item)
            self._variant_items.append(item)
        self._expanded_item = parent

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        kind = item.data(Qt.ItemDataRole.UserRole + 1)
        cheat = item.data(Qt.ItemDataRole.UserRole)
        if kind == "parent" and isinstance(cheat, Cheat):
            self._copy_command(cheat.command)
            if self._expanded_item is item:
                self._collapse()
            else:
                self._expand_parent(item, cheat)
                self.list_widget.scrollToItem(item)
            return
        if isinstance(cheat, Cheat):
            self._copy_command(cheat.command)

    def _copy_command(self, command: str) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(command)
        self.copied_label.setText(f"Скопійовано: {command}")

    def _fill_harvest_resources(self) -> None:
        last_category = ""
        for resource in HARVEST_RESOURCES:
            if resource.category != last_category:
                if last_category:
                    self.harvest_resource.insertSeparator(self.harvest_resource.count())
                last_category = resource.category
            self.harvest_resource.addItem(f"{resource.category}: {resource.label}", resource)

    def _current_harvest(self) -> HarvestResource | None:
        data = self.harvest_resource.currentData()
        return data if isinstance(data, HarvestResource) else None

    def _sync_harvest_amounts(self) -> None:
        resource = self._current_harvest()
        self.harvest_amount.blockSignals(True)
        self.harvest_amount.clear()
        if resource is None:
            self.harvest_amount.setEnabled(False)
            self.harvest_hint.setText("")
            self.harvest_amount.blockSignals(False)
            return
        station = "research station" if resource.station == "research" else "mining station"
        if resource.fixed_id or not resource.amounts:
            self.harvest_amount.addItem("—")
            self.harvest_amount.setEnabled(False)
            self.harvest_hint.setText(f"Фіксований депозит. Потрібна {station}.")
        else:
            self.harvest_amount.setEnabled(True)
            for amount in resource.amounts:
                self.harvest_amount.addItem(f"×{amount}", amount)
            self.harvest_amount.setCurrentIndex(self.harvest_amount.count() - 1)
            self.harvest_hint.setText(f"Потрібна {station}. Mining і research на одному тілі не мішай.")
        self.harvest_amount.blockSignals(False)

    def _copy_harvest(self) -> None:
        resource = self._current_harvest()
        if resource is None:
            return
        amount = self.harvest_amount.currentData()
        command = resource.command(amount if isinstance(amount, int) else None)
        self._copy_command(command)

    def hide(self) -> None:
        was_visible = self.isVisible()
        super().hide()
        if was_visible:
            self.closed.emit()

    def shutdown(self) -> None:
        if self._special is not None:
            self._special.shutdown()
            self._special = None
        self._force_close = True
        self.close()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._force_close:
            event.accept()
            return
        event.ignore()
        self.hide()
