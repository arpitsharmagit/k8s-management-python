"""UI Panel — Pod Status viewer with sortable QTableWidget."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.k8s_service import PodInfo
from app.config import settings
from app.ui.workers.k8s_workers import PodsWorker

HEADERS = ["Name", "Namespace", "Status", "Ready", "Restarts", "Node", "Age"]
STATUS_COLORS = {
    "Running": "#3fb950",
    "Pending": "#d29922",
    "Failed":  "#f85149",
    "Succeeded": "#58a6ff",
    "Unknown": "#8b949e",
}


class PodsPanel(QWidget):
    """Pod Status panel — live pod table with status colour coding."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._worker: PodsWorker | None = None
        self._setup_ui()
        self._start_auto_refresh()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("Pod Status")
        title.setObjectName("section-title")
        self._count_lbl = QLabel("")
        self._count_lbl.setObjectName("muted")
        self._status_lbl = QLabel("Loading…")
        self._status_lbl.setObjectName("muted")
        self._refresh_btn = QPushButton("⟳  Refresh")
        self._refresh_btn.setFixedWidth(100)
        self._refresh_btn.clicked.connect(self.refresh)

        header.addWidget(title)
        header.addWidget(self._count_lbl)
        header.addStretch()
        header.addWidget(self._status_lbl)
        header.addWidget(self._refresh_btn)
        root.addLayout(header)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(len(HEADERS))
        self._table.setHorizontalHeaderLabels(HEADERS)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSortingEnabled(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        root.addWidget(self._table)

    def refresh(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._refresh_btn.setEnabled(False)
        self._status_lbl.setText("Fetching…")
        self._worker = PodsWorker(parent=self)
        self._worker.result_ready.connect(self._on_result)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.finished.connect(lambda: self._refresh_btn.setEnabled(True))
        self._worker.start()

    def _on_result(self, pods: list[PodInfo]) -> None:
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(pods))
        for row, pod in enumerate(pods):
            values = [
                pod.name, pod.namespace, pod.status,
                pod.ready, str(pod.restarts), pod.node, pod.age,
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                if col == 2:  # Status column
                    color = STATUS_COLORS.get(pod.status, "#8b949e")
                    item.setForeground(Qt.GlobalColor.white)
                    item.setBackground(__import__("PySide6.QtGui", fromlist=["QColor"]).QColor(color).darker(200))
                self._table.setItem(row, col, item)
        self._table.setSortingEnabled(True)
        self._table.resizeColumnsToContents()
        self._count_lbl.setText(f"({len(pods)} pods)")
        self._status_lbl.setText("✓ Live")
        self._status_lbl.setStyleSheet("color: #3fb950;")

    def _on_error(self, err: str) -> None:
        self._status_lbl.setText(f"Error: {err[:60]}")
        self._status_lbl.setStyleSheet("color: #f85149;")

    def _start_auto_refresh(self) -> None:
        self._timer = QTimer(self)
        self._timer.setInterval(settings.REFRESH_INTERVAL_SECONDS * 1000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        self.refresh()
