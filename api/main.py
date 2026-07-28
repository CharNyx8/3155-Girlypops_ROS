import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies.config import conf
from .models import model_loader
from .routers import index as index_route


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_loader.index()
index_route.load_routes(app)


if __name__ == "__main__":
    uvicorn.run(app, host=conf.app_host, port=conf.app_port)