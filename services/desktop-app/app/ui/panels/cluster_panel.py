"""UI Panel — Cluster Health overview with live stat cards."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.application.k8s_service import ClusterHealth
from app.config import settings
from app.ui.workers.k8s_workers import ClusterHealthWorker


class StatCard(QFrame):
    """A single metric card with icon, value, and label."""

    def __init__(self, icon: str, label: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("stat-card")
        self.setMinimumSize(160, 100)
        self.setStyleSheet("""
            QFrame#stat-card {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
            QFrame#stat-card:hover {
                border-color: #388bfd;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 22px;")
        self._value_lbl = QLabel("—")
        self._value_lbl.setStyleSheet("font-size: 26px; font-weight: 700; color: #e6edf3;")
        label_lbl = QLabel(label)
        label_lbl.setObjectName("muted")

        layout.addWidget(icon_lbl)
        layout.addWidget(self._value_lbl)
        layout.addWidget(label_lbl)

    def set_value(self, val: str | int) -> None:
        self._value_lbl.setText(str(val))


class ClusterPanel(QWidget):
    """Cluster Health panel — shows node/pod counts via live stat cards."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._worker: ClusterHealthWorker | None = None
        self._setup_ui()
        self._start_auto_refresh()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Cluster Health")
        title.setObjectName("section-title")
        self._status_lbl = QLabel("Refreshing…")
        self._status_lbl.setObjectName("muted")

        self._refresh_btn = QPushButton("⟳  Refresh")
        self._refresh_btn.setFixedWidth(100)
        self._refresh_btn.clicked.connect(self.refresh)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self._status_lbl)
        header.addWidget(self._refresh_btn)
        root.addLayout(header)

        # Stat cards
        grid = QGridLayout()
        grid.setSpacing(12)
        self._card_total_nodes  = StatCard("🖥️", "Total Nodes")
        self._card_ready_nodes  = StatCard("🟢", "Ready Nodes")
        self._card_total_pods   = StatCard("📦", "Total Pods")
        self._card_running_pods = StatCard("▶️", "Running Pods")
        self._card_namespaces   = StatCard("📂", "Namespaces")

        cards = [
            self._card_total_nodes, self._card_ready_nodes,
            self._card_total_pods, self._card_running_pods,
            self._card_namespaces,
        ]
        for i, card in enumerate(cards):
            grid.addWidget(card, i // 3, i % 3)

        root.addLayout(grid)
        root.addStretch()

    def refresh(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._status_lbl.setText("Fetching…")
        self._refresh_btn.setEnabled(False)
        self._worker = ClusterHealthWorker(parent=self)
        self._worker.result_ready.connect(self._on_result)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.finished.connect(lambda: self._refresh_btn.setEnabled(True))
        self._worker.start()

    def _on_result(self, health: ClusterHealth) -> None:
        self._card_total_nodes.set_value(health.node_count)
        self._card_ready_nodes.set_value(health.ready_nodes)
        self._card_total_pods.set_value(health.pod_count)
        self._card_running_pods.set_value(health.running_pods)
        self._card_namespaces.set_value(health.namespace_count)
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
