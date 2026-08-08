"""UI Panel — Deployment Scaling with inline replica control."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.k8s_service import DeploymentInfo, k8s_service
from app.config import settings
from app.ui.workers.base_worker import BaseWorker
from app.ui.workers.k8s_workers import DeploymentsWorker

HEADERS = ["Name", "Namespace", "Ready", "Up-to-Date", "Available", "Desired", "Scale To"]


class ScaleWorker(BaseWorker):
    def __init__(self, name: str, namespace: str, replicas: int, parent=None):
        super().__init__(
            fn=k8s_service.scale_deployment,
            fn_kwargs={"name": name, "namespace": namespace, "replicas": replicas},
            parent=parent,
        )


class DeploymentsPanel(QWidget):
    """Deployment Scaling panel — list of deployments with inline scale control."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._worker: DeploymentsWorker | None = None
        self._deployments: list[DeploymentInfo] = []
        self._setup_ui()
        self._start_auto_refresh()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("Deployment Scaling")
        title.setObjectName("section-title")
        self._status_lbl = QLabel("Loading…")
        self._status_lbl.setObjectName("muted")
        self._refresh_btn = QPushButton("⟳  Refresh")
        self._refresh_btn.setFixedWidth(100)
        self._refresh_btn.clicked.connect(self.refresh)

        header.addWidget(title)
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
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        root.addWidget(self._table)

    def refresh(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self._refresh_btn.setEnabled(False)
        self._status_lbl.setText("Fetching…")
        self._worker = DeploymentsWorker(parent=self)
        self._worker.result_ready.connect(self._on_result)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.finished.connect(lambda: self._refresh_btn.setEnabled(True))
        self._worker.start()

    def _on_result(self, deployments: list[DeploymentInfo]) -> None:
        self._deployments = deployments
        self._table.setRowCount(len(deployments))
        for row, dep in enumerate(deployments):
            values = [
                dep.name, dep.namespace, dep.ready,
                str(dep.up_to_date), str(dep.available), str(dep.desired),
            ]
            for col, val in enumerate(values):
                self._table.setItem(row, col, QTableWidgetItem(val))

            # Scale control in last column
            scale_widget = QWidget()
            h = QHBoxLayout(scale_widget)
            h.setContentsMargins(4, 2, 4, 2)
            h.setSpacing(6)
            spin = QSpinBox()
            spin.setRange(0, 50)
            spin.setValue(dep.desired)
            spin.setFixedWidth(60)
            btn = QPushButton("Scale")
            btn.setObjectName("btn-primary")
            btn.setFixedWidth(56)
            btn.clicked.connect(self._make_scale_handler(dep, spin))
            h.addWidget(spin)
            h.addWidget(btn)
            self._table.setCellWidget(row, len(HEADERS) - 1, scale_widget)

        self._table.resizeColumnsToContents()
        self._status_lbl.setText("✓ Live")
        self._status_lbl.setStyleSheet("color: #3fb950;")

    def _make_scale_handler(self, dep: DeploymentInfo, spin: QSpinBox):
        def _handler():
            worker = ScaleWorker(
                name=dep.name,
                namespace=dep.namespace,
                replicas=spin.value(),
                parent=self,
            )
            worker.result_ready.connect(lambda _: self.refresh())
            worker.error_occurred.connect(
                lambda err: self._status_lbl.setText(f"Scale error: {err[:50]}")
            )
            worker.start()
        return _handler

    def _on_error(self, err: str) -> None:
        self._status_lbl.setText(f"Error: {err[:60]}")
        self._status_lbl.setStyleSheet("color: #f85149;")

    def _start_auto_refresh(self) -> None:
        self._timer = QTimer(self)
        self._timer.setInterval(settings.REFRESH_INTERVAL_SECONDS * 1000)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        self.refresh()
