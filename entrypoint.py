"""
This file serves as the entrypoint for the docker container to start the FastAPI application.
"""

import uvicorn
from server.sync import sync

if __name__ == "__main__":
    # Sync the repository to the database
    sync()
    # Start the FastAPI application
    uvicorn.run("server.app:app", reload=False, host="0.0.0.0", port=80)
