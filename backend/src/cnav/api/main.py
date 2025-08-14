import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "cnav.api:app",  # Use import string for reload functionality
        host="0.0.0.0",
        port=8001,
        reload=True
    )