from fastapi import APIRouter, HTTPException, status, Depends
from app.models import LoginRequest, LoginResponse
from app.dependencies import authenticate_user, create_access_token, verify_token

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Admin login endpoint
    """
    if not authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(data={"sub": request.username})

    return LoginResponse(access_token=access_token)


@router.get("/verify")
async def verify(payload: dict = Depends(verify_token)):
    """
    Verify JWT token
    """
    return {"valid": True, "username": payload.get("sub")}
