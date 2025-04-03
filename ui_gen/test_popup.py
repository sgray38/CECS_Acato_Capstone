from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, 
    QLineEdit, QDialogButtonBox, QMessageBox,
    QComboBox)
from PyQt6.QtCore import pyqtSignal

class InputDialog(QDialog):
    text_accepted = pyqtSignal(tuple)  # Define a custom signal

    def __init__(self, field_names=[], parent=None):
        super().__init__(parent)
        self.field_names = field_names 
        self.setWindowTitle(f"Add New Setting")
        
        layout = QVBoxLayout()

        self.key_field = QLineEdit()
        layout.addWidget(self.key_field)
        self.value_field = QLineEdit()
        layout.addWidget(self.value_field)
        
        # add a combobox for the field being added to in the form
        self.edit_field = QComboBox()
        self.edit_field.addItems(self.field_names)
        layout.addWidget(self.edit_field)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def on_accept(self):
        form_update = self.get_fkv()
        self.text_accepted.emit(form_update)  # Emit the custom signal with the input text
        self.accept()
    
    def get_curr_field(self):
        return self.edit_field.currentText()
    
    def get_fkv(self):
        return self.get_curr_field(),self.key_field.text(), self.value_field.text()

if __name__ == '__main__':
    app = QApplication([])

    def handle_text_accepted(text):
        QMessageBox.information(None, "Input", f"You entered: {text}")

    dialog = InputDialog()
    dialog.text_accepted.connect(handle_text_accepted)  # Connect the custom signal to a slot
    dialog.exec()