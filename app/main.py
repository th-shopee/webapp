from sqlalchemy.orm import Session
from . import models, schemas, database
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse,StreamingResponse
from fastapi.templating import Jinja2Templates
import io
import csv
from collections import Counter

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.post("/submit", response_class=HTMLResponse)
def submit_form(
    request: Request,
    basket_id: str = Form(...),
    error_type: str = Form(...),
    station_id: str = Form(...),
    comment: str = Form(None),
    db: Session = Depends(get_db)
):
    print(">> Form Received:", basket_id, error_type, station_id, comment)  # DEBUG

    db_error = models.Error(
        basket_id=basket_id,
        error_type=error_type,
        station_id=station_id,
        comment=comment
    )
    db.add(db_error)
    db.commit()
    db.refresh(db_error)

    return templates.TemplateResponse("thanks.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.get("/data", response_class=HTMLResponse)
def view_data(
    request: Request,
    basket_id: str = "",
    error_type: str = "",
    station_id: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(models.Error)

    if basket_id:
        query = query.filter(models.Error.basket_id.contains(basket_id))
    if error_type:
        query = query.filter(models.Error.error_type.contains(error_type))
    if station_id:
        query = query.filter(models.Error.station_id.contains(station_id))

    results = query.order_by(models.Error.id.desc()).all()

    # Chart: Count by error_type
    error_types = [r.error_type for r in results]
    error_counts = Counter(error_types)
    chart_labels = list(error_counts.keys())
    chart_values = list(error_counts.values())

    return templates.TemplateResponse("data.html", {
        "request": request,
        "data": results,
        "chart_labels": chart_labels,
        "chart_values": chart_values
    })

@app.get("/download")
def download_data(db: Session = Depends(get_db)):
    records = db.query(models.Error).order_by(models.Error.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Basket ID", "Error Type", "Station ID", "Comment"])

    for r in records:
        writer.writerow([r.id, r.basket_id, r.error_type, r.station_id, r.comment])

    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=data.csv"})