import pandas as pd

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.cursor import Cursor
from pymongo.database import Database

from timeit import default_timer as timer

import os

from dotenv import load_dotenv

file_path = os.path.join('Data', 'data.csv') 

load_dotenv()
uri = os.getenv('MONGODB_URI')

_sorted_df : pd.DataFrame


def loadData(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, header=None, names=["raw"])
    return df

def normalizeData(df: pd.DataFrame) -> pd.DataFrame:
    df[['numerical_id', 'numerical_value']] = df['raw'].str.split('_', expand=True)
    df['numerical_value'] = df['numerical_value'].astype(int)
    df = df.drop(columns=['raw'])
    return df

def sortData(df: pd.DataFrame) -> pd.DataFrame:
    sorted_df = df.sort_values(by='numerical_value', ascending=False, kind="mergesort")
    return sorted_df

def getTopValues(topVals: int):
    global _sorted_df
    return _sorted_df.head(topVals).to_dict(orient='records')

def init() -> pd.DataFrame:
    df = loadData(file_path)
    df = normalizeData(df)
    return df

def initAndSort() -> pd.DataFrame:
    df = loadData(file_path)
    df = normalizeData(df)
    global _sorted_df
    _sorted_df = sortData(df)    


def connectToDb() -> MongoClient:
    client = MongoClient(uri, server_api=ServerApi('1'), maxPoolSize=50)
    try:
        client.admin.command('ping')
        print("Connected to DB")
        return client
    except Exception as e:
        print(e)

def getCollection(collectionName: str) -> Database:
    client = connectToDb()
    db = client["Test"]
    return db[collectionName]
    

def insertDataToDb(collectionName: str) -> None:
    collection = getCollection(collectionName)
    normalizedDf = init()
    start = timer()
    collection.insert_many(normalizedDf.to_dict(orient='records'))
    end = timer()
    print(end - start)


def getTopInDb(topVals: int, dbName: str) -> Cursor:
    collection = getCollection(dbName)
    return collection.find().sort("numerical_value", -1).limit(topVals)

def formatResult(cursor: Cursor) -> dict:
    return [{"numerical_id": doc['numerical_id'], "numerical_value": doc['numerical_value']} for doc in cursor]
    