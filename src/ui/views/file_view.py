"""
Vue du module Fichier.
Import/Export CSV, Sauvegarde et Restauration.
Design fin, Dark/Light automatique, scrollable.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFileDialog,
    QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFrame,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from src.utils.helpers import get_asset_path


def load_svg_icon(icon_name: str, size: int = 24) -> QPixmap:
    try:
        from src.utils.helpers import get_asset_path
        icon_path = get_asset_path("icons", f"{icon_name}.svg")
        if not icon_path.exists():
            return QPixmap()
        icon = QIcon(str(icon_path))
        return icon.pixmap(size, size) if not icon.isNull() else QPixmap()
    except:
        return QPixmap()


def _groupbox_style(accent: str) -> str:
    return f"""
        QGroupBox {{
            font-size: 15px;
            font-weight: 600;
            border: 2px solid {accent};
            border-radius: 12px;
            margin-top: 22px;
            padding-top: 18px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255,255,255,0.02), stop:1 rgba(255,255,255,0.01));
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 5px 18px;
            left: 10px;
            top: -2px;
            color: {accent};
            font-weight: 600;
            background: transparent;
        }}
    """


def _input_style() -> str:
    return """
        QLineEdit {
            font-size: 13px;
            padding: 8px 14px;
            border: 2px solid rgba(150,150,150,0.3);
            border-radius: 8px;
            min-height: 24px;
            background: rgba(255,255,255,0.03);
        }
        QLineEdit:hover {
            border: 2px solid rgba(52, 152, 219, 0.5);
        }
        QLineEdit:focus {
            border: 2px solid #3498db;
            background: rgba(52, 152, 219, 0.05);
        }
    """


def _btn(label, bg, hover, h=38, w=None, icon_name=None) -> QPushButton:
    btn = QPushButton(label)
    btn.setMinimumHeight(h)
    btn.setMaximumHeight(h)
    if w:
        btn.setMinimumWidth(w)
    btn.setCursor(Qt.PointingHandCursor)
    if icon_name:
        px = load_svg_icon(icon_name, 18)
        if not px.isNull():
            btn.setIcon(QIcon(px))
            btn.setIconSize(QSize(18, 18))
    btn.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {bg}, stop:1 {hover});
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            padding: 6px 20px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {hover}, stop:1 {bg});
        }}
        QPushButton:pressed {{
            background: {hover};
            padding-top: 7px;
            padding-bottom: 5px;
        }}
    """)
    return btn


def _browse_btn() -> QPushButton:
    """Bouton Parcourir — design moderne et visible."""
    btn = QPushButton("Parcourir")
    btn.setMinimumHeight(38)
    btn.setMaximumHeight(38)
    btn.setMinimumWidth(100)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #95a5a6, stop:1 #7f8c8d);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            padding: 6px 16px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #7f8c8d, stop:1 #95a5a6);
        }
        QPushButton:pressed {
            background: #6c7a7b;
            padding-top: 7px;
            padding-bottom: 5px;
        }
    """)
    return btn


def _info_box(text: str, accent: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet(f"""
        font-size: 12px;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid {accent};
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 rgba(230, 126, 34, 0.08), stop:1 rgba(230, 126, 34, 0.02));
        color: {accent};
        font-weight: 500;
    """)
    return lbl


class FileView(QWidget):
    """Vue principale du module Fichier — Dark/Light auto."""

    version = "1.0.0"

    import_csv_requested     = Signal(str)
    export_csv_requested     = Signal(str)
    create_backup_requested  = Signal()
    restore_backup_requested = Signal(str)
    delete_backup_requested  = Signal(str)
    refresh_backups_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._backup_data = []
        self.init_ui()

    # ──────────────────────────────────────────────────────────────────
    # INIT UI
    # ──────────────────────────────────────────────────────────────────

    def init_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(28, 24, 28, 20)
        main.setSpacing(18)

        # ── TITRE ────────────────────────────────────────────────────
        title = QLabel("Gestion des Fichiers")
        title.setStyleSheet("font-size: 28px; font-weight: 700; letter-spacing: -0.5px;")
        subtitle = QLabel("Import/Export CSV  •  Sauvegarde et Restauration")
        subtitle.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-top: 4px;")
        main.addWidget(title)
        main.addWidget(subtitle)
        
        # Espacement après le titre
        main.addSpacing(8)

        # ── SCROLL ───────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                border: none; background: rgba(52, 152, 219, 0.08);
                width: 12px; border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #3498db);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)
        scroll.viewport().setAutoFillBackground(False)

        content = QWidget()
        content.setAutoFillBackground(False)
        lay = QHBoxLayout(content)
        lay.setSpacing(20)
        lay.setContentsMargins(0, 4, 12, 4)

        lay.addWidget(self._make_csv_group(), 1)
        lay.addWidget(self._make_backup_group(), 1)

        scroll.setWidget(content)
        main.addWidget(scroll, 1)

    # ──────────────────────────────────────────────────────────────────
    # GROUPE CSV
    # ──────────────────────────────────────────────────────────────────

    def _make_csv_group(self) -> QGroupBox:
        grp = QGroupBox("Import / Export Stock (CSV)")
        grp.setStyleSheet(_groupbox_style("#3498db"))

        lay = QVBoxLayout(grp)
        lay.setSpacing(16)
        lay.setContentsMargins(20, 24, 20, 20)

        # ── IMPORT ───────────────────────────────────────────────────
        imp_lbl = QLabel("Importer depuis un fichier CSV")
        imp_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #3498db;")
        lay.addWidget(imp_lbl)

        file_row = QHBoxLayout()
        file_row.setSpacing(10)
        self.import_path_input = QLineEdit()
        self.import_path_input.setPlaceholderText("Sélectionner un fichier .csv …")
        self.import_path_input.setReadOnly(True)
        self.import_path_input.setStyleSheet(_input_style())
        bi = _browse_btn()
        bi.clicked.connect(self._browse_import)
        file_row.addWidget(self.import_path_input, 3)
        file_row.addWidget(bi, 0)
        lay.addLayout(file_row)

        imp_btns = QHBoxLayout()
        imp_btns.setSpacing(10)
        btn_import = _btn("Importer le stock",     "#3498db", "#2980b9", icon_name="upload")
        btn_tpl    = _btn("Télécharger modèle",    "#9b59b6", "#8e44ad", icon_name="download")
        btn_import.clicked.connect(self._do_import)
        btn_tpl.clicked.connect(self._download_template)
        imp_btns.addWidget(btn_import)
        imp_btns.addWidget(btn_tpl)
        lay.addLayout(imp_btns)

        lay.addWidget(_info_box(
            "Format : Nom ; Description ; Prix ; Quantité ; Catégorie\n"
            "Séparateur : point-virgule ( ; ) — Encodage : UTF-8",
            "#e67e22"
        ))

        # Séparateur moderne
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(52, 152, 219, 0), stop:0.5 rgba(52, 152, 219, 0.3), stop:1 rgba(52, 152, 219, 0));
        """)
        sep.setFixedHeight(2)
        lay.addWidget(sep)
        lay.addSpacing(4)

        # ── EXPORT ───────────────────────────────────────────────────
        exp_lbl = QLabel("Exporter le stock vers un CSV")
        exp_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #2ecc71;")
        lay.addWidget(exp_lbl)

        dest_row = QHBoxLayout()
        dest_row.setSpacing(10)
        self.export_path_input = QLineEdit()
        self.export_path_input.setPlaceholderText("Choisir l'emplacement …")
        self.export_path_input.setReadOnly(True)
        self.export_path_input.setStyleSheet(_input_style())
        be = _browse_btn()
        be.clicked.connect(self._browse_export)
        dest_row.addWidget(self.export_path_input, 3)
        dest_row.addWidget(be, 0)
        lay.addLayout(dest_row)

        btn_export = _btn("Exporter le stock", "#2ecc71", "#27ae60", icon_name="download")
        btn_export.clicked.connect(self._do_export)
        lay.addWidget(btn_export)

        lay.addStretch()
        return grp

    # ──────────────────────────────────────────────────────────────────
    # GROUPE SAUVEGARDE
    # ──────────────────────────────────────────────────────────────────

    def _make_backup_group(self) -> QGroupBox:
        grp = QGroupBox("Sauvegarde et Restauration")
        grp.setStyleSheet(_groupbox_style("#e67e22"))

        lay = QVBoxLayout(grp)
        lay.setSpacing(16)
        lay.setContentsMargins(20, 24, 20, 20)

        btn_backup = _btn("Créer une sauvegarde maintenant", "#e67e22", "#d35400",
                          h=46, icon_name="save")
        btn_backup.clicked.connect(lambda: self.create_backup_requested.emit())
        lay.addWidget(btn_backup)
        
        lay.addSpacing(4)

        # En-tête liste
        hdr = QHBoxLayout()
        lbl = QLabel("Sauvegardes disponibles :")
        lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #e67e22;")
        ref = QPushButton("Actualiser")
        ref.setMinimumHeight(32)
        ref.setMaximumHeight(32)
        ref.setMinimumWidth(100)
        ref.setCursor(Qt.PointingHandCursor)
        ref.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #95a5a6, stop:1 #7f8c8d);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7f8c8d, stop:1 #95a5a6);
            }
            QPushButton:pressed {
                background: #6c7a7b;
            }
        """)
        ref.clicked.connect(lambda: self.refresh_backups_requested.emit())
        hdr.addWidget(lbl)
        hdr.addStretch()
        hdr.addWidget(ref)
        lay.addLayout(hdr)

        # Tableau avec design moderne
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(3)
        self.backup_table.setHorizontalHeaderLabels(["Nom", "Date", "Taille"])
        self.backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.backup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backup_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.backup_table.setAlternatingRowColors(False)
        self.backup_table.setMinimumHeight(220)
        self.backup_table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
                border: 2px solid rgba(230, 126, 34, 0.3);
                border-radius: 10px;
                gridline-color: transparent;
                background: transparent;
            }
            QTableWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid rgba(230, 126, 34, 0.15);
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e67e22, stop:1 #d35400);
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e67e22, stop:1 #d35400);
                color: white;
                font-weight: 600;
                font-size: 12px;
                padding: 10px;
                border: none;
                border-right: 1px solid rgba(211, 84, 0, 0.5);
            }
            QHeaderView::section:first {
                border-top-left-radius: 8px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 8px;
                border-right: none;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(230, 126, 34, 0.08);
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e67e22, stop:1 #d35400);
                min-height: 25px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #d35400, stop:1 #e67e22);
            }
        """)
        lay.addWidget(self.backup_table)

        # Boutons actions
        act = QHBoxLayout()
        act.setSpacing(10)
        btn_restore = _btn("Restaurer la sélection", "#3498db", "#2980b9", icon_name="refresh")
        btn_delete  = _btn("Supprimer",               "#e74c3c", "#c0392b", w=120)
        btn_restore.clicked.connect(self._do_restore)
        btn_delete.clicked.connect(self._do_delete)
        act.addWidget(btn_restore)
        act.addWidget(btn_delete)
        lay.addLayout(act)

        lay.addWidget(_info_box(
            "La restauration remplace la base de données actuelle.\n"
            "Une sauvegarde automatique est créée avant chaque restauration.",
            "#e74c3c"
        ))

        lay.addStretch()
        return grp

    # ──────────────────────────────────────────────────────────────────
    # ACTIONS
    # ──────────────────────────────────────────────────────────────────

    def _browse_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier CSV", "",
            "CSV (*.csv);;Tous les fichiers (*)")
        if path:
            self.import_path_input.setText(path)

    def _browse_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le CSV", "stock_export.csv",
            "CSV (*.csv);;Tous les fichiers (*)")
        if path:
            self.export_path_input.setText(path)

    def _do_import(self):
        path = self.import_path_input.text().strip()
        if not path:
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Fichier requis",
                               "Veuillez sélectionner un fichier CSV à importer.")
            return
        self.import_csv_requested.emit(path)

    def _do_export(self):
        path = self.export_path_input.text().strip()
        if not path:
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Destination requise",
                               "Veuillez choisir un emplacement pour le CSV.")
            return
        self.export_csv_requested.emit(path)

    def _download_template(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le modèle CSV", "modele_stock.csv", "CSV (*.csv)")
        if path:
            parent = self.parent()
            if parent and hasattr(parent, 'modules') and 'file' in parent.modules:
                parent.modules['file'].generate_csv_template(path)

    def _do_restore(self):
        row = self.backup_table.currentRow()
        if row < 0 or row >= len(self._backup_data):
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Sélection requise",
                               "Veuillez sélectionner une sauvegarde à restaurer.")
            return
        self.restore_backup_requested.emit(self._backup_data[row]['path'])

    def _do_delete(self):
        row = self.backup_table.currentRow()
        if row < 0 or row >= len(self._backup_data):
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Sélection requise",
                               "Veuillez sélectionner une sauvegarde à supprimer.")
            return
        self.delete_backup_requested.emit(self._backup_data[row]['path'])

    # ──────────────────────────────────────────────────────────────────
    # MÉTHODE PUBLIQUE
    # ──────────────────────────────────────────────────────────────────

    def update_backups_list(self, backups: list):
        self._backup_data = backups
        self.backup_table.setRowCount(len(backups))
        for i, b in enumerate(backups):
            self.backup_table.setItem(i, 0, QTableWidgetItem(b['name']))
            self.backup_table.setItem(i, 1, QTableWidgetItem(b['date']))
            self.backup_table.setItem(i, 2, QTableWidgetItem(b['size']))
        if not backups:
            self.backup_table.setRowCount(1)
            empty = QTableWidgetItem("Aucune sauvegarde disponible")
            empty.setTextAlignment(Qt.AlignCenter)
            self.backup_table.setItem(0, 0, empty)
            self.backup_table.setSpan(0, 0, 1, 3)