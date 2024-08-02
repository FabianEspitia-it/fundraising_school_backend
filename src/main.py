import os
import uvicorn

from fastapi import FastAPI, Depends, HTTPException, status

from src.course.router import course
from src.users.router import user
from src.vc_sheet.router import vc_sheet_router
from src.startups.router import startup_router
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


app = FastAPI(dependencies=[Depends(api_key_auth)])

app.title = "Dashboard CTW API"




@app.get("/")
def read_root():
    return {"Hello": "World Rey"}


app.include_router(user)
app.include_router(vc_sheet_router)
app.include_router(startup_router)
app.include_router(course)

if __name__ == "__main__":

    port = os.getenv("PORT")

    print(f"[INFO] Port: {port}")

    if not port:
        print("[INFO] Environment variable not found: Port")

        port = 8080

    uvicorn.run(app, host="0.0.0.0", port=int(port))
