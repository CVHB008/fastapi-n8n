from fastapi import FastAPI, Path, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
import json

app = FastAPI()

class Item(BaseModel):
    name: str
    model: int
    price: float
    tint: Optional[bool] = None

class UpdateItem(BaseModel):
    name: Optional[str] = None
    model: Optional[int] = None
    price: Optional[float] = None
    tint: Optional[bool] = None

# Load JSON on startup
my_cars = {}

@app.on_event("startup")
def load_data():
    global my_cars
    with open("data.json", "r") as file:
        data = json.load(file)
        # Convert dicts into Item objects
        my_cars = {int(k): Item(**v) for k, v in data.items()}

@app.get("/get-by-id/{item_id}")
def get_by_id(item_id:int = Path(description="This is the id of the data you like to view")):
    if item_id not in my_cars:
        raise HTTPException(status_code=404, detail="Item ID not found")
    return my_cars[item_id]

@app.get("/get-by-name")
def get_by_name(name: Optional[str] = None):
    for item_id in my_cars:
        if my_cars[item_id].name == name:
            return my_cars[item_id]
    raise HTTPException(status_code=404, detail="Item name not found")

@app.post("/create-item/{item_id}")
def create_item(item_id:int, item:Item):
    if item_id in my_cars:
        raise HTTPException(status_code=400, detail="Item ID already exists.")
    my_cars[item_id] = item
    return my_cars[item_id]

@app.patch("/patch-item/{item_id}")
def patch_item(item_id: int, item: UpdateItem):
    if item_id not in my_cars:
        raise HTTPException(status_code=404, detail="Item not found")

    # Only update provided fields
    if item.name != None:
        my_cars[item_id].name = item.name
    if item.model != None:
        my_cars[item_id].model = item.model
    if item.price != None:
        my_cars[item_id].price = item.price
    if item.tint != None:
        my_cars[item_id].tint = item.tint

    return my_cars[item_id]

@app.put("/update-item/{item_id}")
def update_item(item_id:int, item:UpdateItem):
    if item_id not in my_cars:
        raise HTTPException(status_code=404, detail="Item ID does not exist")

    stored_item = my_cars[item_id]
    updated_item = stored_item.copy(update=item.dict(exclude_unset=True))
    my_cars[item_id] = updated_item
    return my_cars[item_id]

@app.delete("/delete-item")
def delete_item(item_id: int = Query(..., description="The ID of the item you want to delete")):
    if item_id not in my_cars:
        raise HTTPException(status_code=404, detail="Item ID does not exist")
    del my_cars[item_id]
    return {"Success" : "Item deleted"}
