from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def read_hello(name: str = "World"):
   return {"message": f"Hello, {name}!"}

@app.get("/")
def root():
   return "Heath Check Sucessfull"