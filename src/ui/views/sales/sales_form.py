"""
Formulaires pour le point de vente.
Paiement, facture, etc.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QLabel, QPushButton,
    QTextEdit, QDialog, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QTextDocument

from src.ui.widgets.ModalView import ModalView


class SalesPaymentForm(QWidget):
    """Formulaire de paiement"""
    
    def __init__(self, total: float = 0, payment_methods: list = None, parent=None):
        super().__init__(parent)
        self.total = total
        self.payment_methods = payment_methods or []
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Recap
        recap_frame = QFrame()
        recap_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border: 2px solid #9b59b6;
                border-radius: 10px;
            }
        """)
        recap_layout = QHBoxLayout(recap_frame)
        recap_layout.setContentsMargins(16, 10, 16, 10)
        
        self.recap_label = QLabel(f"Total : {self.total:.0f} FCFA")
        self.recap_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #9b59b6; "
            "border: none; background: transparent;"
        )
        recap_layout.addStretch()
        recap_layout.addWidget(self.recap_label)
        layout.addWidget(recap_frame)
        
        # Separateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #e0e0e0;")
        sep.setFixedHeight(2)
        layout.addWidget(sep)
        
        # Formulaire
        LABEL_STYLE = "font-weight: bold; font-size: 14px; color: #2c3e50;"
        INPUT_STYLE = """
            QLineEdit {
                font-size: 14px;
                padding: 10px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                color: #1a1a1a;
                min-height: 42px;
            }
            QLineEdit:focus {
                border-color: #9b59b6;
                background-color: #fafafa;
            }
        """
        COMBO_STYLE = """
            QComboBox {
                font-size: 14px;
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ffffff;
                color: #1a1a1a;
                min-height: 42px;
            }
            QComboBox:focus {
                border-color: #9b59b6;
            }
        """
        
        def make_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(LABEL_STYLE)
            lbl.setMinimumWidth(110)
            return lbl
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(14)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Nom du client
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Jean-Paul Nguema (optionnel)")
        self.name_input.setStyleSheet(INPUT_STYLE)
        form_layout.addRow(make_label("Nom du client :"), self.name_input)
        
        # Telephone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Ex: 6XX XXX XXX (optionnel)")
        self.phone_input.setStyleSheet(INPUT_STYLE)
        form_layout.addRow(make_label("Numero :"), self.phone_input)
        
        # Mode de paiement
        self.payment_combo = QComboBox()
        self.payment_combo.setStyleSheet(COMBO_STYLE)
        for method in self.payment_methods:
            self.payment_combo.addItem(method["name"], method["id"])
        form_layout.addRow(make_label("Paiement :"), self.payment_combo)
        
        layout.addWidget(form_widget)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_data(self) -> dict:
        """Recupere les donnees du formulaire"""
        return {
            'client_name': self.name_input.text().strip(),
            'client_phone': self.phone_input.text().strip(),
            'payment_method_id': self.payment_combo.currentData(),
            'payment_method_name': self.payment_combo.currentText(),
        }
    
    def validate(self) -> tuple:
        """Valide les donnees du formulaire"""
        # Tout est optionnel
        return True, ""


class InvoiceViewer(QDialog):
    """Visualisateur de facture avec impression"""
    
    def __init__(self, invoice_number: str, html_content: str, parent=None):
        super().__init__(parent)
        self.invoice_number = invoice_number
        self.html_content = html_content
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle(f"Facture {self.invoice_number}")
        self.setMinimumSize(600, 580)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Titre
        title_lbl = QLabel(f"Facture {self.invoice_number}")
        title_lbl.setFont(QFont("Arial", 16, QFont.Bold))
        title_lbl.setStyleSheet("color: #9b59b6;")
        layout.addWidget(title_lbl)
        
        # Apercu
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setHtml(self.html_content)
        layout.addWidget(self.preview)
        
        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        print_btn = QPushButton("Imprimer la facture")
        print_btn.setMinimumHeight(42)
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 18px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        print_btn.clicked.connect(self._on_print)
        
        close_btn = QPushButton("Fermer")
        close_btn.setMinimumHeight(42)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 18px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addWidget(print_btn)
        layout.addLayout(btn_layout)
    
    def _on_print(self):
        printer = QPrinter(QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec() == QPrintDialog.Accepted:
            doc = QTextDocument()
            doc.setHtml(self.html_content)
            doc.print_(printer)


def build_invoice_html(invoice_number: str, client_name: str, client_phone: str,
                       payment_label: str, total: float, cart_snapshot: list) -> str:
    """Construit le HTML de la facture"""
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    rows = ""
    for item in cart_snapshot:
        product = item["product"]
        subtotal = product["price"] * item["quantity"]
        rows += f"""
        <tr>
            <td>{product['name']}</td>
            <td style="text-align:center;">{item.get('type_display', '')}</td>
            <td style="text-align:center;">{item['quantity']}</td>
            <td style="text-align:right;">{product['price']:.0f} FCFA</td>
            <td style="text-align:right;"><b>{subtotal:.0f} FCFA</b></td>
        </tr>
        """
    
    return f"""
    <html><head><style>
        body {{ font-family: Arial, sans-serif; font-size: 13px; color: #1a1a1a; margin: 20px; }}
        h2 {{ color: #9b59b6; margin-bottom: 4px; }}
        .meta {{ color: #555; font-size: 12px; margin-bottom: 16px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th {{ background-color: #9b59b6; color: white; padding: 8px 6px; text-align: left; }}
        td {{ padding: 7px 6px; border-bottom: 1px solid #e0e0e0; }}
        .total-row td {{ font-size: 15px; font-weight: bold; border-top: 2px solid #9b59b6;
                         background-color: #f0f8ff; color: #9b59b6; padding: 10px 6px; }}
        .info-block {{ background: #f9f9f9; border: 1px solid #ddd; border-radius: 6px;
                       padding: 10px 14px; margin-bottom: 14px; }}
    </style></head><body>
    <h2>Facture de Vente</h2>
    <p class="meta">N° {invoice_number} — Emise le : {date_str}</p>
    <div class="info-block">
        <p><b>Client :</b> {client_name or 'Anonyme'}</p>
        <p><b>Telephone :</b> {client_phone or '—'}</p>
        <p><b>Mode de paiement :</b> {payment_label}</p>
    </div>
    <table><thead><tr>
        <th>Produit</th><th style="text-align:center;">Type</th>
        <th style="text-align:center;">Qte</th><th style="text-align:right;">Prix unit.</th>
        <th style="text-align:right;">Sous-total</th>
    </tr></thead><tbody>
        {rows}
        <tr class="total-row"><td colspan="4" style="text-align:right;">TOTAL</td>
            <td style="text-align:right;">{total:.0f} FCFA</td></tr>
    </tbody></table>
    <p style="margin-top:24px; color:#888; font-size:11px; text-align:center;">
        Merci pour votre achat — Librairie Papeterie Siledje
    </p></body></html>
    """


# Import pour build_invoice_html
from datetime import datetime