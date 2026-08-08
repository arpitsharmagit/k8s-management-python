"""Dark QSS theme — VS Code / JetBrains-inspired dark palette."""

DARK_THEME = """
/* ─── Global ─────────────────────────────────────────────────────────────── */
QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: "Inter", "Segoe UI", "Ubuntu", sans-serif;
    font-size: 13px;
    selection-background-color: #388bfd;
    selection-color: #ffffff;
}

QMainWindow {
    background-color: #0d1117;
}

/* ─── Sidebar / Navigation ────────────────────────────────────────────────── */
QListWidget {
    background-color: #161b22;
    border: none;
    border-right: 1px solid #30363d;
    outline: none;
}
QListWidget::item {
    padding: 12px 16px;
    border-radius: 6px;
    margin: 2px 6px;
    color: #8b949e;
    font-weight: 500;
}
QListWidget::item:selected, QListWidget::item:hover {
    background-color: #21262d;
    color: #e6edf3;
}
QListWidget::item:selected {
    color: #79c0ff;
    background-color: #1f3358;
}

/* ─── Tab Widget / Stack ──────────────────────────────────────────────────── */
QStackedWidget {
    background-color: #0d1117;
}

/* ─── Toolbar / Header ────────────────────────────────────────────────────── */
QFrame#topbar {
    background-color: #161b22;
    border-bottom: 1px solid #30363d;
}

/* ─── Tables ──────────────────────────────────────────────────────────────── */
QTableWidget, QTableView {
    background-color: #161b22;
    alternate-background-color: #1c2128;
    border: 1px solid #30363d;
    border-radius: 6px;
    gridline-color: #21262d;
    selection-background-color: #1f3358;
    selection-color: #e6edf3;
}
QHeaderView::section {
    background-color: #21262d;
    color: #8b949e;
    padding: 6px 10px;
    border: none;
    border-right: 1px solid #30363d;
    border-bottom: 1px solid #30363d;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
QTableWidget::item, QTableView::item {
    padding: 6px 10px;
}

/* ─── Text Edit (Log viewer) ──────────────────────────────────────────────── */
QTextEdit, QPlainTextEdit {
    background-color: #0d1117;
    color: #7ee787;
    border: 1px solid #30363d;
    border-radius: 6px;
    font-family: "JetBrains Mono", "Cascadia Code", "Fira Code", monospace;
    font-size: 12px;
    padding: 8px;
}

/* ─── Buttons ─────────────────────────────────────────────────────────────── */
QPushButton {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
}
QPushButton:pressed {
    background-color: #161b22;
}
QPushButton#btn-primary {
    background-color: #1f6feb;
    border-color: #388bfd;
    color: white;
}
QPushButton#btn-primary:hover {
    background-color: #388bfd;
}
QPushButton#btn-danger {
    background-color: #da3633;
    border-color: #f85149;
    color: white;
}

/* ─── Spin Box ────────────────────────────────────────────────────────────── */
QSpinBox {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 10px;
    min-width: 70px;
}
QSpinBox:focus { border-color: #388bfd; }

/* ─── Combo Box ───────────────────────────────────────────────────────────── */
QComboBox {
    background-color: #21262d;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    selection-background-color: #1f3358;
}

/* ─── Status Bar ──────────────────────────────────────────────────────────── */
QStatusBar {
    background-color: #161b22;
    border-top: 1px solid #30363d;
    color: #8b949e;
    font-size: 11px;
}

/* ─── Scroll Bars ─────────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #161b22;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background: #484f58; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #161b22;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #30363d;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover { background: #484f58; }

/* ─── Splitter ────────────────────────────────────────────────────────────── */
QSplitter::handle { background: #30363d; width: 1px; height: 1px; }

/* ─── Labels ──────────────────────────────────────────────────────────────── */
QLabel#section-title {
    color: #e6edf3;
    font-size: 15px;
    font-weight: 700;
}
QLabel#status-online  { color: #3fb950; font-weight: 600; }
QLabel#status-offline { color: #f85149; font-weight: 600; }
QLabel#muted { color: #8b949e; font-size: 12px; }
"""
