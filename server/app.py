import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.app_config import PROBLEMS


logging.basicConfig(level=logging.INFO)

# read from environment variable
IRB_ROOT = os.getenv("IRB_ROOT", "/")
app = FastAPI(root_path=IRB_ROOT)

# Add CORS middleware to allow public access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",  # Allow requests from localhost
        "http://localhost:8080",  # Allow requests from localhost with port 8080
        "https://alg.ibr.cs.tu-bs.de",  # Allow requests from the ibr domain
    ],
    allow_credentials=False,  # Disable cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

for problem in PROBLEMS:
    problem.build_routes(app)
