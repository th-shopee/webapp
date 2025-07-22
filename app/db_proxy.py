# db_proxy.py
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import csv
import io

# Connect to your local PostgreSQL
DATABASE_URL = "postgresql://postgres:123@localhost/webapp_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class Error(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, index=True)
    basket_id = Column(String)
    error_type = Column(String)
    station_id = Column(String)
    comment = Column(String)

# Create table
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/submit")
def submit_data(
    basket_id: str = Form(...),
    error_type: str = Form(...),
    station_id: str = Form(...),
    comment: str = Form(None)
):
    db = SessionLocal()
    try:
        error = Error(
            basket_id=basket_id,
            error_type=error_type,
            station_id=station_id,
            comment=comment
        )
        db.add(error)
        db.commit()
        db.refresh(error)
        return {"message": "Data saved successfully"}
    finally:
        db.close()

@app.get("/errors")
def get_errors():
    db = SessionLocal()
    try:
        data = db.query(Error).order_by(Error.id.desc()).all()
        return [
            {
                "id": r.id,
                "basket_id": r.basket_id,
                "error_type": r.error_type,
                "station_id": r.station_id,
                "comment": r.comment
            }
            for r in data
        ]
    finally:
        db.close()

@app.get("/download")
def download_csv():
    db = SessionLocal()
    try:
        records = db.query(Error).order_by(Error.id.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Basket ID", "Error Type", "Station ID", "Comment"])
        for r in records:
            writer.writerow([r.id, r.basket_id, r.error_type, r.station_id, r.comment])
        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=data.csv"})
    finally:
        db.close()
