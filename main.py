from fastapi import FastAPI

api = FastAPI()

@api.get("/")
def index():
    return {"message": "Hello, World!"}


@api.get("/calculations/{a}")
def calc(a: int):
    return {"result": a * 2}