def userInfoSerializer(user) -> dict:
    return {
        "name": user["name"],
        "email": user["email"],
        "username": user["username"],
        "provider": user["provider"],
        "role": user["role"],
    }
