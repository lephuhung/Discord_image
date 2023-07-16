from fastapi import FastAPI, Request, Header, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware 
import logging
import datetime
from pathlib import Path
from Utils import CheckIP
import curd, model, schemas
from database import SessionLocal, engine
from sqlalchemy.orm import Session
'''
database setup
'''
model.Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
app = FastAPI()
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
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
async def read_root(request: Request, user_agent: str = Header(None, convert_underscores=True)):
    timestamp = request.state.timestamp
    port = request.state.port
    CheckIP('172.225.56.17', url=config["webhook_error"],useragent=user_agent, timestamp=timestamp, port=port, url_thumbnail=config['image'], botname='Cảnh báo server ROOT')
    return {"Hello": "World FastAPI"}
'''
View image without logger database
'''
# View image without logger
@app.get("/view/{filename}")
async def read_item(filename: str, q: str = None):
    image_path = f"/image/{filename}"
    path = Path(image_path)
    if not path.is_file():
        return FileResponse('taylor.gif', media_type="image/gif")
    return FileResponse(image_path, media_type="image/gif")
'''
View Image with logger database
'''
@app.get("/image/{filename}")
async def get_image(request: Request, filename: str,token: str = None, user_agent: str = Header(None, convert_underscores=True)):
    ip = request.state.ip
    timestamp = request.state.timestamp
    port = request.state.port
    image_path = f"/image/{filename}"
    path = Path(image_path)
    if not path.is_file() or token==None:
        CheckIP('172.225.56.17', url=config["webhook_error"],useragent=user_agent, token=token, timestamp=timestamp, port=port, filename=filename, url_thumbnail=config['image'], botname='Cảnh báo server configuration')
        return FileResponse('taylor.gif', media_type="image/gif")
    CheckIP('172.225.56.17', url=config["webhook"],useragent=user_agent, token=token, timestamp=timestamp, port=port, filename=filename)
    return FileResponse(image_path, media_type="image/gif")
'''
Agents managent 
'''
# view agent configuration
@app.get("/agents")
async def agents(db: Session = Depends(get_db)):
    agents= curd.get_agents(db ,skip=0, limit=10)
    return agents
#search agents by id
@app.get("/agents/{agent_id}")
async def agents(agent_id: int  ,db: Session = Depends(get_db)):
    agents= curd.get_agents_by_id(db ,agent_id= agent_id)
    return agents
# search agents by token
@app.get("/agents_token")
async def agents(token: str, db: Session = Depends(get_db)):
    agents= curd.get_agents_by_token(db, token=token)
    return agents
# add agents
@app.post("/agents/add", response_model=schemas.agents)
async def agents(agents: schemas.agents, db: Session = Depends(get_db)):
    agents_model= curd.create_agents(db, agents=agents)
    return agents_model #add Content-Type:application/json

