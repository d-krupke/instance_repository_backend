if __name__ == "__main__":
    import uvicorn

    uvicorn.run("instance_repository_backend.app:app", reload=False)
