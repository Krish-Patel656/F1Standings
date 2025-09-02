from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Query
import fastf1
import os

# Setup FastF1 cache directory (adjust path if needed)
os.makedirs('cache', exist_ok=True)
fastf1.Cache.enable_cache('cache')

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name ="static")

year_Rounds = {
    2020: 17,
    2021: 23,
    2022: 22,
    2023: 24,
    2024: 24
}

# Home page: Show form with year and round dropdowns
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    years = list(year_Rounds.keys())
    # For simplicity, rounds 1 to 24 (max possible rounds)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "years": years,
    })

# Results page: Accept form submission via POST
@app.post("/results", response_class=HTMLResponse)
async def show_results(request: Request, year: int = Form(...), round: int = Form(...)):
    try:
        session = fastf1.get_session(year, round, 'R')  # Race session
        session.load()  # Load session data from cache

        results = session.results
        positions = []
        for _, row in results.iterrows():
            positions.append({
                "position": int(row["Position"]),
                "driver": row["Abbreviation"],
                "team": row["TeamName"]
            })

    except Exception as e:
        positions = []
        error_msg = str(e)
    else:
        error_msg = None

    return templates.TemplateResponse("results.html", {
        "request": request,
        "year": year,
        "round": round,
        "positions": positions,
        "error_msg": error_msg
    })

@app.get("/get_races")
async def get_races(year:int = Query(...)):
    race_counts = {
        2020: list(range(1,18)),
        2021: list(range(1,24)),
        2022: list(range(1,23)),
        2023: list(range(1,25)),
        2024: list(range(1,25)),
    }
    rounds = race_counts.get(year,[])
    return JSONResponse(content={"rounds": rounds})
