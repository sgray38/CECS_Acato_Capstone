# This script is the UI for our RAG application.
import sys
import os
import logging
from llmsherpa.readers import LayoutPDFReader
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QToolBar, QFileDialog, QSpinBox,
                             QPushButton, QTextEdit, QWidget, QLabel, QListWidget, QLineEdit, QCheckBox, QDialog)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QAction
# get our custom summarization module and query module
import sum_text
import query_doc

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

class SummarizationWorker(QThread):
    """Worker thread for summarizing text."""
    finished = pyqtSignal(str)  # Signal to emit the summarized text
    error = pyqtSignal(str)     # Signal to emit error messages

    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        """Perform the summarization in a separate thread."""
        try:
            summary = sum_text.summarize_text(self.text)
            self.finished.emit(summary)  # Emit the summarized text
        except Exception as e:
            self.error.emit(f"Error during summarization: {e}")

class QueryWorker(QThread):
    """Worker thread for querying the document."""
    finished = pyqtSignal(str)  # Signal to emit the query result
    error = pyqtSignal(str)     # Signal to emit error messages

    def __init__(self, query, context, qa_response, n_results=1):
        super().__init__()
        self.query = query
        self.context = context
        self.qa_response = qa_response
        self.n_results = n_results
        
    def run(self):
        """Perform the query processing in a separate thread."""
        try:
            if not self.qa_response:
                response = query_doc.query_document(self.query, self.context)
            else:
                response = query_doc.get_top_result(self.context, self.query, self.n_results)
            self.finished.emit(response)  # Emit the query result
        except Exception as e:
            self.error.emit(f"Error during querying: {e}")

class MainWindow(QMainWindow):
    # get cwd
    cwd = os.getcwd()
    reader = LayoutPDFReader(llmsherpa_api_url)
    parsed_doc = None
    qa_response = False
    n_results = 1
    
    # TODO: add save functionality for summary text
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAG Application")
        self.setGeometry(100, 100, 800, 600)
        
        # Add a toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)

        # Add a "Settings" action to the toolbar
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        self.toolbar.addAction(settings_action)
        
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
        self.doc_display.currentTextChanged.connect(self.show_section_content)
        
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
        q_all = QHBoxLayout()
        q_all.addLayout(query_layout)
        q_with_button = QVBoxLayout()
        self.query_btn = QPushButton("Query")
        self.query_btn.clicked.connect(self.handle_query)
        q_with_button.addWidget(self.query_btn)
        self.top_responses_checkbox = QCheckBox("Top Responses")
        self.top_responses_checkbox.stateChanged.connect(self.single_response_change)
        q_with_button.addWidget(self.top_responses_checkbox)
        q_all.addLayout(q_with_button)
        main_layout.addLayout(q_all)
        
        # Response output
        self.response_label = QLabel("Response:")
        main_layout.addWidget(self.response_label)
        self.summary_out_put = QTextEdit()
        # self.summary_out_put.setReadOnly(True)
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
        
    def open_settings_dialog(self):
        """Open a settings dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout(dialog)

        # Add a spin box for n_results
        layout.addWidget(QLabel("Number of Results (n_results):"))
        n_results_spinbox = QSpinBox()
        n_results_spinbox.setRange(1, 10)  # Allow 1 to 10 results
        n_results_spinbox.setValue(self.n_results)  # Set the current value
        n_results_spinbox.valueChanged.connect(self.update_n_results)
        layout.addWidget(n_results_spinbox)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.exec()
    
    def update_n_results(self, value):
        """Update the n_results value."""
        self.n_results = value
        logger.info(f"n_results updated to: {self.n_results}")    
    
    def single_response_change(self, state):
        """Handle the single response checkbox state change."""
        logger.info(f"single_response signal: {state}")
        self.qa_response = state == 2  # 2 means checked
        
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
    
    def show_section_content(self, section_title):
        """Show the content of the selected section."""
        logger.info(f"clicked signal: show_section_content with title: {section_title}")
        if not self.parsed_doc:
            self.status_label.setText("Status: No parsed document available.")
            return
        for section in self.parsed_doc.sections():
            if section.title == section_title:
                paragraphs = [p.to_text() for p in section.paragraphs()]
                # flatten the list of paragraphs
                # paragraphs = [sentence for sublist in paragraphs for sentence in sublist]
                self.summary_out_put.setText("\n".join(paragraphs))
                self.status_label.setText(f"Status: Displaying content for section: {section_title}")
                return
        
        self.status_label.setText("Status: Section not found.")
               
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
        """Handle the query input asynchronously."""
        logger.info("clicked signal: handle_query")
        query = self.query_input.text().strip()
        if not query:
            self.status_label.setText("Status: Please enter a query.")
            return

        if not self.parsed_doc:
            self.status_label.setText("Status: No parsed document available.")
            return

        # Gather context from the parsed document
        context = []
        for section in self.parsed_doc.chunks():
            context.append([sentence for sentence in section.sentences])
        context = sum(context, [])

        # Disable the button to prevent multiple clicks
        self.query_btn.setEnabled(False)
        self.summarize_btn.setEnabled(False)
        self.status_label.setText("Status: Processing query...")

        # Create and start the worker thread, optional arguments define the query job run:
        # 1. top n results order by similarity
        # 2. document filtered by query and similarity in the order it appears in the document.
        self.query_worker = QueryWorker(query, context, self.qa_response, self.n_results)
        self.query_worker.finished.connect(self.on_query_complete)
        self.query_worker.error.connect(self.on_query_error)
        self.query_worker.start()

    def on_query_complete(self, response):
        """Handle the completion of the query."""
        self.summary_out_put.setText(response)
        self.status_label.setText("Status: Query processed successfully.")
        self.query_btn.setEnabled(True)
        self.summarize_btn.setEnabled(True)

    def on_query_error(self, error_message):
        """Handle errors during query processing."""
        self.status_label.setText(error_message)
        self.query_btn.setEnabled(True)
        self.summarize_btn.setEnabled(True)
        
    def summarize_response(self):
        """Summarize the response output asynchronously."""
        logger.info("clicked signal: summarize_response")
        response = self.summary_out_put.toPlainText().strip()
        if not response:
            self.status_label.setText("Status: No response to summarize.")
            return

        # Disable the button to prevent multiple clicks
        self.summarize_btn.setEnabled(False)
        self.query_btn.setEnabled(False)
        self.status_label.setText("Status: Summarizing...")

        # Create and start the worker thread
        self.worker = SummarizationWorker(response)
        self.worker.finished.connect(self.on_summarization_complete)
        self.worker.error.connect(self.on_summarization_error)
        self.worker.start()

    def on_summarization_complete(self, summary):
        """Handle the completion of the summarization."""
        self.summary_out_put.setText(f"Summary:\n{summary}")
        self.status_label.setText("Status: Response summarized successfully.")
        self.summarize_btn.setEnabled(True)
        self.query_btn.setEnabled(True)
        
    def on_summarization_error(self, error_message):
        """Handle errors during summarization."""
        self.status_label.setText(error_message)
        self.summarize_btn.setEnabled(True)
        self.query_btn.setEnabled(True)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()