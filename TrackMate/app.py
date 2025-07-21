import streamlit as st
import sqlite3
import pandas as pd
import pytesseract
from PIL import Image
import io
import matplotlib.pyplot as plt
import base64
from datetime import datetime
import random
import os

# Configure page
st.set_page_config(page_title="TrackMate", layout="wide")

# Database connection manager
def get_db():
    conn = sqlite3.connect('receipts.db', check_same_thread=False)
    return conn

# Initialize database tables
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if receipts table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='receipts'")
    if not cursor.fetchone():
        cursor.execute('''CREATE TABLE receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT,
            date TEXT,
            amount REAL,
            filename TEXT,
            user_id TEXT
        )''')
    else:
        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(receipts)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE receipts ADD COLUMN user_id TEXT DEFAULT 'admin'")
    
    # Create users table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    
    # Insert default admin user if not exists
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                      ("admin", "admin123"))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()

# Initialize database at startup
init_db()

# --- Background Image ---
def add_bg_from_local():
    bg_url = "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?ixlib=rb-1.2.1&auto=format&fit=crop&w=1600&q=80"
    st.markdown(
        f"""<style>
        .stApp {{
            background-image: url("{bg_url}");
            background-size: cover;
            background-attachment: fixed;
            background-opacity: 0.9;
        }}
        .main {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 10px;
        }}
        </style>""",
        unsafe_allow_html=True
    )

add_bg_from_local()

# --- Sample Data Generator ---
def generate_fake_data(user_id="admin"):
    conn = get_db()
    cursor = conn.cursor()
    vendors = ['Amazon', 'Flipkart', 'Big Bazaar', 'DMart', 'Reliance Fresh', 'Myntra']
    for _ in range(20):
        vendor = random.choice(vendors)
        date = datetime(2024, random.randint(1,12), random.randint(1,28)).strftime('%Y-%m-%d')
        amount = round(random.uniform(50, 2000), 2)
        cursor.execute("INSERT INTO receipts (vendor, date, amount, filename, user_id) VALUES (?, ?, ?, ?, ?)",
                       (vendor, date, amount, f"fake_{random.randint(1000,9999)}.jpg", user_id))
    conn.commit()
    conn.close()

# Generate fake data if database is empty for the current user
def check_and_generate_data(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM receipts WHERE user_id=?", (user_id,))
    if cursor.fetchone()[0] == 0:
        generate_fake_data(user_id)
    conn.close()

# --- Login Page ---
def login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container():
            st.markdown("<div class='main'>", unsafe_allow_html=True)
            st.title("🔐 TrackMate Login")
            
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", type="primary"):
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username=? AND password=?", 
                             (username, password))
                user = cursor.fetchone()
                conn.close()
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = username
                    check_and_generate_data(username)
                    st.rerun()
                else:
                    st.error("Invalid credentials!")
            st.markdown("</div>", unsafe_allow_html=True)

# --- OCR Extraction ---
def extract_text_from_image(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

# --- Upload Page ---
def upload_page():
    st.title("📤 Upload Receipt")
    with st.container():
        st.markdown("<div class='main'>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload JPG, PNG or PDF receipt", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            try:
                st.image(uploaded_file, caption="Uploaded Receipt", width=300)
                
                with st.spinner("Extracting text from receipt..."):
                    text = extract_text_from_image(uploaded_file)
                
                vendor = st.text_input("Vendor", value="Amazon" if "amazon" in text.lower() else "")
                
                date_value = datetime.now().strftime("%Y-%m-%d")
                for line in text.split('\n'):
                    if any(word in line.lower() for word in ['date', 'time']):
                        date_value = line.split()[-1]
                        break
                
                date = st.text_input("Date (YYYY-MM-DD)", value=date_value)
                
                amount_value = 0.0
                for line in text.split('\n'):
                    if any(word in line.lower() for word in ['total', 'amount']):
                        parts = line.split()
                        for part in parts:
                            if part.replace('.','',1).isdigit():
                                amount_value = float(part)
                                break
                
                amount = st.number_input("Amount", min_value=0.0, step=0.1, value=amount_value)
                
                if st.button("Save to Database", type="primary"):
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO receipts (vendor, date, amount, filename, user_id) VALUES (?, ?, ?, ?, ?)",
                                 (vendor, date, amount, uploaded_file.name, st.session_state.user_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ Receipt added successfully!")
                    
            except Exception as e:
                st.error(f"OCR failed or invalid image. Error: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)

# --- View Receipts Page ---
def view_page():
    st.title("📄 View Receipts")
    with st.container():
        st.markdown("<div class='main'>", unsafe_allow_html=True)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, vendor, date, amount, filename FROM receipts WHERE user_id=?", (st.session_state.user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            df = pd.DataFrame(rows, columns=['id', 'vendor', 'date', 'amount', 'filename'])
            df['date'] = pd.to_datetime(df['date'])
            
            col1, col2 = st.columns(2)
            with col1:
                vendor_filter = st.multiselect("Filter by Vendor", options=df['vendor'].unique())
            with col2:
                date_range = st.date_input("Filter by Date Range", 
                                         value=[df['date'].min(), df['date'].max()],
                                         min_value=df['date'].min(), 
                                         max_value=df['date'].max())
            
            if vendor_filter:
                df = df[df['vendor'].isin(vendor_filter)]
            if len(date_range) == 2:
                df = df[(df['date'] >= pd.to_datetime(date_range[0])) & 
                       (df['date'] <= pd.to_datetime(date_range[1]))]
            
            df = df.sort_values('date', ascending=False)
            
            st.dataframe(df.style.format({'amount': '₹{:.2f}'}), 
                         use_container_width=True,
                         column_config={
                             "id": "ID",
                             "vendor": "Vendor",
                             "date": "Date",
                             "amount": "Amount",
                             "filename": "File Name"
                         })
            
            st.subheader("📊 Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Receipts", len(df))
            with col2:
                st.metric("Total Spending", f"₹{df['amount'].sum():.2f}")
            with col3:
                st.metric("Average Receipt", f"₹{df['amount'].mean():.2f}")
            
            st.subheader("📈 Spending Trends")
            trend_option = st.radio("View by", ["Daily", "Monthly", "Vendor"])
            
            if trend_option == "Daily":
                daily_spending = df.groupby('date')['amount'].sum().reset_index()
                st.line_chart(daily_spending.set_index('date'))
            elif trend_option == "Monthly":
                df['month'] = df['date'].dt.to_period('M')
                monthly_spending = df.groupby('month')['amount'].sum().reset_index()
                monthly_spending['month'] = monthly_spending['month'].astype(str)
                st.bar_chart(monthly_spending.set_index('month'))
            else:
                vendor_spending = df.groupby('vendor')['amount'].sum().sort_values(ascending=False)
                st.bar_chart(vendor_spending)
            
            st.subheader("📤 Export Data")
            if st.button("Export to Excel", type="primary"):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Receipts')
                    writer.close()
                
                st.download_button(
                    label="Download Excel File",
                    data=output.getvalue(),
                    file_name="TrackMate_Receipts.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No receipts found. Upload some receipts to get started!")
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- Main App ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    st.sidebar.title(f"👋 Welcome, {st.session_state.user_id}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.radio("Go to", ["Upload Receipt", "View Receipts"])
    
    if page == "Upload Receipt":
        upload_page()
    elif page == "View Receipts":
        view_page()