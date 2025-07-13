# Version 1 Plutot graphsime

# import sys
# from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
# from PySide6.QtGui import QIcon, QPixmap
# from PySide6.QtCore import Qt, QSize
#
# class AccueilManager:
#     version = "1.0.0"
#
#     def __init__(self, parent=None):
#         self.parent = parent
#         self.welcome_label = None
#
#     def get_ui(self):
#         from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QSizePolicy
#         from PySide6.QtGui import QIcon, QPixmap
#         from PySide6.QtCore import Qt, QSize
#
#         widget = QWidget()
#         main_layout = QVBoxLayout()
#         main_layout.setContentsMargins(20, 20, 20, 20)
#         main_layout.setSpacing(20)
#
#         # HEADER : Avatar + Bienvenue
#         header_layout = QHBoxLayout()
#         header_layout.setSpacing(10)
#
#         avatar = QLabel()
#         avatar_pixmap = QPixmap("assets/images/avatar.jpeg")
#         if avatar_pixmap.isNull():
#             avatar.setText("No Img")  # pour debug si image manquante
#             avatar.setAlignment(Qt.AlignCenter)
#         else:
#             avatar_pixmap = avatar_pixmap.scaled(48, 48, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
#             avatar.setPixmap(avatar_pixmap)
#         avatar.setFixedSize(48, 48)
#         avatar.setStyleSheet("border-radius: 24px; border: 2px solid #1abc9c;")
#
#         texts = QVBoxLayout()
#         user_name = getattr(self.parent.current_user, "name", "Utilisateur") if self.parent else "Utilisateur"
#         user_role = getattr(self.parent.current_user, "role", "Rôle inconnu") if self.parent else "Rôle inconnu"
#         self.welcome_label = QLabel(f"Bienvenue {user_name}")
#         self.welcome_label.setStyleSheet("font-size: 20px; font-weight: bold;")
#         role_label = QLabel(f"Rôle : {user_role}")
#         role_label.setStyleSheet("font-size: 14px; color: #888;")
#         texts.addWidget(self.welcome_label)
#         texts.addWidget(role_label)
#
#         header_layout.addWidget(avatar)
#         header_layout.addLayout(texts)
#         header_layout.addStretch()
#         main_layout.addLayout(header_layout)
#
#         # Séparateur
#         separator = QFrame()
#         separator.setFrameShape(QFrame.HLine)
#         separator.setFrameShadow(QFrame.Sunken)
#         main_layout.addWidget(separator)
#
#         # Première ligne statistiques (exemple simple)
#         stats_layout_1 = QHBoxLayout()
#         stats = [
#             ("Articles en stock", "1,234", "Stable par rapport à hier", "#3498db"),
#             ("Ventes aujourd'hui", "500,000 FCFA", "↑ 10% par rapport à hier", "#2ecc71"),
#             ("Ruptures de stock", "12 articles", "3 nouvelles cette semaine", "#e74c3c"),
#         ]
#         for title, value, info, color in stats:
#             stat_frame = QFrame()
#             stat_frame.setStyleSheet(f"""
#                 background-color: {color};
#                 border-radius: 10px;
#                 padding: 15px;
#             """)
#             stat_layout = QVBoxLayout()
#             stat_title = QLabel(title)
#             stat_title.setStyleSheet("font-size: 13px; color: white; font-weight: bold;")
#             stat_value = QLabel(value)
#             stat_value.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
#             stat_info = QLabel(info)
#             stat_info.setStyleSheet("font-size: 11px; color: rgba(255, 255, 255, 0.7); font-style: italic;")
#             stat_info.setWordWrap(True)
#             stat_layout.addWidget(stat_title)
#             stat_layout.addWidget(stat_value)
#             stat_layout.addWidget(stat_info)
#             stat_frame.setLayout(stat_layout)
#             stats_layout_1.addWidget(stat_frame)
#         main_layout.addLayout(stats_layout_1)
#
#         # --- SECTION GRAPHIQUE (placeholder) ---
#         graph_frame = QFrame()
#         graph_frame.setStyleSheet("""
#             background-color: #f7f9fa;  /* fond très clair */
#             border: 1px solid #95a5a6; /* gris moyen */
#             border-radius: 10px;
#         """)
#         graph_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Fixe la hauteur
#         graph_frame.setMinimumHeight(120)  # Hauteur réduite
#         graph_label = QLabel("📊 Graphique de l'activité (placeholder)")
#         graph_label.setAlignment(Qt.AlignCenter)
#         graph_label.setStyleSheet("font-size: 18px; color: #2c3e50;")  # texte plus foncé et un peu plus grand
#         graph_layout = QVBoxLayout()
#         graph_layout.addWidget(graph_label)
#         graph_frame.setLayout(graph_layout)
#         main_layout.addWidget(graph_frame)
#
#         # Section raccourcis rapides (simple)
#         shortcuts_title = QLabel("Raccourcis rapides")
#         shortcuts_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
#         main_layout.addWidget(shortcuts_title)
#
#         shortcuts_layout = QHBoxLayout()
#         shortcuts_layout.setSpacing(15)
#         shortcuts = [
#             ("Caisse", "emblem-sales", lambda: self.parent.tab_widget.setCurrentIndex(2) if self.parent else None),
#             ("Stock", "folder-stock", lambda: self.parent.tab_widget.setCurrentIndex(1) if self.parent else None),
#             ("Rapports", "document", lambda: self.parent.tab_widget.setCurrentIndex(3) if self.parent else None),
#         ]
#         for title, icon, callback in shortcuts:
#             button = QPushButton(title)
#             button.setIcon(QIcon.fromTheme(icon))
#             button.setIconSize(QSize(24, 24))
#             button.setFixedSize(140, 42)
#             button.setStyleSheet("""
#                 QPushButton {
#                     background-color: #1abc9c;
#                     color: white;
#                     font-size: 14px;
#                     border: none;
#                     border-radius: 8px;
#                 }
#                 QPushButton:hover {
#                     background-color: #16a085;
#                 }
#             """)
#             button.clicked.connect(callback)
#             shortcuts_layout.addWidget(button)
#         main_layout.addLayout(shortcuts_layout)
#
#         main_layout.addStretch()
#         widget.setLayout(main_layout)
#         return widget
#
#     def refresh(self):
#         pass
#
# # if __name__ == "__main__":
# #     app = QApplication(sys.argv)
# #     window = ParentWindow()
# #     window.show()
# #     sys.exit(app.exec())
# #
#
#


from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QTableWidget, QTableWidgetItem,
    QRadioButton, QCheckBox, QComboBox, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QSize
import os
from src.data.data import classes_par_niveau, livres_par_classe
from src.utils.helpers import create_circular_avatar_label


class AccueilManager(QWidget):
    version = "1.0.0"

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.welcome_label = None
        self.radio_maternelle = None
        self.radio_primaire = None
        self.radio_secondaire = None
        self.checkbox_anglo = None
        self.checkbox_franco = None
        self.combo_classes = None
        self.table_widget = None
        self.active_niveau = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # HEADER : Avatar + Bienvenue
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        avatar_path = os.path.join(os.path.dirname(__file__), "../../assets/images/avatar.jpeg")
        avatar_label = create_circular_avatar_label(avatar_path, size=48)

        texts = QVBoxLayout()
        user_name = getattr(self.parent.current_user, "name", "Utilisateur") if self.parent else "Utilisateur"
        user_role = getattr(self.parent.current_user, "role", "Rôle inconnu") if self.parent else "Rôle inconnu"
        self.welcome_label = QLabel(f"Bienvenue {user_name}")
        self.welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        role_label = QLabel(f"Rôle : {user_role}")
        role_label.setStyleSheet("font-size: 16px; color: #888;")
        texts.addWidget(self.welcome_label)
        texts.addWidget(role_label)

        header_layout.addWidget(avatar_label)
        # Ajouter un espacement horizontal fixe (ex: 10 pixels)
        header_layout.addSpacerItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        header_layout.addLayout(texts)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("border: 2px solid #bdc3c7;")
        main_layout.addWidget(separator)

        # Statistiques
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        stats = [
            ("Articles en stock", "1,234", "Stable par rapport à hier", "#3498db"),
            ("Ventes aujourd'hui", "500,000 FCFA", "↑ 10% par rapport à hier", "#2ecc71"),
            ("Ruptures de stock", "12 articles", "3 nouvelles cette semaine", "#e74c3c"),
        ]
        for title, value, info, color in stats:
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                background-color: {color};
                border-radius: 12px;
                padding: 4px;  /* On remet un padding un peu plus grand pour l'espacement */
                border: 2px solid #fff;
            """)
            # On ajuste la hauteur fixe. Essayer 100px ou 110px.
            # 100px est un bon point de départ avec les nouvelles tailles de police.
            stat_frame.setFixedHeight(120)  # AUGMENTE LA HAUTEUR FIXE POUR ACCUEILLIR LE TEXTE LISIBLE

            stat_layout = QVBoxLayout()
            stat_layout.setContentsMargins(0, 0, 0, 0)
            stat_layout.setSpacing(5)  # On remet un espacement un peu plus grand entre les labels

            stat_title = QLabel(title)
            stat_title.setStyleSheet(
                "font-size: 14px; color: white; font-weight: bold; border: none;")  # AUGMENTE LA TAILLE DU TITRE
            stat_title.setAlignment(Qt.AlignCenter)

            stat_value = QLabel(value)
            stat_value.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: white; border: none;")  # AUGMENTE ENCORE LA TAILLE DE LA VALEUR PRINCIPALE
            stat_value.setAlignment(Qt.AlignCenter)

            stat_info = QLabel(info)
            stat_info.setStyleSheet(
                "font-size: 12px; color: rgba(255, 255, 255, 0.7); font-style: italic; border: none;")  # AUGMENTE LA TAILLE DE L'INFO
            stat_info.setWordWrap(True)
            stat_info.setAlignment(Qt.AlignCenter)

            stat_layout.addWidget(stat_title)
            stat_layout.addWidget(stat_value)
            stat_layout.addWidget(stat_info)
            stat_frame.setLayout(stat_layout)

            stats_layout.addWidget(stat_frame)

        main_layout.addLayout(stats_layout)

        # Filtres : Boutons radio, Checkboxes et ComboBox sur une ligne horizontale
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(20)

        # Boutons radio
        self.radio_maternelle = QRadioButton("Maternelle")
        self.radio_primaire = QRadioButton("Primaire")
        self.radio_secondaire = QRadioButton("Secondaire")
        for radio in [self.radio_maternelle, self.radio_primaire, self.radio_secondaire]:
            radio.setStyleSheet("font-size: 16px; padding: 5px;")
            filter_layout.addWidget(radio)

        # Checkboxes avec exclusivité
        self.checkbox_anglo = QCheckBox("Anglophone")
        self.checkbox_franco = QCheckBox("Francophone")
        for check in [self.checkbox_anglo, self.checkbox_franco]:
            check.setStyleSheet("font-size: 16px; padding: 5px;")
            filter_layout.addWidget(check)

        # ComboBox
        self.combo_classes = QComboBox()
        self.combo_classes.setFixedWidth(300)
        self.combo_classes.setStyleSheet("font-size: 16px; padding: 8px; border-radius: 5px;")
        filter_layout.addWidget(self.combo_classes)

        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # TableWidget pour la liste des livres
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Titre", "Éditeur", "Édition", "Prix", "Intitulé"])
        self.table_widget.setStyleSheet("""
            font-size: 16px; 
            border: 2px solid #bdc3c7; 
            border-radius: 8px;
            QTableWidget::item { 
                padding: 5px;
                height: 35px; /* <--- AJOUTE CETTE LIGNE POUR AUGMENTER LA HAUTEUR DES LIGNES */
            }
            QScrollBar:vertical {
                border: 2px solid #bdc3c7;
                background: #f0f0f0;
                width: 15px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.table_widget.horizontalHeader().setStyleSheet("font-size: 16px; font-weight: bold;")
        # AJOUTE CETTE LIGNE POUR DÉFINIR LA LARGEUR DE L'EN-TÊTE VERTICAL
        self.table_widget.verticalHeader().setFixedWidth(30)  # Tu peux ajuster cette valeur (ex: 30, 40, 50) pour trouver la bonne largeur
        self.table_widget.setColumnWidth(0, 280)  # Titre
        self.table_widget.setColumnWidth(1, 240)  # Éditeur
        self.table_widget.setColumnWidth(2, 180)  # Édition
        self.table_widget.setColumnWidth(3, 150)  # Prix
        self.table_widget.setColumnWidth(4, 500)  # Intitulé

        self.table_widget.setMinimumHeight(250)  # réduit la hauteur ici
        main_layout.addWidget(self.table_widget)

        # Connexions pour l'exclusivité des checkboxes
        def toggle_anglo(state):
            if state:
                self.checkbox_franco.setChecked(False)

        def toggle_franco(state):
            if state:
                self.checkbox_anglo.setChecked(False)

        self.checkbox_anglo.toggled.connect(toggle_anglo)
        self.checkbox_franco.toggled.connect(toggle_franco)

        # Connexions pour les filtres
        self.radio_maternelle.toggled.connect(self.filters_changed)
        self.radio_primaire.toggled.connect(self.filters_changed)
        self.radio_secondaire.toggled.connect(self.filters_changed)
        self.checkbox_anglo.stateChanged.connect(self.lang_checked)
        self.checkbox_franco.stateChanged.connect(self.lang_checked)
        self.combo_classes.currentIndexChanged.connect(self.update_table)

        main_layout.addStretch()
        self.setLayout(main_layout)

        self.filters_changed()  # Initialisation

    def filters_changed(self):
        # Niveau actif
        if self.radio_maternelle.isChecked():
            self.active_niveau = "Maternelle"
        elif self.radio_primaire.isChecked():
            self.active_niveau = "Primaire"
        elif self.radio_secondaire.isChecked():
            self.active_niveau = "Secondaire"
        else:
            self.active_niveau = None

        # Reset langue
        self.checkbox_anglo.setChecked(False)
        self.checkbox_franco.setChecked(False)
        self.checkbox_anglo.setEnabled(True)
        self.checkbox_franco.setEnabled(True)

        self.update_combo_classes()
        self.table_widget.setRowCount(0)

    def lang_checked(self, state):
        sender = self.sender()
        if sender == self.checkbox_anglo and state == Qt.Checked:
            self.checkbox_franco.setChecked(False)
        elif sender == self.checkbox_franco and state == Qt.Checked:
            self.checkbox_anglo.setChecked(False)
        self.update_combo_classes()

    def update_combo_classes(self):
        self.combo_classes.clear()
        langue = self.get_langue()
        if not self.active_niveau or not langue:
            self.combo_classes.addItem("Sélectionnez une langue")
            self.table_widget.setRowCount(0)
            return

        classes = classes_par_niveau.get((self.active_niveau, langue), [])
        classes = classes[:5]  # Limite 5 classes
        self.combo_classes.addItems(classes)
        if classes:
            self.update_table(0)
        else:
            self.table_widget.setRowCount(0)

    def get_langue(self):
        if self.checkbox_anglo.isChecked():
            return "Anglophone"
        elif self.checkbox_franco.isChecked():
            return "Francophone"
        return None

    def update_table(self, index):
        if isinstance(index, int):
            idx = index
        elif isinstance(index, str):
            idx = self.combo_classes.findText(index)
        else:
            idx = -1

        langue = self.get_langue()
        if not self.active_niveau or not langue or idx == -1:
            self.table_widget.setRowCount(0)
            return

        classes = classes_par_niveau.get((self.active_niveau, langue), [])
        if idx >= len(classes):
            self.table_widget.setRowCount(0)
            return

        classe = classes[idx]
        livres = livres_par_classe.get(classe, [])

        self.table_widget.setRowCount(len(livres))
        for row, livre in enumerate(livres):
            item_titre = QTableWidgetItem(livre["Titre"])
            item_titre.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 0, item_titre)

            item_editeur = QTableWidgetItem(livre["Éditeur"])
            item_editeur.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 1, item_editeur)

            item_edition = QTableWidgetItem(livre["Édition"])
            item_edition.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 2, item_edition)

            item_prix = QTableWidgetItem(livre["Prix"])
            item_prix.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 3, item_prix)

            item_intitule = QTableWidgetItem(livre["Intitulé"])
            item_intitule.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 4, item_intitule)

    def get_ui(self):
        return self

    def refresh(self):
        pass