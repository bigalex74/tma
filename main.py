from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import requests
import docx
import shutil

app = FastAPI(title="bigalexn8n Apps Hub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ВСЕ данные теперь берем из базы postgres (как указал пользователь)
DB_CONFIG_POSTGRES = {
    "host": "127.0.0.1", 
    "database": "postgres", 
    "user": "n8n_user", 
    "password": "n8n_db_password", 
    "port": 5432
}

N8N_WEBHOOK_URL = "https://bigalexn8n.ru/webhook/trigger-translation"

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

def get_conn_pg(): return psycopg2.connect(**DB_CONFIG_POSTGRES)

@app.get("/api/get-form-data")
async def get_form_data():
    try:
        conn = get_conn_pg()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Запрос к таблице telegram_messages в базе postgres
        cur.execute("""
            SELECT 
                type, 
                lang, 
                message->'document'->>'file_name' as name, 
                message->'document'->>'file_id' as file_id 
            FROM telegram_messages 
            WHERE message->'document' IS NOT NULL
            ORDER BY date_time DESC
        """)
        all_items = cur.fetchall()
        
        # Категории данных
        data = {
            "files_ko": [],
            "glossaries": [],
            "prompts_ru": []
        }

        for item in all_items:
            t = (item['type'] or "").lower()
            l = (item['lang'] or "").lower()
            
            # Фильтры пользователя:
            # 1. Файл для перевода: docx/txt + lang: ko
            if t in ['docx', 'txt'] and l == 'ko':
                data['files_ko'].append(item)
            
            # 2. Глоссарий: xlsx (любой язык)
            elif t == 'xlsx':
                data['glossaries'].append(item)
            
            # 3. Промпты: docx/txt + lang: ru
            elif t in ['docx', 'txt'] and l == 'ru':
                data['prompts_ru'].append(item)

        cur.close()
        conn.close()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import httpx
# ... (остальные импорты)

@app.post("/api/start-translation")
async def start_translation(req: StartTranslationRequest):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(N8N_WEBHOOK_URL, json=req.dict(), timeout=10.0)
            print(f"n8n webhook response: {resp.status_code} - {resp.text}")
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail=f"n8n error: {resp.text}")
        return {"status": "success"}
    except Exception as e:
        print(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import shutil

@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        if file.filename.endswith(".docx"):
            # Создаем временный файл
            with open("temp.docx", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            doc = docx.Document("temp.docx")
            full_text = "\n".join([para.text for para in doc.paragraphs])
            os.remove("temp.docx") # Удаляем после обработки
            return {"text": full_text}
        else:
            content = await file.read()
            return {"text": content.decode("utf-8")}
    except Exception as e:
        print(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Промпты для приложения /prompts ---
@app.get("/api/prompts")
async def get_prompts_db():
    conn = get_conn_pg()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, prompt FROM translate_prompts ORDER BY name")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

@app.post("/api/prompts")
async def create_prompt(data: dict):
    try:
        conn = get_conn_pg()
        cur = conn.cursor()
        cur.execute("INSERT INTO translate_prompts (name, prompt) VALUES (%s, %s)", (data['name'], data['prompt']))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        print(f"Error saving new prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/prompts/{prompt_id}")
async def update_prompt(prompt_id: int, data: dict):
    try:
        conn = get_conn_pg()
        cur = conn.cursor()
        cur.execute("INSERT INTO translate_prompts_history (prompt_id, name, prompt, version_date) SELECT id, name, prompt, CURRENT_TIMESTAMP FROM translate_prompts WHERE id = %s", (prompt_id,))
        cur.execute("UPDATE translate_prompts SET name = %s, prompt = %s WHERE id = %s", (data['name'], data['prompt'], prompt_id))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        print(f"Error updating prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/prompts/{prompt_id}")
async def delete_prompt(prompt_id: int):
    conn = get_conn_pg()
    cur = conn.cursor()
    cur.execute("DELETE FROM translate_prompts WHERE id = %s", (prompt_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success"}


@app.get("/api/prompts/{prompt_id}/history")
async def get_prompt_history(prompt_id: int):
    conn = get_conn_pg()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, prompt_id, name, prompt, version_date FROM translate_prompts_history WHERE prompt_id = %s ORDER BY version_date DESC", (prompt_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

@app.get("/", response_class=HTMLResponse)
async def main_hub():
    with open("static/index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/files", response_class=HTMLResponse)
async def files_page():
    with open("static/files/index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/prompts", response_class=HTMLResponse)
async def prompts_page():
    with open("static/prompts/index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/manage-menu", response_class=HTMLResponse)
async def manage_menu():
    with open("static/manage-menu.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/manage", response_class=HTMLResponse)
async def manage_page():
    with open("static/manage/index.html", "r", encoding="utf-8") as f: return f.read()

app.mount("/static", StaticFiles(directory="static"), name="static")
