
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Tuple
from src.models.users import User, UserCreate, UserUpdate
from src.libs.db import db_connection
from pymysql.err import IntegrityError

class UserRouter:
    def __init__(self):
        self.router = APIRouter()

        self.router.add_api_route("/", self.list_users, methods=["GET"])
        self.router.add_api_route("/{user_id}", self.read_user, methods=["GET"])
        self.router.add_api_route("/", self.create_user, methods=["POST"])
        self.router.add_api_route("/{user_id}", self.update_user, methods=["PUT"])
        self.router.add_api_route("/{user_id}", self.delete_user, methods=["DELETE"])

    async def list_users(self, db = Depends(db_connection)) -> List[User]:
        with db.cursor() as cursor:
            sql_stmt: str = """
                SELECT
                    id,
                    username,
                    email
                FROM
                    users
            """
            cursor.execute(sql_stmt)
            result = cursor.fetchall()
        return result

    async def read_user(self, user_id: int, db = Depends(db_connection)):
        with db.cursor() as cursor:
            sql_stmt: str = """
                SELECT
                    id,
                    username,
                    email
                FROM
                    users
                WHERE
                    id = %s
            """
            args: Tuple = (user_id,)
            cursor.execute(sql_stmt, args)
            result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="User not found")
        return result

    async def create_user(self, user: UserCreate, db = Depends(db_connection)):
        with db.cursor() as cursor:
            sql_stmt: str = """
                INSERT INTO
                    users (username, email, password)
                VALUES
                    (%s, %s, %s)
            """
            args: Tuple = (user.username, user.email, user.password)
            try:
                cursor.execute(sql_stmt, args)
                db.commit()
                user_id = cursor.lastrowid
            except IntegrityError as error:
                raise HTTPException(status_code=500, detail="User already exist")
        return {**user.dict(), "id": user_id}

    async def update_user(self, user_id: int, user: UserUpdate, db = Depends(db_connection)):
        with db.cursor() as cursor:
            sql_stmt: str = """
                SELECT
                    id,
                    username,
                    email
                FROM
                    users
                WHERE id = %s
            """
            args: Tuple = (user_id,)
            cursor.execute(sql_stmt, args)
            existing_user = cursor.fetchone()
        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user.dict(exclude_unset=True)
        with db.cursor() as cursor:
            sql_stmt: str = """
                UPDATE users SET username = %s, email = %s WHERE id = %s
            """
            args: Tuple = (
                update_data.get("username", existing_user["username"]),
                update_data.get("email", existing_user["email"]),
                user_id
            )
            cursor.execute(sql_stmt, args)
            db.commit()
        return {**existing_user, **update_data}

    async def delete_user(self, user_id: int, db = Depends(db_connection)):
        with db.cursor() as cursor:
            sql_stmt: str = """
                SELECT id FROM users WHERE id = %s
            """
            args: Tuple = (user_id,)
            cursor.execute(sql_stmt, args)
            existing_user = cursor.fetchone()
        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        with db.cursor() as cursor:
            sql_stmt: str = """
                DELETE FROM users WHERE id = %s
            """
            args: Tuple = (user_id,)
            cursor.execute(sql_stmt, args)
            db.commit()
        return {"detail": "User deleted"}
