# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx
from collections import Counter

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set this to your current ngrok HTTPS URL
NGROK_URL = "https://annually-safe-dog.ngrok-free.app"

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/submit", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    basket_id: str = Form(...),
    error_type: str = Form(...),
    station_id: str = Form(...),
    comment: str = Form(None)
):
    async with httpx.AsyncClient() as client:
        data = {
            "basket_id": basket_id,
            "error_type": error_type,
            "station_id": station_id,
            "comment": comment,
        }
        try:
            res = await client.post(f"{NGROK_URL}/submit", data=data)
            res.raise_for_status()
        except Exception as e:
            return HTMLResponse(f"<h1>Submission Failed: {e}</h1>", status_code=500)

    return templates.TemplateResponse("thanks.html", {"request": request})

@app.get("/data", response_class=HTMLResponse)
async def view_data(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{NGROK_URL}/errors")
            res.raise_for_status()
            results = res.json()
        except Exception as e:
            return HTMLResponse(f"<h1>Error Loading Data: {e}</h1>", status_code=500)

    error_counts = Counter([r["error_type"] for r in results])
    chart_labels = list(error_counts.keys())
    chart_values = list(error_counts.values())

    return templates.TemplateResponse("data.html", {
        "request": request,
        "data": results,
        "chart_labels": chart_labels,
        "chart_values": chart_values
    })

@app.get("/download")
async def download_data():
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{NGROK_URL}/download")
            res.raise_for_status()
            return HTMLResponse(res.text, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=data.csv"})
        except Exception as e:
            return HTMLResponse(f"<h1>Download Failed: {e}</h1>", status_code=500)
