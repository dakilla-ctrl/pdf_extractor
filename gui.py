import os
import sys
import PyPDF2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
                             QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog,
                             QTextEdit, QProgressBar, QStatusBar, QGroupBox,
                             QMessageBox, QListWidget, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


# Glossy UI styles
def get_glossy_style():
    return """
    QMainWindow {
        background-color: #f0f0f0;
    }

    QGroupBox {
        background-color: rgba(255, 255, 255, 200);
        border: 1px solid #cccccc;
        border-radius: 6px;
        margin-top: 12px;
        font-weight: bold;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        color: #444444;
    }

    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #f6f7fa, stop:0.5 #dadbde, stop:1 #cacbcf);
        border: 1px solid #999;
        border-radius: 4px;
        padding: 6px;
        min-height: 20px;
        color: #333333;
    }

    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #e4e5e8, stop:0.5 #c8c9cc, stop:1 #b8b9bc);
    }

    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #c8c9cc, stop:0.5 #b8b9bc, stop:1 #a8a9ac);
    }

    QLineEdit {
        padding: 5px;
        border: 1px solid #aaaaaa;
        border-radius: 4px;
        background-color: rgba(255, 255, 255, 220);
    }

    QTextEdit, QListWidget {
        border: 1px solid #aaaaaa;
        background-color: rgba(255, 255, 255, 220);
        border-radius: 4px;
    }

    QProgressBar {
        border: 1px solid #aaaaaa;
        border-radius: 4px;
        background-color: rgba(255, 255, 255, 220);
        text-align: center;
        height: 20px;
    }

    QProgressBar::chunk {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                  stop:0 #2196F3, stop:1 #0D47A1);
        border-radius: 3px;
    }

    QStatusBar {
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                      stop:0 #f6f7fa, stop:1 #dadbde);
        color: #333333;
    }

    QLabel {
        color: #444444;
    }

    QSplitter::handle {
        background-color: #cccccc;
        width: 1px;
    }
    """


class PDFSearchThread(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(list, list)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, file_path, search_phrase):
        super().__init__()
        self.file_path = file_path
        self.search_phrase = search_phrase

    def run(self):
        try:
            pdf_reader = PyPDF2.PdfReader(self.file_path)
            num_pages = len(pdf_reader.pages)
            extracted_pages = []
            found_pages = []

            for page_num in range(num_pages):
                # Update progress
                progress = int((page_num + 1) / num_pages * 100)
                self.progress_signal.emit(progress)

                # Search page for text
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                if self.search_phrase.lower() in text.lower():
                    extracted_pages.append(page)
                    found_pages.append(page_num + 1)

            self.result_signal.emit(extracted_pages, found_pages)

            if len(extracted_pages) == 0:
                self.finished_signal.emit(False, f"No pages found containing '{self.search_phrase}'")
            else:
                self.finished_signal.emit(True, f"Found '{self.search_phrase}' in {len(extracted_pages)} pages")

        except Exception as e:
            self.finished_signal.emit(False, f"Error: {str(e)}")


class PDFExportThread(QThread):
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, output_path, extracted_pages):
        super().__init__()
        self.output_path = output_path
        self.extracted_pages = extracted_pages

    def run(self):
        try:
            pdf_writer = PyPDF2.PdfWriter()

            for page in self.extracted_pages:
                pdf_writer.add_page(page)

            with open(self.output_path, "wb") as output_file:
                pdf_writer.write(output_file)

            self.finished_signal.emit(True, f"Successfully saved to: {self.output_path}")

        except Exception as e:
            self.finished_signal.emit(False, f"Error saving file: {str(e)}")


class PDFSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Search & Extract")
        self.setMinimumSize(800, 600)

        # Initialize variables
        self.file_path = ""
        self.file_title = ""
        self.num_pages = 0
        self.size_mb = 0
        self.extracted_pages = []
        self.found_pages = []

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setCentralWidget(central_widget)

        # File selection section
        file_group = QGroupBox("Select PDF File")
        file_layout = QVBoxLayout()

        file_selector = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText("No file selected")

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)
        browse_button.setFixedWidth(100)

        file_selector.addWidget(self.file_path_edit)
        file_selector.addWidget(browse_button)

        # File info section
        file_info_layout = QHBoxLayout()

        self.file_name_label = QLabel("File Name: ")
        self.file_pages_label = QLabel("Pages: ")
        self.file_size_label = QLabel("Size: ")

        file_info_layout.addWidget(self.file_name_label)
        file_info_layout.addStretch()
        file_info_layout.addWidget(self.file_pages_label)
        file_info_layout.addStretch()
        file_info_layout.addWidget(self.file_size_label)

        file_layout.addLayout(file_selector)
        file_layout.addLayout(file_info_layout)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # Search section
        search_group = QGroupBox("Search PDF")
        search_layout = QVBoxLayout()

        search_input_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter search phrase...")

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_pdf)
        search_button.setFixedWidth(100)

        search_input_layout.addWidget(self.search_edit)
        search_input_layout.addWidget(search_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        search_layout.addLayout(search_input_layout)
        search_layout.addWidget(self.progress_bar)
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)

        # Results section
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()

        # Create splitter for results area
        results_splitter = QSplitter(Qt.Horizontal)

        # Pages list
        self.pages_list = QListWidget()
        self.pages_list.setMinimumWidth(200)

        # Results text view
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)

        results_splitter.addWidget(self.pages_list)
        results_splitter.addWidget(self.results_text)
        results_splitter.setSizes([200, 600])

        export_button = QPushButton("Export PDF with Found Pages")
        export_button.clicked.connect(self.export_pdf)

        results_layout.addWidget(results_splitter)
        results_layout.addWidget(export_button)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        # Set up status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Set initial state
        self.update_ui_state(False)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )

        if file_path:
            self.file_path = file_path
            self.file_path_edit.setText(file_path)

            try:
                # Extract file information
                self.file_title = os.path.splitext(os.path.basename(file_path))[0]
                self.num_pages = len(PyPDF2.PdfReader(file_path).pages)
                size_bytes = os.path.getsize(file_path)
                self.size_mb = round(size_bytes / (1024 * 1024), 2)

                # Update UI
                self.file_name_label.setText(f"File Name: {self.file_title}.pdf")
                self.file_pages_label.setText(f"Pages: {self.num_pages}")
                self.file_size_label.setText(f"Size: {self.size_mb} MB")

                self.update_ui_state(True)
                self.status_bar.showMessage(f"Loaded file: {self.file_title}.pdf")

            except Exception as e:
                self.status_bar.showMessage(f"Error loading file: {str(e)}")
                QMessageBox.critical(self, "Error", f"Could not load PDF file: {str(e)}")
                self.update_ui_state(False)

    def search_pdf(self):
        if not self.file_path:
            self.status_bar.showMessage("No file selected")
            return

        search_phrase = self.search_edit.text().strip()
        if not search_phrase:
            self.status_bar.showMessage("Please enter a search phrase")
            return

        # Clear previous results
        self.pages_list.clear()
        self.results_text.clear()
        self.extracted_pages = []
        self.found_pages = []

        # Set up and start search thread
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage(f"Searching for '{search_phrase}'...")

        self.search_thread = PDFSearchThread(self.file_path, search_phrase)
        self.search_thread.progress_signal.connect(self.update_progress)
        self.search_thread.result_signal.connect(self.handle_search_results)
        self.search_thread.finished_signal.connect(self.search_completed)
        self.search_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def handle_search_results(self, extracted_pages, found_pages):
        self.extracted_pages = extracted_pages
        self.found_pages = found_pages

    def search_completed(self, success, message):
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(message)

        if success and self.found_pages:
            # Update pages list
            for page_num in self.found_pages:
                self.pages_list.addItem(f"Page {page_num}")

            # Update results text
            result_msg = f"Found '{self.search_edit.text()}' in {len(self.found_pages)} out of {self.num_pages} pages.\n\n"
            result_msg += f"Pages containing the search phrase: {', '.join(map(str, self.found_pages))}"
            self.results_text.setText(result_msg)
        else:
            self.results_text.setText(f"No matches found for '{self.search_edit.text()}'")

    def export_pdf(self):
        if not self.extracted_pages:
            self.status_bar.showMessage("No pages to export")
            return

        search_phrase = self.search_edit.text().strip()
        default_name = f"{self.file_title}-{search_phrase[:10].capitalize()}.pdf"

        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Extracted Pages", default_name, "PDF Files (*.pdf)"
        )

        if output_path:
            self.status_bar.showMessage(f"Exporting to {output_path}...")

            self.export_thread = PDFExportThread(output_path, self.extracted_pages)
            self.export_thread.finished_signal.connect(self.export_completed)
            self.export_thread.start()

    def export_completed(self, success, message):
        self.status_bar.showMessage(message)

        if success:
            QMessageBox.information(self, "Export Complete", message)

    def update_ui_state(self, file_loaded):
        self.search_edit.setEnabled(file_loaded)
        self.pages_list.setEnabled(file_loaded)
        self.results_text.setEnabled(file_loaded)

        # Reset UI elements if no file is loaded
        if not file_loaded:
            self.file_name_label.setText("File Name: ")
            self.file_pages_label.setText("Pages: ")
            self.file_size_label.setText("Size: ")
            self.pages_list.clear()
            self.results_text.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show window
    window = PDFSearchApp()

    # Apply glossy styling
    window.setStyleSheet(get_glossy_style())

    window.show()

    sys.exit(app.exec_())