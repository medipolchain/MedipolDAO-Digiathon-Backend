import jwt
import os
import time
from web3 import Web3
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
from fastapi.exceptions import HTTPException
from datetime import datetime, timezone, timedelta
from eth_account.messages import encode_defunct
from collections import OrderedDict

from functools import wraps

import pydantic
from bson.objectid import ObjectId

pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

load_dotenv(find_dotenv())


class DbWrapper:
    def __init__(self):
        self.setup()

    def setup(self) -> bool:
        """
        :return: True if connected to the MongoDB, Error otherwise
        """
        try:
            self.connection_string = os.environ.get("MONGODB_PWD")
            self.client = MongoClient(self.connection_string)
            self.web3 = Web3()

        except Exception as e:
            print(e)
            return e

    def get_database_names(self):
        """
        :return: a list of all the database names
        """
        try:
            dbs = self.client.list_database_names()
            return dbs

        except Exception as e:
            print(e)
            return e

    def get_database(self, db_name: str):
        """
        :param db_name: the name of the database to get
        :return: the database object
        """
        try:
            db = self.client[db_name]
            return db

        except Exception as e:
            print(e)
            return e

    def get_collections_names(self, db_name: str):
        """
        :param db_name: the name of the database to get the collections from
        :return: a list of all the collections in the database
        """
        try:
            db = self.get_database(db_name)
            collections = db.list_collection_names()
            return collections

        except Exception as e:
            print(e)
            return e

    def get_collection(self, collection_name: str):
        """
        :param db_name: the name of the database to get the collection from
        :param collection_name: the name of the collection to get
        :return: the collection object
        """
        try:
            db = self.get_database("medipoldao-digiathon")
            collection = db[collection_name]
            return collection

        except Exception as e:
            print(e)
            return e

    def set_user(self, user_info: dict):
        """
        :param user_info: the user info to set
        :return: the user id
        """
        """
        user_info = {
            "tckn": "12345678901",
            "nonce": 0
        }
        """
        try:
            if self.user_exists_by_tckn(user_info["tckn"]):
                return HTTPException(status_code=400, detail="User already exists. Try updating it!")

            if user_info["tckn"] and len(user_info["tckn"]) == 11:

                collection_name = "users"

                collection = self.get_collection(collection_name)
                user = collection.insert_one(user_info).inserted_id
                return user

            else:
                return HTTPException(status_code=400, detail="Invalid TCKN")

        except Exception as e:
            print(e)
            return e

    def user_exists_by_tckn(self, user_tckn: str):
        """
        :return: True if the user exists, False otherwise
        :param user_public_address: the public address of the user to check
        """
        try:
            collection_name = "users"

            collection = self.get_collection(collection_name)
            user = collection.find_one({
                "tckn": user_tckn
            })
            return user is not None

        except Exception as e:
            print(e)
            return e

    def user_exists(self, user_public_address: str) -> bool:
        """
        :return: True if the user exists, False otherwise
        :param user_public_address: the public address of the user to check
        """
        try:
            collection_name = "users"

            collection = self.get_collection(collection_name)
            user = collection.find_one({
                "publicAddress": user_public_address
            })
            return user is not None

        except Exception as e:
            print(e)
            return e

    def update_user_public_address(self, user_public_address: str, tckn: str):
        """
        Set user public address to user_public_address by finding the user by its tckn
        """
        try:
            if self.user_exists_by_tckn(tckn):
                collection_name = "users"
                collection = self.get_collection(collection_name)

                collection.update_one({
                    "tckn": tckn
                }, {
                    "$set": {
                        "publicAddress": user_public_address
                    }
                })
                return {
                    "message": "User public address updated successfully"
                }
            else:
                return {
                    "message": "User does not exist"
                }

        except Exception as e:
            print(e)
            return e

    def user_check(self, user_public_address: str):
        """
        :param user_public_address: the user public address
        :return: the user if exists
        """
        try:
            collection_name = "users"

            collection = self.get_collection(collection_name)

            if self.user_exists(user_public_address):
                user = collection.find_one({"publicAddress": user_public_address})
                if user:
                    return HTTPException(status_code=200, detail={
                        "message": "User retrieved successfully",
                        "user": user
                    })
                else:
                    return HTTPException(status_code=404, detail={
                        "message": "User not found"
                    })
            else:
                return HTTPException(status_code=404, detail={
                    "message": "User not found"
                })

        except Exception as e:
            print(e)
            return

    def update_user_nonce(self, user_public_address: str, nonce: int):
        """
        :param user_public_address: the public address of the user to update
        :param nonce: the nonce to set
        :return: True if the user was updated, Error otherwise
        """
        try:
            if self.user_exists(user_public_address):
                collection_name = "users"

                collection = self.get_collection(collection_name)
                collection.update_one({"publicAddress": user_public_address}, {"$set": {"nonce": nonce}})
                return True
            else:
                return "Such user does not exist"

        except Exception as e:
            print(e)
            return

    def user_jwt(self, tckn: str):
        try:
            user_exists = self.user_exists_by_tckn(tckn)
            if user_exists:
                token = jwt.encode(
                    {
                        "tckn": tckn,
                        "exp": datetime.now(tz=timezone.utc) + timedelta(days=7),
                    },
                    os.environ.get("SECRET"),
                    algorithm="HS256",
                )

                return HTTPException(status_code=200, detail={
                    "message": "User authenticated",
                    "token": token,
                })
            else:
                return HTTPException(status_code=404, detail={
                    "message": "User not found"
                })

        except Exception as e:
            print(e)
            return e

    def verify(self, token: str):
        try:
            decoded = jwt.decode(token, os.environ.get("SECRET"), algorithms=["HS256"])
            return HTTPException(status_code=200, detail={
                "message": "User verified",
                "user": decoded
            })
        except Exception as e:
            print(e)
            return e

    def login(self, tckn: str, password: str):
        """
        :return: True if the user exists, False otherwise
        :param
        """
        try:
            if not self.user_exists_by_tckn(tckn):
                return HTTPException(status_code=400, detail="User does not exist!")

            collection_name = "users"

            collection = self.get_collection(collection_name)
            user = collection.find_one({
                "tckn": tckn
            })

            if user["password"] == password:
                return True
            else:
                return False

        except Exception as e:
            print(e)
            return e

    def get_users(self):
        """
        :param db_name: the name of the database to get the users from
        :param collection_name: the name of the collection to get the users from
        :return: a list of all the users in the collection
        """
        try:

            collection_name = "users"

            collection = self.get_collection(collection_name)
            users = collection.find()
            users_list = [i for i in users]
            return {i: users_list[i] for i in range(len(users_list))}

        except Exception as e:
            print(e)
            return e
