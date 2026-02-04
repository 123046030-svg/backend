from fastapi import FastAPI

app = FastAPI(title="Backend Service", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/hello")
def hello(name: str = "world"):
    return {"message": f"Hello, {name}!"}
