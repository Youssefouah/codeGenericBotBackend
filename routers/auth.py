from fastapi import APIRouter, HTTPException, status, Response, Depends, Body
from datetime import datetime, timedelta
from random import randbytes
import hashlib
from typing import Annotated
from pydantic import EmailStr

from schemas.userSchemas import SocialSignupSchema, UserSignupSchema, UserSigninSchema
from database import Users
import utils
from emails.verifyEmail import VerifyEmail
from emails.forgotEmail import ForgotEmail
from oauth2 import AuthJWT, require_user
from config import settings

router = APIRouter()


@router.post("/social")
async def social_signup(
    social_data: SocialSignupSchema, response: Response, Authorize: AuthJWT = Depends()
):
    if social_data.provider == "google":
        db_user = Users.find_one({"email": social_data.email})
    if social_data.provider == "github":
        db_user = Users.find_one(
            {"provider": "github", "username": social_data.username}
        )
    if not db_user:
        user_info = social_data.dict()
        user_info["role"] = "user"
        user_info["verified"] = True
        user_info["created_at"] = datetime.utcnow()
        user_info["updated_at"] = user_info["created_at"]
        result = Users.insert_one(user_info)
        db_user = Users.find_one({"_id": result.inserted_id})

    # Create access token
    access_token = Authorize.create_access_token(
        subject=str(db_user["_id"]),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )

    # Create refresh token
    refresh_token = Authorize.create_refresh_token(
        subject=str(db_user["_id"]),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRES_IN * 60,
        expires=ACCESS_TOKEN_EXPIRES_IN * 60,
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="none",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRES_IN * 60,
        expires=REFRESH_TOKEN_EXPIRES_IN * 60,
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="none",
    )
    response.set_cookie(
        key="logged_in",
        value="True",
        max_age=ACCESS_TOKEN_EXPIRES_IN * 60,
        expires=ACCESS_TOKEN_EXPIRES_IN * 60,
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="none",
    )

    # Send both access
    return {
        "access_token": access_token,
        "role": db_user["role"],
    }


@router.post("/signup")
async def signup_user(payload: UserSignupSchema):
    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Password doesn't match"
        )
    existing = Users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    user_info = payload.dict()
    del user_info["passwordConfirm"]
    user_info["role"] = "user"
    user_info["verified"] = False
    user_info["provider"] = "normal"
    user_info["username"] = None
    user_info["created_at"] = datetime.utcnow()
    user_info["updated_at"] = user_info["created_at"]
    user_info["password"] = utils.hash_password(payload.password)
    result = Users.insert_one(user_info)
    new_user = Users.find_one({"_id": result.inserted_id})
    try:
        token = randbytes(10)
        hashedCode = hashlib.sha256()
        hashedCode.update(token)
        verification_code = hashedCode.hexdigest()
        Users.find_one_and_update(
            {"_id": result.inserted_id},
            {
                "$set": {
                    "verification_code": verification_code,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        print(token.hex())
        await VerifyEmail(
            new_user["name"], token.hex(), [payload.email]
        ).sendVerificationCode()
    except Exception as error:
        print(error)
        Users.find_one_and_update(
            {"_id": result.inserted_id},
            {"$set": {"verification_code": None, "updated_at": datetime.utcnow()}},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error sending email",
        )
    return {
        "status": "success",
        "message": "Verification token successfully sent to your email",
    }


ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


@router.post("/signin")
async def user_signin(
    payload: UserSigninSchema, response: Response, Authorize: AuthJWT = Depends()
):
    # Check if the user exist
    db_user = Users.find_one({"email": payload.email})
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email",
        )

    # Check if the password is valid
    if not utils.verify_password(payload.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Password",
        )

    # Create access token
    access_token = Authorize.create_access_token(
        subject=str(db_user["_id"]),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
    )

    # Create refresh token
    refresh_token = Authorize.create_refresh_token(
        subject=str(db_user["_id"]),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
    )

    # Store refresh and access tokens in cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRES_IN * 60,
        expires=ACCESS_TOKEN_EXPIRES_IN * 60,
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="none",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRES_IN * 60,
        expires=REFRESH_TOKEN_EXPIRES_IN * 60,
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="none",
    )
    response.set_cookie(
        key="logged_in",
        value="True",
        max_age=ACCESS_TOKEN_EXPIRES_IN * 60,
        expires=ACCESS_TOKEN_EXPIRES_IN * 60,
        path="/",
        domain=None,
        secure=True,
        httponly=True,
        samesite="none",
    )

    # Send both access
    return {
        "access_token": access_token,
        "role": db_user["role"],
        "verified": db_user["verified"],
    }


@router.patch("/verify")
async def verify_email(code: Annotated[str, Body(..., embed=True)]):
    hashedCode = hashlib.sha256()
    hashedCode.update(bytes.fromhex(code))
    verification_code = hashedCode.hexdigest()
    result = Users.find_one_and_update(
        {"verification_code": verification_code},
        {
            "$set": {
                "verification_code": None,
                "verified": True,
                "updated_at": datetime.utcnow(),
            }
        },
        new=True,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid verification code",
        )
    return {"status": "success", "message": "Verified Successfully"}


@router.patch("/forgot")
async def reset_password(email: str = Body(..., embed=True)):
    user = Users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No account with this email."
        )

    generated_password = randbytes(10).hex()
    Users.find_one_and_update(
        {"email": email},
        {
            "$set": {
                "password": utils.hash_password(generated_password),
                "updated_at": datetime.utcnow(),
            }
        },
    )

    try:
        await ForgotEmail(
            user["name"], generated_password, [EmailStr(email)]
        ).sendResetPassword()
    except Exception as error:
        print(error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error sending email",
        )
    return {"status": "success"}
