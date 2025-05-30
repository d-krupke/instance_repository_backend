"""
This file serves as the entrypoint for the docker container to start the FastAPI application.
"""

import uvicorn
import os
import logging
from server.sync import sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

if __name__ == "__main__":
    # Sync the repository to the database
    sync()
    # Start the FastAPI application
    IRB_ROOT = os.environ.get("IRB_ROOT", "")
    logging.info("IRB_ROOT set to '%s'", IRB_ROOT)
    uvicorn.run(
        "server.app:app",
        reload=False,
        host="0.0.0.0",
        port=80,
        root_path=IRB_ROOT,
    )
