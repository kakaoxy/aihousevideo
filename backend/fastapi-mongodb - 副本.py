from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from pathlib import Path
from fastapi.responses import JSONResponse
from bson import json_util
import os
from datetime import datetime
from typing import List
import logging
import json
# 导入generate_video.py中的generate_video函数
from generate_video import generate_video
from generate_video import logger

app = FastAPI()

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HousingData(BaseModel):
    description: str
    community: str
    area: float
    layout: str
    floor: str
    total_price: int
    images: List[str]

# 连接到 MongoDB
uri = "mongodb://localhost:27017/"
client = MongoClient(uri)
try:
    client.admin.command('ping')
    logger.info("Connected successfully")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
database = client["aihousevideo"]
collection = database["houseings"]

@app.post("/add_housing/")
async def add_housing(data: HousingData):
    try:
        new_data = {
            "house_id": ObjectId(),
            "description": data.description,
            "community": data.community,
            "area": data.area,
            "layout": data.layout,
            "floor": data.floor,
            "total_price": data.total_price,
            "images": data.images,
            "is_video_generated": False
        }
        result = collection.insert_one(new_data)
        logger.info(f"Housing added successfully with inserted_id: {result.inserted_id}")
        return {"message": "Housing added successfully", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Failed to add housing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

BASE_DIR = Path(__file__).resolve().parent / "uploaded_images"
os.makedirs(BASE_DIR, exist_ok=True)

app.mount("/uploaded_images", StaticFiles(directory=BASE_DIR), name="uploaded_images")

@app.post("/upload/image")
async def upload_image(files: List[UploadFile] = File(...)):
    folder_name = datetime.now().strftime("%Y%m%d%H%M%S")
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

            image_url = f"http://192.168.100.198:8000/uploaded_images/{folder_name}/{file_name}"
            image_urls.append(image_url)
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"imageUrls": image_urls})

@app.get("/get_latest_housings")
async def get_latest_housings():
    try:
        housings = collection.find().sort("_id", -1).limit(10)
        housings_list = []
        for housing in housings:
            housing_json = json.loads(json_util.dumps(housing))
            housing_json["images"] = [url.replace("http://127.0.0.1:8000/", "http://192.168.100.198:8000/uploaded_images/") for url in housing_json["images"]]
            housings_list.append(housing_json)
        
        return {"housings": housings_list}
    except Exception as e:
        logger.error(f"Failed to get latest housings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_video")
async def generate_video_endpoint(data: dict):
    try:
        house_id = data.get("house_id")
        housing_id = ObjectId(house_id)
        print('接收到房屋id:', house_id)
        print('处理后的房屋id:', housing_id)

            
        housing = collection.find_one({"_id": housing_id})
        if not housing:
            raise HTTPException(status_code=404, detail="Housing not found")

        housing_data = json.loads(json_util.dumps(housing))

        house_info = f"{housing_data['description']}{housing_data['community']}{housing_data['area']}{housing_data['layout']}{housing_data['floor']}{housing_data['total_price']}"
        house_title = housing_data['community']
        logger.info('接收到房屋信息: %s', house_info)
        logger.info('接收到房屋标题: %s', house_title)
        logger.info('接收到房屋图片: %s', housing_data['images'])

        # 处理图片路径
        image_paths = [url.replace('http://192.168.100.198:8000/', './') for url in housing_data['images']]
        

        print('信息已经准备好，开始生成视频，请稍等...', house_title, house_info, image_paths)

        # 调用生成视频的函数
        video_url = generate_video(house_title, house_info, image_paths)
        # video_url = "./uploaded_images/20241103144135\Video_of_西郊景平苑.mp4"
        # 检查视频是否生成成功,如果成功就修改数据库中的is_video_generated字段为True，同时在数据中添加一个video_url字段，值为视频的url
        print('视频已经生成，下载地址为：', video_url)   
        if video_url:
            # 更新数据库中的is_video_generated字段为True，同时在数据中添加一个video_url字段，值为视频的url，捕获异常
            try:
                collection.update_one({"_id": housing_id}, {"$set": {"is_video_generated": True, "video_url": video_url}})
                return {
                    "message": "视频生成成功",
                    "video_url": video_url
                }
            except Exception as e:
                logger.error(f"数据库更新失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        else:
            return {
                "message": "视频生成失败"
            }


    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发生错误: {str(e)}")


# 获取日志信息
def get_log():
    with open('video_generation.log', 'r', encoding='utf-8') as f:
        log_content = f.read()
    return log_content

@app.get("/get_log")
async def get_log_endpoint():
    try:
        log_content = get_log()
        return {"log": log_content}
    except Exception as e:
        logger.error(f"获取日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
