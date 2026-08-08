"""UI — Main Window: QMainWindow with left-side navigation panel."""
from __future__ import annotations

import logging

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QWidget,
)

from app.ui.panels.cluster_panel import ClusterPanel
from app.ui.panels.deployments_panel import DeploymentsPanel
from app.ui.panels.logs_panel import LogsPanel
from app.ui.panels.pods_panel import PodsPanel

logger = logging.getLogger(__name__)


NAV_ITEMS = [
    ("🖥️  Cluster Health",     ClusterPanel),
    ("📦  Pod Status",          PodsPanel),
    ("⚖️  Deployments",         DeploymentsPanel),
    ("📋  Node Logs",           LogsPanel),
]


class MainWindow(QMainWindow):
    """Application main window with a left navigation list and a QStackedWidget."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("K8s Fleet Manager — IoT Platform Suite")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 780)
        self._panels: list[QWidget] = []
        self._setup_ui()
        self._setup_statusbar()
        logger.info("Main window initialised.")

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        h_layout = QHBoxLayout(central)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)

        # ── Left navigation ──────────────────────────────────────────────────
        nav_container = QWidget()
        nav_container.setFixedWidth(220)
        nav_container.setObjectName("nav-container")
        nav_container.setStyleSheet("""
            QWidget#nav-container {
                background-color: #161b22;
                border-right: 1px solid #30363d;
            }
        """)
        from PySide6.QtWidgets import QVBoxLayout
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        # Brand header
        brand = QLabel("  ⚡  K8s Manager")
        brand.setStyleSheet("""
            padding: 18px 16px;
            font-size: 15px;
            font-weight: 700;
            color: #e6edf3;
            border-bottom: 1px solid #30363d;
        """)
        nav_layout.addWidget(brand)

        # Nav list
        self._nav_list = QListWidget()
        self._nav_list.setObjectName("nav-list")
        self._nav_list.setSpacing(2)
        self._nav_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._nav_list.currentRowChanged.connect(self._on_nav_changed)

        for label, PanelClass in NAV_ITEMS:
            item = QListWidgetItem(label)
            item.setSizeHint(QSize(200, 42))
            self._nav_list.addItem(item)
            panel = PanelClass()
            self._panels.append(panel)

        nav_layout.addWidget(self._nav_list)
        nav_layout.addStretch()

        # Footer
        footer = QLabel("  Kubernetes Python SDK")
        footer.setStyleSheet("color: #484f58; font-size: 11px; padding: 10px 16px;")
        nav_layout.addWidget(footer)

        h_layout.addWidget(nav_container)

        # ── Stack ─────────────────────────────────────────────────────────────
        self._stack = QStackedWidget()
        for panel in self._panels:
            self._stack.addWidget(panel)
        h_layout.addWidget(self._stack)

        # Select first item
        self._nav_list.setCurrentRow(0)

    def _on_nav_changed(self, row: int) -> None:
        if 0 <= row < len(self._panels):
            self._stack.setCurrentIndex(row)
            self.setWindowTitle(
                f"K8s Fleet Manager — {NAV_ITEMS[row][0].strip()}"
            )

    def _setup_statusbar(self) -> None:
        bar = QStatusBar()
        bar.showMessage("Connected to Kubernetes cluster — auto-refresh enabled")
        self.setStatusBar(bar)
