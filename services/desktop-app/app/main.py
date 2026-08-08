"""Desktop App — Entry Point."""
from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from app.config import settings
from app.theme import DARK_THEME
from app.ui.main_window import MainWindow

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("K8s Fleet Manager")
    app.setOrganizationName("IoT Platform Suite")
    app.setStyleSheet(DARK_THEME)

    window = MainWindow()
    window.show()

    logger.info("K8s Desktop App started.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
