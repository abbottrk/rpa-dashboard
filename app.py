import streamlit as st
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine
from datetime import datetime
import socket
import threading

# ---------------- DATABASE ----------------
DATABASE_URL = "YOUR_SUPABASE_POSTGRES_URL"

engine = create_engine(DATABASE_URL)

# ---------------- FASTAPI ----------------
api = FastAPI()

class LogEntry(BaseModel):
    bot_name: str
    status: str
    duration_seconds: int
    pc_name: str

@api.post("/log")
def log_data(entry: LogEntry):

    query = """
        INSERT INTO automation_logs
        (timestamp, bot_name, status, duration_seconds, pc_name)
        VALUES (%s, %s, %s, %s, %s)
    """

    with engine.connect() as conn:
        conn.execute(query, (
            datetime.now(),
            entry.bot_name,
            entry.status,
            entry.duration_seconds,
            entry.pc_name
        ))
        conn.commit()

    return {"message": "Logged successfully"}

# ---------------- STREAMLIT ----------------
def run_dashboard():

    st.title("RPA Control Center")

    df = pd.read_sql("SELECT * FROM automation_logs ORDER BY timestamp DESC", engine)

    st.dataframe(df)

# ---------------- THREADING ----------------
def run_api():
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)

threading.Thread(target=run_api).start()

run_dashboard()
