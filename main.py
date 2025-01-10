from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 定义 Task 模型
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# FastAPI 应用
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 首页：显示所有任务
@app.get("/", response_class=HTMLResponse)
async def read_tasks(request: Request):
    db = SessionLocal()
    tasks = db.query(Task).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

# 添加任务
@app.post("/add")
async def add_task(title: str = Form(...)):
    db = SessionLocal()
    db_task = Task(title=title)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return RedirectResponse(url="/", status_code=303)

# 删除任务
@app.get("/delete/{task_id}")
async def delete_task(task_id: int):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)