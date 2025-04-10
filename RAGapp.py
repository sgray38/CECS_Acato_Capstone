# This script is the UI for our RAG application.
import sys
import os
import logging
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QWidget, QLabel, QListWidget)
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QFileDialog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("RAGapp.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    # get cwd
    cwd = os.getcwd()
    # TODO: add save functionality for summary text
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAG Application")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # file explorer list box
        file_explorer_layout = QVBoxLayout()
        self.file_explorer_label = QLabel("File Explorer:")
        file_explorer_layout.addWidget(self.file_explorer_label)
        self.file_explorer = QListWidget()
        file_explorer_layout.addWidget(self.file_explorer)
        
        # Create a horizontal layout for file explorer and button
        file_explorer_with_button_layout = QHBoxLayout()
        file_explorer_with_button_layout.addLayout(file_explorer_layout)
        
        # add load files button to file explorer layout
        load_files_btn = QPushButton("Load Files")
        load_files_btn.clicked.connect(self.load_files)
        file_explorer_with_button_layout.addWidget(load_files_btn)
        self.file_explorer.currentTextChanged.connect(self.change_f_path)
        main_layout.addLayout(file_explorer_with_button_layout)
                
        # Query input with the label
        query_layout = QVBoxLayout()
        self.current_doc_path = ''
        self.query_label = QLabel(f"Enter your query for:{self.current_doc_path}")
        query_layout.addWidget(self.query_label)
        self.query_input = QTextEdit()
        query_layout.addWidget(self.query_input)
        
        # create a horizontal layout for query input and its button
        q_with_button = QHBoxLayout()
        q_with_button.addLayout(query_layout)
        self.query_btn = QPushButton("Query")
        self.query_btn.clicked.connect(self.handle_query)
        q_with_button.addWidget(self.query_btn)
        main_layout.addLayout(q_with_button)
        
        # Response output
        self.response_label = QLabel("Response:")
        main_layout.addWidget(self.response_label)
        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        main_layout.addWidget(self.response_output)
        
        # Summarize button
        self.summarize_btn = QPushButton("Summarize Response")
        self.summarize_btn.clicked.connect(self.summarize_response)
        main_layout.addWidget(self.summarize_btn)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        main_layout.addWidget(self.status_label)
        logger.info("RAG Application started. prompting for directory.")
        # give the file explorer the cwd
        self.load_files()
        
    def change_f_path(self, fp):
        self.current_doc_path = fp
        self.query_label.setText(f"Enter your query for: {self.current_doc_path}")
        logger.info(f"currentTextChanged signal: {fp}")
    
    def load_files(self):
        """Load files from the current directory into the file explorer."""
        logger.info(f"clicked signal: load_files")
        # bring up a file browser popup
        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory", self.cwd)
            if directory:
                files = os.listdir(directory)
            else:
                self.status_label.setText(f'failed to load directory: {directory}')
            self.file_explorer.clear()
            for file in files:
                self.file_explorer.addItem(file)
            
            self.status_label.setText(f"Status: Files loaded from {directory}.")
        except Exception as e:
            logger.error(f"Error loading files: {e}")
            self.status_label.setText("Status: Error loading files.")
        
            
    def handle_query(self):
        """Handle the query input and simulate a response."""
        logger.info(f"clicked signal: handle_query")
        query = self.query_input.toPlainText().strip()
        if not query:
            self.status_label.setText("Status: Please enter a query.")
            return
        
        # TODO: Implement actual query handling logic
        response = f"Simulated response for query: {query}"
        self.response_output.setPlainText(response)
        self.status_label.setText("Status: Query processed successfully.")
        
    def summarize_response(self):
        """Summarize the response output."""
        logger.info(f"clicked signal: summarize_response")
        response = self.response_output.toPlainText().strip()
        if not response:
            self.status_label.setText("Status: No response to summarize.")
            return
        
        # TODO: Implement actual summarization logic
        summary = f"Simulated summary for response: {response[:50]}..."
        self.response_output.setPlainText(summary)
        self.status_label.setText("Status: Response summarized successfully.")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()