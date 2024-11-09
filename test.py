from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.params import Body
from typing import Annotated


class Item(BaseModel):
    name: str
    desc: str | None = None
    price : float
    tax : float | None = None


app = FastAPI()

@app.get("/")
def root():
    return {"message": "This is the root page"}

@app.get("/users/me")
def user():
    return  {"message" : "This is your profile page"}

@app.get("/users/{user_id}")
def users(user_id:str):
    return {"User_ID": user_id, "Message":"This is the user's page"}

@app.get("/items/{item_id}")
def get_items(item_id:str, item_name: str, skip: bool = False, buyer: str | None = None):
    item = {"item_id":item_id, "item_name":item_name}
    if skip:
        return {"message": f"item {item_name} unavailable", "buyer": buyer}
    else:
        return item

@app.post("/item/create_item")
def create_item(item: Item, seller_name: Annotated[str,Query(max_length=20,min_length=1)]|None=None):
    if seller_name:
        return [{"seller_name":seller_name},{"item":{**item.dict()}}]
    return {"item":{**item.dict()}}