# This script is the UI for our RAG application.
import sys
import os
import logging
from llmsherpa.readers import LayoutPDFReader
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QWidget, QLabel, QListWidget, QLineEdit, QComboBox)
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QFileDialog
# get our custom summarization module
import sum_text

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

llmsherpa_api_url = "http://localhost:5010/api/parseDocument?renderFormat=all"

class MainWindow(QMainWindow):
    # get cwd
    cwd = os.getcwd()
    reader = LayoutPDFReader(llmsherpa_api_url)
    parsed_doc = None
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
        file_display_layout = QVBoxLayout()
        self.file_display_label = QLabel("File display:")
        file_display_layout.addWidget(self.file_display_label)
        self.file_list_widget = QListWidget()
        self.file_list_widget.addItem("No files loaded.")
        file_display_layout.addWidget(self.file_list_widget)
        
        
        doc_display_layout = QVBoxLayout()
        self.doc_display_label = QLabel("No file selected.")
        doc_display_layout.addWidget(self.doc_display_label)
        self.doc_display = QListWidget()
        doc_display_layout.addWidget(self.doc_display)
        
        # Create a horizontal layout for file explorer and button
        file_explorer_with_button_layout = QHBoxLayout()
        
        # add load files button to file explorer layout
        load_dir_btn = QPushButton("Load Files")
        load_dir_btn.clicked.connect(self.load_directory_contents)
        read_file_btn = QPushButton("Read File")
        read_file_btn.clicked.connect(self.parse_file)
        file_display_layout.addWidget(load_dir_btn)
        doc_display_layout.addWidget(read_file_btn)
        file_explorer_with_button_layout.addLayout(file_display_layout)
        file_explorer_with_button_layout.addLayout(doc_display_layout)

        self.file_list_widget.currentTextChanged.connect(self.change_f_path)
        main_layout.addLayout(file_explorer_with_button_layout)
                
        # Query input with the label
        query_layout = QVBoxLayout()
        self.current_doc_path = ''
        self.query_label = QLabel(f"Enter your query for:{self.current_doc_path}")
        query_layout.addWidget(self.query_label)
        self.query_input = QLineEdit()
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
        self.summary_out_put = QTextEdit()
        self.summary_out_put.setReadOnly(True)
        main_layout.addWidget(self.summary_out_put)
        
        # Summarize button
        self.summarize_btn = QPushButton("Summarize Response")
        self.summarize_btn.clicked.connect(self.summarize_response)
        main_layout.addWidget(self.summarize_btn)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        main_layout.addWidget(self.status_label)
        logger.info("RAG Application started. prompting for directory.")
        # give the file explorer the cwd
        self.load_directory_contents()
        
    def parse_file(self):
        """Parse the selected PDF file."""
        pdf_path = os.path.join(os.path.relpath(self.cwd), self.current_doc_path)
        logger.info(f"clicked signal: parse_file with path: {pdf_path}")
        if not self.current_doc_path:
            self.status_label.setText("Status: No file selected.")
            return
        try:
            
            response = self.reader.read_pdf(pdf_path)
            if response:
                self.parsed_doc = response
                self.query_label.setText(f"Enter your query for: {self.current_doc_path}")
                self.status_label.setText("Status: File parsed successfully.")
                self.doc_display_label.setText(f"parsed sections for: {self.current_doc_path}")
                # show the section titles in the file explorer
                self.doc_display.clear()
                for section in self.parsed_doc.sections():
                    self.doc_display.addItem(section.title)
            else:
                self.status_label.setText("Status: No content parsed from file.")
                
        except Exception as e:
            logger.error(f"Error parsing file: {e}")
            self.status_label.setText("Status: Error parsing file.")
            self.parsed_doc = None
            
    def change_f_path(self, fp):
        self.current_doc_path = fp
        self.query_label.setText(f"Enter your query for: {self.current_doc_path}")
        logger.info(f"currentTextChanged signal: {fp}")
    
    def load_directory_contents(self):
        """Load files from the current directory into the file explorer."""
        logger.info(f"clicked signal: load_directory_contents")
        # bring up a file browser popup
        try:
            directory = QFileDialog.getExistingDirectory(self, "Select Directory", self.cwd)
            if directory:
                files = os.listdir(directory)
                self.cwd = directory
            else:
                self.status_label.setText(f'failed to load directory: {directory}')
            self.file_list_widget.clear()
            for file in files:
                self.file_list_widget.addItem(file)
            
            self.status_label.setText(f"Status: Files loaded from {directory}.")
        except Exception as e:
            logger.error(f"Error loading files: {e}")
            self.status_label.setText("Status: Error loading files.")
        
            
    def handle_query(self):
        """Handle the query input and simulate a response."""
        logger.info(f"clicked signal: handle_query")
        query = self.query_input.text().strip()
        if not query:
            self.status_label.setText("Status: Please enter a query.")
            return
        
        # TODO: Implement actual query handling logic
        response = f"{query}"
        self.summary_out_put.setPlainText(response)
        self.status_label.setText("Status: Query processed successfully.")
        
    def summarize_response(self):
        """Summarize the response output."""
        logger.info(f"clicked signal: summarize_response")
        response = self.summary_out_put.toPlainText().strip()
        response = sum_text.summarize_text(response)
        if not response:
            self.status_label.setText("Status: No response to summarize.")
            return
        
        # TODO: Implement actual summarization logic
        summary = f"Summary:\n {response}"
        self.summary_out_put.setPlainText(summary)
        self.status_label.setText("Status: Response summarized successfully.")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()