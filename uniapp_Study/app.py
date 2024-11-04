from fastapi import FastAPI, File, UploadFile, HTTPException, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config
import os
import datetime
import json
from bson import json_util
from typing import List

app = FastAPI()

# MongoDB configuration
mongo_client = AsyncIOMotorClient(config("MONGO_URI"))
db = mongo_client[config("MONGO_DB_NAME")]
collection = db[config("MONGO_COLLECTION_NAME")]

# Base directory for uploaded files
BASE_DIR = config("BASE_DIR", default="uploaded_images")
os.makedirs(BASE_DIR, exist_ok=True)

# Server host configuration
SERVER_HOST = config("SERVER_HOST", default="http://localhost")

# Define the upload image route
@app.post("/upload/image")
async def upload_image(files: List[UploadFile] = File(...)):
    folder_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    folder_path = os.path.join(BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    image_urls = []

    for file in files:
        try:
            file_content = await file.read()
            file_name = file.filename
            file_path = os.path.join(folder_path, file_name)

            with open(file_path, "wb") as f:
                f.write(file_content)

            image_url = f"{SERVER_HOST}/uploaded_images/{folder_name}/{file_name}"
            image_urls.append(image_url)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"imageUrls": image_urls})

# Define the get latest housings route
@app.get("/get_latest_housings")
async def get_latest_housings():
    try:
        housings = collection.find().sort("_id", -1).limit(10)
        housings_list = []
        for housing in housings:
            housing_json = json.loads(json_util.dumps(housing))
            housing_json["id"] = str(housing_json["_id"])
            del housing_json["_id"]
            housing_json["images"] = [url.replace("http://localhost", f"{SERVER_HOST}/uploaded_images/") for url in housing_json["images"]]
            housings_list.append(housing_json)
        
        return {"housings": housings_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config("HOST", default="0.0.0.0"), port=config("PORT", default=8000, cast=int))
