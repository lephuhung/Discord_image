from sqlalchemy.orm import Session

import model, schemas

# User management
def get_user(db: Session, user_id: int):
    return db.query(model.User).filter(model.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.User).offset(skip).limit(limit).all()

def get_user_by_password(db: Session, password: str):
    return db.query(model.User).filter(model.User.hashed_password == password).first()


# Agent management
def create_agents(db: Session, agents: schemas.agents):
    db_agent = model.agents(name=agents.name, token=agents.token, zalo_name=agents.zalo_name, zalo_number_target=agents.zalo_number_target, webhook_id=agents.webhook_id)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def get_agents_by_id(db: Session, agent_id: int):
    return db.query(model.agents).filter(model.agents.id == agent_id).first()

def get_agents_by_token(db: Session, token:str):
    return db.query(model.agents).filter(model.agents.token == token).first()

def get_agents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.agents).offset(skip).limit(limit).all()
# Webhooks management

def create_webhooks(db: Session, webhooks: model.webhooks):
    webhooks = db.webhooks(url_webhooks=webhooks.url_webhook, webhooks_name= webhooks.webhook_name, created_at= webhooks.created_at, ended_at= webhooks.ended_at )
    db.add(webhooks)
    db.commit()
    db.refresh()
    return webhooks

def create_user(db: Session, user: schemas.user):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = model.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(model.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = model.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
