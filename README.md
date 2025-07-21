# TrackMate - Receipt Tracking Application
TrackMate is a Streamlit-based web application that helps users organize and analyze their purchase receipts. With OCR capabilities and SQLite database storage, it provides an easy way to track spending habits.

## Features

- 📤 **Receipt Upload**: Upload images of receipts with automatic data extraction (OCR)
- 🔍 **Expense Tracking**: View and filter your purchase history
- 📊 **Data Visualization**: Interactive charts showing spending patterns
- 📥 **Excel Export**: Download your receipt data for further analysis
- 🔐 **User Authentication**: Secure login system
- 🏷️ **Vendor Categorization**: Automatic vendor detection from receipts

## Screenshots
<img width="1920" height="1080" alt="Screenshot (459)" src="https://github.com/user-attachments/assets/2c62ef1b-f7de-47b4-b836-b39070414bbc" />
<img width="1920" height="1080" alt="Screenshot (460)" src="https://github.com/user-attachments/assets/6105450f-73b5-4757-9456-f545fa375448" />
<img width="1920" height="1080" alt="Screenshot (461)" src="https://github.com/user-attachments/assets/eed58025-51c9-43ef-9f92-e86ef7547d69" />
<img width="1920" height="1080" alt="Screenshot (462)" src="https://github.com/user-attachments/assets/3e049863-39de-4902-8baf-707fc69adc02" />

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/TrackMate.git
   cd TrackMate
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR** (required for text extraction):
   - **Windows**: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Mac**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr`

## Usage

1. **Run the application**:
   ```bash
   streamlit run app.py
   ```

2. **Login credentials**:
   - Username: `admin`
   - Password: `admin123`

3. **Features**:
   - Upload receipts via the "Upload Receipt" page
   - View and analyze your spending on the "View Receipts" page
   - Export data to Excel for further analysis

## File Structure

```
TrackMate/
├── app.py                # Main application code
├── receipts.db           # Database file (created automatically)
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── screenshots/          # Application screenshots
```

## Technologies Used

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite
- **OCR**: Tesseract (pytesseract)
- **Data Processing**: Pandas
- **Visualization**: Matplotlib

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

For questions or feedback, please contact:

Your Name - reachteju10@gmail.com  
Project Link: [https://github.com/yourusername/TrackMate](https://github.com/yourusername/TrackMate)
