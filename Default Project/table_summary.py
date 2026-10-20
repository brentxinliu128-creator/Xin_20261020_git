import os
import sys
import pandas as pd
from sqlalchemy import create_engine
import ollama
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'mydb')
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PATH = os.getenv('DB_PATH', 'database.db')
TABLE_NAME = os.getenv('TABLE_NAME', 'mytable')

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT', 'Table Summary Report')

OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')


def get_db_url():
    if DB_TYPE == 'sqlite':
        return f'sqlite:///{DB_PATH}'
    elif DB_TYPE == 'mysql':
        return f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    elif DB_TYPE == 'postgresql':
        return f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    elif DB_TYPE == 'sqlserver':
        return f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server'
    else:
        raise ValueError(f'Unsupported DB_TYPE: {DB_TYPE}')


def read_table():
    url = get_db_url()
    engine = create_engine(url)
    df = pd.read_table(TABLE_NAME, con=engine)
    return df


def generate_summary(df):
    stats = df.describe(include='all').to_string()
    info = f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
    info += f"Columns: {', '.join(df.columns.tolist())}\n\n"
    info += f"Statistics:\n{stats}\n\n"
    info += f"First 5 rows:\n{df.head().to_string()}\n\n"

    prompt = f"Summarize this table data in a clear, concise report:\n\n{info}"
    response = ollama.chat(model=OLLAMA_MODEL, messages=[
        {'role': 'user', 'content': prompt}
    ])
    return response['message']['content']


def send_email(summary):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = EMAIL_SUBJECT
    msg.attach(MIMEText(summary, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


def main():
    print(f"Reading table '{TABLE_NAME}'...")
    df = read_table()
    print(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns")

    print("Generating summary with local LLM...")
    summary = generate_summary(df)
    print(f"\nSummary:\n{summary}\n")

    if not SMTP_USER or not EMAIL_TO:
        print("SMTP credentials not configured. Skipping email.")
        print("Set SMTP_USER, SMTP_PASSWORD, and EMAIL_TO in .env file.")
        return

    print(f"Sending email to {EMAIL_TO}...")
    send_email(summary)
    print("Email sent successfully!")


if __name__ == '__main__':
    main()
