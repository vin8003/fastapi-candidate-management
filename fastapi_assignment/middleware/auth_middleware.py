from jose import JWTError
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi_assignment.config import SECURE_PATH_PATTERNS
from fastapi_assignment.utils.jwt_utils import decode_access_token


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check if the request path matches any regex pattern in SECURE_PATH_PATTERNS
        if any(pattern.match(request.url.path) for pattern in SECURE_PATH_PATTERNS):
            authorization: str = request.headers.get("Authorization")
            if not authorization:
                return JSONResponse(
                    status_code=403, content={"detail": "Authorization header missing"}
                )

            try:
                # Extract and validate the Bearer token
                scheme, token = authorization.split()
                if scheme.lower() != "bearer":
                    raise HTTPException(
                        status_code=403, detail="Invalid authentication scheme"
                    )

                # Decode the JWT token using the utility function
                payload = decode_access_token(token)
                if payload is None:
                    return JSONResponse(
                        status_code=403, content={"detail": "Invalid token"}
                    )

                email = payload.get("email")
                if not email:
                    raise HTTPException(
                        status_code=403, detail="Token does not contain an email"
                    )

                # Store email in request.state
                request.state.email = email
            except (JWTError, ValueError):
                return JSONResponse(
                    status_code=403, content={"detail": "Invalid token"}
                )

        # Proceed to the next middleware or request handler
        response = await call_next(request)
        return response
