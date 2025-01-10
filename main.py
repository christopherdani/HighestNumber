from fastapi import FastAPI

from processData import *

from timeit import default_timer as timer


app = FastAPI()

@app.get("/")
async def root() -> None:
    return {"message": "Hello"}

@app.post("/initialize")
async def initialize() -> None:
    start = timer()
    initAndSort()
    end = timer()
    return {"time" : end - start,
            "message": "initialized data in dataframe, normalized and sorted."}

@app.get("/top/{top_value}")
async def getTopIds(top_value: int, method: str):
    match method:
        case "db":
            start = timer()
            cursor = getTopInDb(top_value, "Test")
            formattedResult = formatResult(cursor)
            end = timer() 
            searchTime = end - start 
        case "df":
            start = timer()
            formattedResult = getTopValues(int(top_value))
            end = timer()
            searchTime = end - start
        case "index":
            start = timer()
            cursor = getTopInDb(top_value, "Indexed-Test")
            formattedResult = formatResult(cursor)
            end = timer() 
            searchTime = end - start  
    return {"search duration" : searchTime,
            "top values": formattedResult}

