from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from main import QuestGenerator
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# Настройка путей
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Создаем необходимые папки
(BASE_DIR / "templates").mkdir(exist_ok=True)
(BASE_DIR / "static/css").mkdir(exist_ok=True, parents=True)
(BASE_DIR / "static/js").mkdir(exist_ok=True, parents=True)
(BASE_DIR / "uploads").mkdir(exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Инициализация генератора с ключом из .env
from main import QuestGenerator
generator = QuestGenerator(api_key=os.getenv("GROQ_API_KEY"))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница только с загрузкой файла"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate/")
async def generate_quest(request: Request, file: UploadFile = Form(...)):
    """Обработка генерации квеста из загруженного файла"""
    try:
        # Сохраняем загруженный файл
        upload_dir = BASE_DIR / "uploads"
        input_file = upload_dir / file.filename
        
        with open(input_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Генерация квеста
        quest_data = generator.generate_quest(str(input_file))
        output_file = BASE_DIR / "quest.json"
        generator.save_to_json(quest_data, str(output_file))
        
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "quest": quest_data,
                "json_file": "quest.json",
                "input_filename": file.filename
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)}
        )

@app.get("/download/quest.json")
async def download_quest():
    """Скачивание сгенерированного квеста"""
    return FileResponse(
        "quest.json",
        media_type="application/json",
        filename="generated_quest.json"
    )

@app.get("/download/sample.txt")
async def download_sample():
    """Скачивание примера входного файла"""
    sample_content = """жанр: киберпанк
герой: хакер-одиночка
цель: взломать корпоративный сервер МегаКорп"""
    
    sample_path = BASE_DIR / "sample.txt"
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    return FileResponse(
        sample_path,
        media_type="text/plain",
        filename="sample_input.txt"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)