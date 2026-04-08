from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import requests
import httpx
import docx
import shutil

app = FastAPI(title="bigalexn8n Apps Hub")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

N8N_WEBHOOK_URL = "https://bigalexn8n.ru/webhook/trigger-translation"
DB_CONFIG_POSTGRES = {"host": "127.0.0.1", "database": "postgres", "user": "n8n_user", "password": "n8n_db_password", "port": 5432}

def get_conn_pg(): return psycopg2.connect(**DB_CONFIG_POSTGRES)

class StartTranslationRequest(BaseModel):
    file_id: str
    file_name: str
    bp_file_id: str = None
    bp_file_name: str = None
    pp_file_id: str = None
    pp_file_name: str = None
    glossary_id: str = None
    glossary_file_name: str = None
    create_glossary: bool = False

@app.get("/api/get-form-data")
async def get_form_data():
    conn = get_conn_pg()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT type, lang, message->'document'->>'file_name' as name, message->'document'->>'file_id' as file_id FROM telegram_messages WHERE message->'document' IS NOT NULL AND (is_translate IS NULL OR is_translate = false) ORDER BY date_time DESC")
    all_items = cur.fetchall()
    cur.close()
    conn.close()
    return {
        "files_ko": [f for f in all_items if f['lang'] == 'ko'],
        "glossaries": [f for f in all_items if f['type'] == 'xlsx'],
        "prompts_ru": [f for f in all_items if f['lang'] == 'ru']
    }

@app.post("/api/start-translation")
async def start_translation(req: StartTranslationRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(N8N_WEBHOOK_URL, json=req.dict(), timeout=10.0)
        return {"status": "success"}

@app.post("/api/files/hide")
async def hide_files(data: dict):
    file_ids = data.get("file_ids", [])
    conn = get_conn_pg()
    cur = conn.cursor()
    cur.execute("UPDATE telegram_messages SET is_translate = true WHERE message->'document'->>'file_id' = ANY(%s)", (file_ids,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success"}

@app.get("/", response_class=HTMLResponse)
async def main_hub():
    with open("static/index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/files", response_class=HTMLResponse)
async def files_page():
    with open("static/files/index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/manage-menu", response_class=HTMLResponse)
async def manage_menu():
    with open("static/manage-menu.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/manage", response_class=HTMLResponse)
async def manage_page():
    with open("static/manage/index.html", "r", encoding="utf-8") as f: return f.read()

app.mount("/static", StaticFiles(directory="static"), name="static")
