"""QThread base worker — provides the generic worker pattern used by all K8s panels."""
from __future__ import annotations

import logging
from typing import Any, Callable

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class BaseWorker(QThread):
    """Generic QThread that runs a callable and emits result or error signals.

    Usage:
        worker = BaseWorker(fn=k8s_service.list_pods, fn_kwargs={"namespace": "default"})
        worker.result_ready.connect(my_slot)
        worker.error_occurred.connect(my_error_slot)
        worker.start()
    """

    result_ready = Signal(object)       # Emits the return value of fn
    error_occurred = Signal(str)        # Emits error message string
    started_loading = Signal()          # Emits before fn is called

    def __init__(self, fn: Callable, fn_kwargs: dict | None = None, parent=None) -> None:
        super().__init__(parent)
        self._fn = fn
        self._fn_kwargs = fn_kwargs or {}

    def run(self) -> None:
        self.started_loading.emit()
        try:
            result = self._fn(**self._fn_kwargs)
            self.result_ready.emit(result)
        except Exception as exc:
            logger.error("Worker error in %s: %s", self._fn.__name__, exc, exc_info=True)
            self.error_occurred.emit(str(exc))
