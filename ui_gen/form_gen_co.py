import sys
import json
import logging
from typing import Any, Dict, Union, Callable
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QCheckBox, QScrollArea, QPushButton, QComboBox, 
    QGroupBox, QTextEdit
)
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import pyqtSignal
from hkWarnings import notImplementedWarning
from test_popup import InputDialog

# Configure logging
logging.basicConfig(level=logging.INFO, format='form_gen - %(asctime)s - %(levelname)s - %(message)s')

class DynamicFormGenerator(QWidget):
    config_changed = pyqtSignal(dict)  # Signal for config updates
    closed = pyqtSignal()  # Signal for form closure
    
    def __init__(self, initial_dict: Dict[str, Any] = None):
        super().__init__()
        self.form_dict = {}
        self.on_update = None
        self.setWindowTitle("Dynamic Form Generator")
        self.setGeometry(100, 100, 700, 600)
        editable_fields = initial_dict.keys() if initial_dict else []
        # Create input dialogs for adding and deleting fields
        self.popup_add = InputDialog(field_names=editable_fields)
        self.popup_del = InputDialog(field_names=editable_fields)
        # Connect signals to slots
        self.popup_add.text_accepted.connect(self.modify_form_field)
        self.popup_del.text_accepted.connect(self.delete_field_value)
        # Main layout
        main_layout = QVBoxLayout()
        
        # Scroll area for dynamic fields
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        self.form_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # buttons layout
        button_layout = QHBoxLayout() 
        # add field button
        add_field_btn = QPushButton("Add Field")
        add_field_btn.clicked.connect(self.popup_add.show)
        main_layout.addWidget(add_field_btn)
        # delete field button
        del_field_btn = QPushButton("Delete Field")
        del_field_btn.clicked.connect(self.popup_del.show)
        main_layout.addWidget(del_field_btn)
        # save button
        save_btn = QPushButton("Save Form")
        save_btn.clicked.connect(self.signal_save)
        button_layout.addWidget(save_btn)    
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
        # If initial dictionary is provided, generate form after event loop starts
        if initial_dict:
            QTimer.singleShot(0, lambda: self.generate_dict_form(initial_dict))
            
    def modify_form_field(self, field_update):
        logging.info(f"Text accepted: {field_update}")
        field, key, value = field_update
        self.form_dict[field][key] = value
        self.generate_dict_form(self.form_dict)
        self.signal_save()
        self.popup_add.close()

    def delete_field_value(self, field_update):
        logging.info(f"Text accepted: {field_update}")
        field, key, value = field_update
        del self.form_dict[field][key]
        self.generate_dict_form(self.form_dict)
        self.signal_save()
        self.popup_del.close()
    
    def signal_save(self):
        # signal the save event of the application that uses this form
        form_dict = self.get_form_dict()
        self.config_changed.emit(form_dict)
        if self.on_update:
            self.on_update(form_dict)
        
    def get_form_dict(self) -> Dict[str, Any]:
        form_dict = {}
        
        for i in range(self.form_layout.count()):
            widget = self.form_layout.itemAt(i).widget()
            if isinstance(widget, QGroupBox):
                key = widget.title()
                value = self.get_nested_dict(widget.layout())
            else:
                key = widget.layout().itemAt(0).widget().text()
                value = self.get_field_value(widget.layout().itemAt(1).widget())
            
            form_dict[key] = value
        
        return form_dict
    
    def get_nested_dict(self, layout: QVBoxLayout) -> Dict[str, Any]:
        nested_dict = {}
        
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            key = widget.layout().itemAt(0).widget().text()
            value = self.get_field_value(widget.layout().itemAt(1).widget())
            logging.info(f"{key}: {value}")
            nested_dict[key.split('.')[-1]] = value
        
        return nested_dict
    
    def get_field_value(self, widget: QWidget) -> Any:
        if isinstance(widget, QLineEdit):
            txt = widget.text()
            try:
                return eval(txt)
            except:
                return txt
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QComboBox):
            value_str = widget.parent().layout().itemAt(1).widget().text()
            value = eval(value_str)
            return value
        else:
            return None
    
    def generate_dict_form(self, initial_dict):
        """Separate method to generate form from dictionary"""
        self.form_dict = initial_dict.copy()
        self.generate_form()

    def generate_form(self):
        # Clear existing form
        for i in reversed(range(self.form_layout.count())): 
            self.form_layout.itemAt(i).widget().setParent(None)
        
        try:
            # Safely evaluate the dictionary input
            input_dict = self.form_dict.copy()
            
            # Generate form fields for each key-value pair
            self.create_nested_fields(input_dict, self.form_layout)
        
        except Exception as e:
            error_label = QLabel(f"Error: {str(e)}")
            self.form_layout.addWidget(error_label)
        
    def create_nested_fields(self, data: Dict[str, Any], parent_layout: QVBoxLayout, parent_key: str = ''):
        """Recursively create form fields for nested dictionaries"""
        for key, value in data.items():
            # Construct full key path for nested dictionaries
            full_key = f"{key}" if parent_key else key
            
            # Handle nested dictionary
            if isinstance(value, dict):
                # Create a group box for nested dictionary
                group_box = QGroupBox(full_key)
                nested_layout = QVBoxLayout()
                group_box.setLayout(nested_layout)
                
                # Recursively create fields for nested dictionary
                self.create_nested_fields(value, nested_layout, full_key)
                
                parent_layout.addWidget(group_box)
                # button to add new key-value pair
            
            # Handle other types (similar to previous implementation)
            else:
                field = self.create_field(full_key, value)
                if field:
                    parent_layout.addWidget(field)

    def create_field(self, key: str, value: Any) -> Union[QWidget, None]:
        # Create a horizontal layout for each field
        field_layout = QHBoxLayout()
        if key not in ['', ' ', None]:
            key_input = QLabel(str(key))
        else:
            # If the key is empty or None, we dont want a key input field
            key_input = QLabel("")
        field_layout.addWidget(key_input)
        
        if isinstance(value, int) and not value in [True, False]:
            input_widget = QLineEdit()
            input_widget.setValidator(QIntValidator())
            input_widget.setText(str(value))
        
        elif isinstance(value, float):
            input_widget = QLineEdit()
            input_widget.setValidator(QDoubleValidator())
            input_widget.setText(str(value))
        
        elif isinstance(value, bool):
            input_widget = QCheckBox()
            input_widget.setChecked(value)
        
        elif isinstance(value, str) and not value.strip() == "":
            input_widget = QLineEdit()
            input_widget.setText(value)
        
        elif isinstance(value, list):
            # if its an empty list, add a large text edit
            if not value:
                input_widget = QTextEdit()
                input_widget.setPlaceholderText("Empty list, enter items here...")
            else:
                # it's a non-empty list, add the text edit and join the items
                input_widget = QTextEdit()
                input_widget.setPlainText("\n".join(map(str, value)))
        
        else:
            return None  # Unsupported type
        
        field_layout.addWidget(input_widget)
        
        field_widget = QWidget()
        field_widget.setLayout(field_layout)
        
        return field_widget

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
    

def launch_form(input_dict: Dict[str, Any] = None) -> tuple[QApplication, DynamicFormGenerator]:
    """
    Launch the form with an optional input dictionary.
    Ensures QApplication is created in main thread.
    """
    app = QApplication(sys.argv)
    form_generator = DynamicFormGenerator(initial_dict=input_dict)
    return app, form_generator

def main():
    # Load initial dictionary from file
    with open("ui_gen\\test_form.json") as f:
        initial_dict = json.load(f)
    
    # Launch form with initial dictionary
    app, form = launch_form(initial_dict)
    form.show()
    app.exec()
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        logging.info("Exiting...")
    except TypeError as e:
        logging.error(e)
        raise notImplementedWarning("This feature is not implemented yet")
    else:
        logging.info("Exiting...")