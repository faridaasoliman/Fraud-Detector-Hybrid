# gui.py
import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import Qt, QRectF

# Add the backend/models directory to sys.path to import model_loader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_loader import predict_fraud


class RingProgress(QWidget):
    def __init__(self):
        super().__init__()
        self.value = 0

    def setValue(self, v):
        self.value = v
        self.repaint()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(10, 10, self.width() - 20, self.height() - 20)

        # background circle
        painter.setPen(QPen(QColor("#333"), 16))
        painter.drawArc(rect, 0, 360 * 16)

        # progress arc
        painter.setPen(QPen(QColor("#ff9f43"), 16))
        angle = int(self.value * 360)
        painter.drawArc(rect, 90 * 16, -angle * 16)

        # text - show percentage with %
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 22, 600))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter,
                         f"{int(self.value * 100)}%")


class FraudGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fraud Detector")
        self.setGeometry(200, 150, 850, 500)
        self.setStyleSheet("background-color: #121212; color: white;")

        layout = QHBoxLayout(self)

        # left panel → result
        result_layout = QVBoxLayout()
        result_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Detection Result")
        title.setStyleSheet("font-size: 22px; font-weight: 600;")
        result_layout.addWidget(title)

        # ring progress
        self.ring = RingProgress()
        self.ring.setFixedHeight(200)
        result_layout.addWidget(self.ring)

        # fraud status label
        self.status_label = QLabel("No prediction yet")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #888; text-align: center;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.status_label)

        self.feature_bars = {}
        feature_names = [
            "Amount", "Time", "Country", "MerchantCategory",
            "TransactionType", "Device", "CardType",
            "PreviousFraudHistory"
        ]

        for f in feature_names:
            name_label = QLabel(f)
            name_label.setStyleSheet("font-size: 14px; margin-top: 10px;")

            bar = QProgressBar()
            bar.setMaximum(100)
            bar.setValue(0)
            bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    background: #333;
                    height: 6px;
                }
                QProgressBar::chunk {
                    background: #bb86fc;
                }
            """)

            result_layout.addWidget(name_label)
            result_layout.addWidget(bar)
            self.feature_bars[f] = bar

        layout.addLayout(result_layout, 1)

        # right panel → inputs
        input_layout = QVBoxLayout()
        input_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        def build_input(name, widget):
            lbl = QLabel(name)
            lbl.setStyleSheet("font-size: 14px;")
            input_layout.addWidget(lbl)
            input_layout.addWidget(widget)

        # INPUTS
        self.amount = QLineEdit()
        self.time = QLineEdit()
        self.country = QComboBox()
        self.country.addItems(["AE", "CN", "DE", "EG", "FR", "IN", "UK", "US"])

        self.merchant = QComboBox()
        self.merchant.addItems(["Clothing", "Electronics", "Food", "Gaming", "Gas", "Luxury", "OnlineServices", "Travel"])

        self.tx_type = QComboBox()
        self.tx_type.addItems(["ATM", "Online", "POS", "Transfer"])

        self.device = QComboBox()
        self.device.addItems(["Desktop", "Mobile", "POS", "Tablet"])

        self.card = QComboBox()
        self.card.addItems(["Credit", "Debit", "Virtual"])

        self.prev_fraud = QCheckBox("Previous Fraud History")

        # add them
        build_input("Amount", self.amount)
        build_input("Time", self.time)
        build_input("Country", self.country)
        build_input("MerchantCategory", self.merchant)
        build_input("TransactionType", self.tx_type)
        build_input("Device", self.device)
        build_input("CardType", self.card)
        input_layout.addWidget(self.prev_fraud)

        # button
        btn = QPushButton("Run Prediction")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #bb86fc;
                padding: 8px;
                font-size: 16px;
                border-radius: 6px;
            }
        """)
        btn.clicked.connect(self.run_prediction)
        input_layout.addWidget(btn)

        layout.addLayout(input_layout, 1)

    def run_prediction(self):
        try:
            data = {
                "Amount": float(self.amount.text()),
                "Time": self.time.text(),  # Keep as HH:MM string, model_loader will convert
                "Country": self.country.currentText(),
                "MerchantCategory": self.merchant.currentText(),
                "TransactionType": self.tx_type.currentText(),
                "Device": self.device.currentText(),
                "CardType": self.card.currentText(),
                "PreviousFraudHistory": 1 if self.prev_fraud.isChecked() else 0
            }

            prob, label, feature_importances = predict_fraud(data)

            # update UI
            self.ring.setValue(prob)

            # Update status label
            if label == 1:
                self.status_label.setText("⚠️ FRAUD DETECTED")
                self.status_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #ff5252; text-align: center;")
            else:
                self.status_label.setText("✓ NO FRAUD DETECTED")
                self.status_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #4caf50; text-align: center;")

            # Update feature importance bars based on actual model importances
            feature_labels = [
                "Amount", "Time", "Country", "MerchantCategory",
                "TransactionType", "Device", "CardType",
                "PreviousFraudHistory"
            ]
            
            for feature in feature_labels:
                if feature in self.feature_bars and feature in feature_importances:
                    importance_score = feature_importances[feature]
                    self.feature_bars[feature].setValue(int(importance_score))
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Please enter valid values.\nAmount: numeric (e.g., 100.00)\nTime: HH:MM format (e.g., 14:30)\nError: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Prediction Error", f"An error occurred during prediction:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = FraudGUI()
    gui.show()
    sys.exit(app.exec())
