"""
Vue du module Fichier.
Import/Export CSV, Sauvegarde et Restauration.
Emplacement: src/ui/views/file_view.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QFileDialog,
    QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont


class FileView(QWidget):
    """Vue principale du module Fichier."""

    version = "1.0.0"

    # Signaux
    import_csv_requested    = Signal(str)   # chemin du fichier
    export_csv_requested    = Signal(str)   # chemin de destination
    create_backup_requested = Signal()
    restore_backup_requested = Signal(str)  # chemin de la sauvegarde
    delete_backup_requested  = Signal(str)  # chemin de la sauvegarde
    refresh_backups_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._backup_data = []   # cache de la liste des sauvegardes
        self.init_ui()

    # ------------------------------------------------------------------
    # Construction UI
    # ------------------------------------------------------------------

    def init_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(25, 25, 25, 25)
        root.setSpacing(20)

        # En-tête
        root.addLayout(self._make_header())

        # Deux colonnes : Import/Export | Sauvegarde/Restauration
        cols = QHBoxLayout()
        cols.setSpacing(20)
        cols.addWidget(self._make_csv_group(), 1)
        cols.addWidget(self._make_backup_group(), 1)
        root.addLayout(cols)

        root.addStretch()
        self.setLayout(root)

    def _make_header(self) -> QHBoxLayout:
        lay = QHBoxLayout()

        title = QLabel("Gestion des Fichiers")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: palette(text);")

        subtitle = QLabel("Import/Export CSV  |  Sauvegarde et Restauration")
        subtitle.setStyleSheet("font-size: 13px; color: #7f8c8d;")

        v = QVBoxLayout()
        v.setSpacing(2)
        v.addWidget(title)
        v.addWidget(subtitle)

        lay.addLayout(v)
        lay.addStretch()
        return lay

    # ── CSV ────────────────────────────────────────────────────────────

    def _make_csv_group(self) -> QGroupBox:
        grp = QGroupBox("Import / Export Stock (CSV)")
        grp.setStyleSheet(self._group_style("#3498db"))

        lay = QVBoxLayout()
        lay.setSpacing(18)
        lay.setContentsMargins(18, 20, 18, 18)

        # -- IMPORT --
        imp_title = QLabel("Importer le stock depuis un CSV")
        imp_title.setStyleSheet("font-size: 14px; font-weight: bold; color: palette(text);")
        lay.addWidget(imp_title)

        # Sélecteur de fichier
        file_row = QHBoxLayout()
        self.import_path_input = QLineEdit()
        self.import_path_input.setPlaceholderText("Sélectionner un fichier .csv …")
        self.import_path_input.setReadOnly(True)
        self.import_path_input.setStyleSheet(self._input_style())
        self.import_path_input.setMinimumHeight(40)

        browse_import = QPushButton("Parcourir")
        browse_import.setMinimumHeight(40)
        browse_import.setMinimumWidth(100)
        browse_import.setCursor(Qt.PointingHandCursor)
        browse_import.setStyleSheet(self._btn_style("#7f8c8d", "#626567"))
        browse_import.clicked.connect(self._browse_import)

        file_row.addWidget(self.import_path_input, 3)
        file_row.addWidget(browse_import, 1)
        lay.addLayout(file_row)

        # Boutons import
        imp_btns = QHBoxLayout()
        btn_import = QPushButton("Importer le stock")
        btn_import.setMinimumHeight(44)
        btn_import.setCursor(Qt.PointingHandCursor)
        btn_import.setStyleSheet(self._btn_style("#3498db", "#2980b9"))
        btn_import.clicked.connect(self._do_import)

        btn_template = QPushButton("Télécharger modèle CSV")
        btn_template.setMinimumHeight(44)
        btn_template.setCursor(Qt.PointingHandCursor)
        btn_template.setStyleSheet(self._btn_style("#9b59b6", "#8e44ad"))
        btn_template.clicked.connect(self._download_template)

        imp_btns.addWidget(btn_import)
        imp_btns.addWidget(btn_template)
        lay.addLayout(imp_btns)

        # Info format
        info = QLabel(
            "Format attendu: Nom ; Description ; Prix ; Quantité ; Catégorie\n"
            "Séparateur: point-virgule (;) — Encodage: UTF-8"
        )
        info.setStyleSheet(
            "font-size: 12px; color: #e67e22; background: #fef5e7; "
            "padding: 10px; border-radius: 6px; border-left: 3px solid #e67e22;"
        )
        info.setWordWrap(True)
        lay.addWidget(info)

        # Séparateur
        sep = QLabel()
        sep.setFixedHeight(2)
        sep.setStyleSheet("background: palette(mid);")
        lay.addWidget(sep)

        # -- EXPORT --
        exp_title = QLabel("Exporter le stock vers un CSV")
        exp_title.setStyleSheet("font-size: 14px; font-weight: bold; color: palette(text);")
        lay.addWidget(exp_title)

        dest_row = QHBoxLayout()
        self.export_path_input = QLineEdit()
        self.export_path_input.setPlaceholderText("Choisir l'emplacement d'enregistrement …")
        self.export_path_input.setReadOnly(True)
        self.export_path_input.setStyleSheet(self._input_style())
        self.export_path_input.setMinimumHeight(40)

        browse_export = QPushButton("Parcourir")
        browse_export.setMinimumHeight(40)
        browse_export.setMinimumWidth(100)
        browse_export.setCursor(Qt.PointingHandCursor)
        browse_export.setStyleSheet(self._btn_style("#7f8c8d", "#626567"))
        browse_export.clicked.connect(self._browse_export)

        dest_row.addWidget(self.export_path_input, 3)
        dest_row.addWidget(browse_export, 1)
        lay.addLayout(dest_row)

        btn_export = QPushButton("Exporter le stock")
        btn_export.setMinimumHeight(44)
        btn_export.setCursor(Qt.PointingHandCursor)
        btn_export.setStyleSheet(self._btn_style("#2ecc71", "#27ae60"))
        btn_export.clicked.connect(self._do_export)
        lay.addWidget(btn_export)

        lay.addStretch()
        grp.setLayout(lay)
        return grp

    # ── SAUVEGARDE ─────────────────────────────────────────────────────

    def _make_backup_group(self) -> QGroupBox:
        grp = QGroupBox("Sauvegarde et Restauration")
        grp.setStyleSheet(self._group_style("#e67e22"))

        lay = QVBoxLayout()
        lay.setSpacing(14)
        lay.setContentsMargins(18, 20, 18, 18)

        # Bouton nouvelle sauvegarde
        btn_backup = QPushButton("Créer une sauvegarde maintenant")
        btn_backup.setMinimumHeight(48)
        btn_backup.setCursor(Qt.PointingHandCursor)
        btn_backup.setStyleSheet(self._btn_style("#e67e22", "#d35400"))
        btn_backup.clicked.connect(lambda: self.create_backup_requested.emit())
        lay.addWidget(btn_backup)

        # Titre liste
        list_hdr = QHBoxLayout()
        list_lbl = QLabel("Sauvegardes disponibles:")
        list_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: palette(text);")

        refresh_btn = QPushButton("Actualiser")
        refresh_btn.setMaximumWidth(100)
        refresh_btn.setMaximumHeight(30)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet(self._btn_style("#95a5a6", "#7f8c8d"))
        refresh_btn.clicked.connect(lambda: self.refresh_backups_requested.emit())

        list_hdr.addWidget(list_lbl)
        list_hdr.addStretch()
        list_hdr.addWidget(refresh_btn)
        lay.addLayout(list_hdr)

        # Tableau des sauvegardes
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(3)
        self.backup_table.setHorizontalHeaderLabels(["Nom", "Date", "Taille"])
        self.backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.backup_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backup_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.backup_table.setAlternatingRowColors(True)
        self.backup_table.setMinimumHeight(180)
        self.backup_table.setStyleSheet("""
            QTableWidget { border: 2px solid palette(mid); border-radius: 8px;
                gridline-color: palette(mid); font-size: 12px; }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:selected { background: #3498db; color: white; }
            QHeaderView::section { background: palette(alternate-base);
                padding: 6px; font-weight: bold; border: none;
                border-bottom: 2px solid palette(mid); }
        """)
        lay.addWidget(self.backup_table)

        # Boutons Restaurer / Supprimer
        action_btns = QHBoxLayout()
        action_btns.setSpacing(10)

        btn_restore = QPushButton("Restaurer la sélection")
        btn_restore.setMinimumHeight(44)
        btn_restore.setCursor(Qt.PointingHandCursor)
        btn_restore.setStyleSheet(self._btn_style("#3498db", "#2980b9"))
        btn_restore.clicked.connect(self._do_restore)

        btn_delete = QPushButton("Supprimer")
        btn_delete.setMinimumHeight(44)
        btn_delete.setMaximumWidth(120)
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet(self._btn_style("#e74c3c", "#c0392b"))
        btn_delete.clicked.connect(self._do_delete)

        action_btns.addWidget(btn_restore)
        action_btns.addWidget(btn_delete)
        lay.addLayout(action_btns)

        # Info restauration
        warn = QLabel(
            "La restauration remplace la base de données actuelle.\n"
            "Une sauvegarde automatique est créée avant chaque restauration."
        )
        warn.setStyleSheet(
            "font-size: 12px; color: #c0392b; background: #fdedec; "
            "padding: 10px; border-radius: 6px; border-left: 3px solid #e74c3c;"
        )
        warn.setWordWrap(True)
        lay.addWidget(warn)

        lay.addStretch()
        grp.setLayout(lay)
        return grp

    # ------------------------------------------------------------------
    # Actions internes
    # ------------------------------------------------------------------

    def _browse_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier CSV", "",
            "CSV (*.csv);;Tous les fichiers (*)"
        )
        if path:
            self.import_path_input.setText(path)

    def _browse_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le CSV", "stock_export.csv",
            "CSV (*.csv);;Tous les fichiers (*)"
        )
        if path:
            self.export_path_input.setText(path)

    def _do_import(self):
        path = self.import_path_input.text().strip()
        if not path:
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Fichier requis", "Veuillez sélectionner un fichier CSV à importer.")
            return
        self.import_csv_requested.emit(path)

    def _do_export(self):
        path = self.export_path_input.text().strip()
        if not path:
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Destination requise", "Veuillez choisir un emplacement pour sauvegarder le CSV.")
            return
        self.export_csv_requested.emit(path)

    def _download_template(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le modèle CSV", "modele_stock.csv",
            "CSV (*.csv)"
        )
        if path:
            # Émettre vers le manager via un signal spécial
            # On passe par le parent pour appeler generate_csv_template
            parent = self.parent()
            if parent and hasattr(parent, 'modules') and 'file' in parent.modules:
                parent.modules['file'].generate_csv_template(path)

    def _do_restore(self):
        row = self.backup_table.currentRow()
        if row < 0 or row >= len(self._backup_data):
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Sélection requise", "Veuillez sélectionner une sauvegarde à restaurer.")
            return
        self.restore_backup_requested.emit(self._backup_data[row]['path'])

    def _do_delete(self):
        row = self.backup_table.currentRow()
        if row < 0 or row >= len(self._backup_data):
            from src.ui.widgets.InfoDialog import InfoDialog
            InfoDialog.warning(self, "Sélection requise", "Veuillez sélectionner une sauvegarde à supprimer.")
            return
        self.delete_backup_requested.emit(self._backup_data[row]['path'])

    # ------------------------------------------------------------------
    # Méthode publique appelée par le manager
    # ------------------------------------------------------------------

    def update_backups_list(self, backups: list):
        """Met à jour le tableau des sauvegardes."""
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

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------

    def _group_style(self, color: str) -> str:
        return f"""
            QGroupBox {{
                font-size: 15px; font-weight: bold;
                border: 2px solid {color}; border-radius: 10px;
                margin-top: 14px; padding-top: 12px;
                color: palette(text);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 4px 12px; background: palette(base);
                color: {color};
            }}
        """

    def _input_style(self) -> str:
        return """
            QLineEdit {
                font-size: 13px; padding: 8px 12px;
                border: 2px solid palette(mid); border-radius: 7px;
                background: palette(base); color: palette(text);
            }
            QLineEdit:focus { border: 2px solid #3498db; }
        """

    def _btn_style(self, bg: str, hover: str) -> str:
        return f"""
            QPushButton {{
                background: {bg}; color: white; padding: 10px 18px;
                border: none; border-radius: 8px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:pressed {{ background: {hover}; opacity: 0.8; }}
        """