import uvicorn
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/")
def read_root():
    """
    Get the root endpoint.

    Returns:
        dict: A dictionary with a single key "message" and the value "Hello World".
"""
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)
    #  uvicorn main:app --host localhost --port 8000
