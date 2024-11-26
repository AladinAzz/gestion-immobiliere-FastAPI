from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # You need to import StaticFiles

app = FastAPI()

# Mount the static directory to serve static files (CSS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Specify the templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Pass data to the template
    return templates.TemplateResponse("index.html", {"request": request, "title": "Accueil - AADL 2.0"})

@app.get("/list", response_class=HTMLResponse)
async def read_list(request: Request):
    # Pass data to the template
    return templates.TemplateResponse("list.html", {"request": request, "title": "Nos Propriétés"})



