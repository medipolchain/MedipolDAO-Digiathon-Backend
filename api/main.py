from fastapi import FastAPI, Request
from api.db_wrapper import DbWrapper

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from web3 import Web3

import pydantic
from bson.objectid import ObjectId

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

origins = [
    "http://localhost:3000"
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=['*'],  # origins if domain is mentioned
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
]

app = FastAPI(middleware=middleware)
db = DbWrapper()
web3 = Web3()


@app.get("/")
async def root(info: Request):
    """
    :return: a welcoming screen
    :return:
    """
    try:
        return "MedipolDAO Digiathon API"

    except Exception as e:
        return e


@app.get("/user_exists/")
async def user_exists(info: Request) -> bool:
    """
    :param tckn: TCKN of the user
    :return: a boolean indicating if the user exists
    """
    try:
        req = await info.json()
        if req['tckn']:
            exists = db.user_exists_by_tckn(req['tckn'])

            return exists
        else:
            return {
                "message": "Please provide TCKN!"
            }

    except Exception as e:
        return e


# Admin permission only should be added
@app.get("/get_users")
async def get_users(info: Request):
    """
    :return: a list of all the users
    """
    try:
        users = db.get_users()
        return users

    except Exception as e:
        return e

@app.get("/get_meskens")
async def get_meskens():
    """
    :return: meskens
    """
    try:
        meskens = db.get_meskens()
        if meskens:
            return meskens
        else:
            return {
                "message": "You are not authorized to view this page"
            }

    except Exception as e:
        return e

@app.post('/get_mesken')
async def get_mesken(info: Request):
    """
    :return: mesken
    """
    try:
        req = await info.json()
        mesken = db.get_mesken(req['meskenId'])
        if mesken:
            return mesken
        else:
            return {
                "message": "You are not authorized to view this page"
            }

    except Exception as e:
        return e

@app.post('/add_maintenance')
async def add_maintenance(info: Request):
    """
    :return: mesken
    """
    try:
        req = await info.json()
        maintenance = db.add_maintenance(req['meskenId'], req['maintenance'], req["token"])
        return maintenance

    except Exception as e:
        return e

@app.post('/put_on_sale')
async def put_on_sale(info: Request):
    try:
        req = await info.json()
        token = req["token"]

        sale_info = {
            "meskenId": req["meskenId"],
            "price": req["price"],
            "amount": req["amount"],
        }

        user = db.put_on_sale(token, sale_info)

        return user

    except Exception as e:
        return e

# Admin permission only should be added
@app.post("/get_user_by_tckn")
async def get_user_by_tckn(info: Request):
    """
    :return: a user by TCKN
    """
    try:
        req = await info.json()
        if req["tckn"]:
            user = db.get_user_by_tckn(req["tckn"])
            return user
        else:
            return {
                "message": "You are not authorized to view this page"
            }

    except Exception as e:
        return e


# Admin permission only should be added
@app.post("/get_user")
async def get_user_by_public_address(info: Request):
    """
    :return: a user by public address
    """
    try:
        req = await info.json()
        if req["publicAddress"]:
            user = db.get_user(req["publicAddress"])
            return user
        else:
            return {
                "message": "You are not authorized to view this page"
            }

    except Exception as e:
        return e


# Admin permission only should be added
@app.post("/set_user")
async def set_user(info: Request):
    """
    :return: the user id
    """
    try:
        req = await info.json()
        user_info = {
            "tckn": req["tckn"],
            "password": req["password"],
            "publicAddress": "",
            "name": req["name"],
            "surname": req["surname"],
            "nonce": 0,
            "meskenlerim": [],
        }
        user_id = db.set_user(user_info)

        return user_id

    except Exception as e:
        return e

@app.post("/set_mesken")
async def set_mesken(info: Request):
    """
    :return: the mesken id
    """
    try:
        req = await info.json()
        token = req["token"]
        mesken_info = {
            "meskenId": req["meskenId"],
            "ilId": req["ilId"],
            "parselId": req["parselId"],
            "zeminId":req["zeminId"],
            "parselNo" :req["parselNo"],
            "mahalleId": req["mahalleId"],
            "adaNo":req["adaNo"],
            "ilceId": req["ilceId"],
            "katNo": req["katNo"],
            "kapiNo": req["kapiNo"],
            "rayicFiyat": req["rayicFiyat"],
            "pay": req["pay"],
            "payda": req["payda"],
            "status": req["status"],
            "auctionInfo":{},
            "saleHistory":[],
            "saleInfo":{},
            "maintenanceHistory":[],
            "age": req["age"],
            "tckn": req["tckn"],
        }
        mesken_id = db.set_mesken(mesken_info,token)

        return mesken_id

    except Exception as e:
        return e


@app.post("/update_public_address")
async def update_public_address(info: Request):
    """
    :return: the user id
    """
    try:
        req = await info.json()

        user_id = db.update_user_public_address(
            user_public_address=req["publicAddress"],
            tckn=req["tckn"]
        )

        return user_id

    except Exception as e:
        return e

@app.post("/update_mesken")
async def update_mesken(info: Request):
    """
    :return: the mesken id
    """
    try:
        req = await info.json()
        token = req["token"]
        meskenObjectId= req["meskenObjectId"]
        meskenTokenId= req["meskenTokenId"]
        mesken_info = {
            "date": req["date"],
            "desc": req["desc"],
            "price": req["price"],
        }
        mesken_id = db.update_mesken(token,meskenObjectId,meskenTokenId,mesken_info)

        return mesken_id

    except Exception as e:
        return e



@app.post("/user_jwt")
async def user_jwt(info: Request):
    """
    :return: the user id
    """
    try:
        req = await info.json()

        token = db.user_jwt(req["tckn"])

        return token

    except Exception as e:
        return e

@app.post('/login')
async def login(info: Request):
    """
    :return: the user id
    """
    try:
        req = await info.json()

        user = db.login(req["tckn"],req["password"])

        return user

    except Exception as e:
        return e

@app.post('/verify')
async def verify(info: Request):
    """
    :return: the user id
    """
    try:
        req = await info.json()

        user = db.verify(req["token"])

        return user

    except Exception as e:
        return e