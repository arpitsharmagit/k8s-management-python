"""UI Panel — Node Logs viewer using QTextEdit with pod selector."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.application.k8s_service import k8s_service
from app.config import settings
from app.ui.workers.base_worker import BaseWorker
from app.ui.workers.k8s_workers import LogsWorker, NodesWorker


class LogsPanel(QWidget):
    """Node Logs panel — shows pod logs from the selected pod."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._pods: list = []
        self._log_worker: LogsWorker | None = None
        self._pods_worker: NodesWorker | None = None
        self._setup_ui()
        self._load_pods()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # Header
        header = QHBoxLayout()
        title = QLabel("Node / Pod Logs")
        title.setObjectName("section-title")
        header.addWidget(title)
        header.addStretch()
        root.addLayout(header)

        # Controls
        controls = QHBoxLayout()
        pod_label = QLabel("Pod:")
        pod_label.setObjectName("muted")
        self._pod_combo = QComboBox()
        self._pod_combo.setMinimumWidth(280)
        self._pod_combo.setPlaceholderText("Select a pod…")

        self._fetch_btn = QPushButton("▶  Fetch Logs")
        self._fetch_btn.setObjectName("btn-primary")
        self._fetch_btn.clicked.connect(self._fetch_logs)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self._clear_logs)

        self._status_lbl = QLabel("Select a pod and click Fetch Logs.")
        self._status_lbl.setObjectName("muted")

        controls.addWidget(pod_label)
        controls.addWidget(self._pod_combo)
        controls.addWidget(self._fetch_btn)
        controls.addWidget(self._clear_btn)
        controls.addStretch()
        controls.addWidget(self._status_lbl)
        root.addLayout(controls)

        # Log output
        self._log_view = QTextEdit()
        self._log_view.setReadOnly(True)
        self._log_view.setPlaceholderText(
            "Logs will appear here after selecting a pod and clicking 'Fetch Logs'."
        )
        root.addWidget(self._log_view)

    def _load_pods(self) -> None:
        """Populate the pod combo box via a background worker."""
        worker = BaseWorker(
            fn=k8s_service.list_pods,
            fn_kwargs={"namespace": settings.K8S_NAMESPACE},
            parent=self,
        )
        worker.result_ready.connect(self._on_pods_loaded)
        worker.start()

    def _on_pods_loaded(self, pods) -> None:
        self._pods = pods
        self._pod_combo.clear()
        for pod in pods:
            self._pod_combo.addItem(f"{pod.namespace}/{pod.name}", userData=(pod.name, pod.namespace))
        self._status_lbl.setText(f"Loaded {len(pods)} pods.")

    def _fetch_logs(self) -> None:
        if self._log_worker and self._log_worker.isRunning():
            return
        idx = self._pod_combo.currentIndex()
        if idx < 0:
            self._status_lbl.setText("⚠ Please select a pod first.")
            return

        pod_name, namespace = self._pod_combo.currentData()
        self._status_lbl.setText(f"Fetching logs for {namespace}/{pod_name}…")
        self._fetch_btn.setEnabled(False)

        self._log_worker = LogsWorker(pod_name=pod_name, namespace=namespace, parent=self)
        self._log_worker.result_ready.connect(self._on_logs_ready)
        self._log_worker.error_occurred.connect(self._on_error)
        self._log_worker.finished.connect(lambda: self._fetch_btn.setEnabled(True))
        self._log_worker.start()

    def _on_logs_ready(self, log_text: str) -> None:
        self._log_view.setPlainText(log_text)
        # Scroll to bottom
        sb = self._log_view.verticalScrollBar()
        sb.setValue(sb.maximum())
        self._status_lbl.setText("✓ Logs loaded.")
        self._status_lbl.setStyleSheet("color: #3fb950;")

    def _on_error(self, err: str) -> None:
        self._log_view.setPlainText(f"[Error]\n{err}")
        self._status_lbl.setText(f"Error: {err[:60]}")
        self._status_lbl.setStyleSheet("color: #f85149;")

    def _clear_logs(self) -> None:
        self._log_view.clear()
        self._status_lbl.setText("Cleared.")
        self._status_lbl.setStyleSheet("")
