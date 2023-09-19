from fastapi import APIRouter, Depends
from bson import ObjectId

import oauth2
from serializers.userSerializers import userInfoSerializer
from database import Users

router = APIRouter()


@router.get(
    "/me",
    description="gets profile from cookie",
)
def get_me(user_id: str = Depends(oauth2.require_user)):
    user = userInfoSerializer(Users.find_one({"_id": ObjectId(user_id)}))
    return {"status": "success", "user": user}
