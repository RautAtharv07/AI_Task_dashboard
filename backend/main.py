
from fastapi import FastAPI
from database import engine, Base
import models
from routes import auth_routes, task_routes , summary
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()



Base.metadata.create_all(bind=engine)



app.include_router(auth_routes.router, prefix="")
app.include_router(task_routes.router, prefix="")
app.include_router(summary.router, prefix="")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify exact frontend URL like ["http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods including OPTIONS
    allow_headers=["*"],  # Allows all headers
)
