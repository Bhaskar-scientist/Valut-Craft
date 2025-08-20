from fastapi import FastAPI

app = FastAPI(title="Test Same Uvicorn")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
