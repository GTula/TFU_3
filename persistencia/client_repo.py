from models.client import Client
from sqlalchemy.orm import Session

def get_all_clients(db: Session):
    return db.query(Client).all()

def get_client(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()

def add_client(db: Session, client: Client):
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

def update_client(db: Session, client_id: int, data: dict):
    client = get_client(db, client_id)
    if client:
        for key, value in data.items():
            setattr(client, key, value)
        db.commit()
        db.refresh(client)
    return client

def delete_client(db: Session, client_id: int):
    client = get_client(db, client_id)
    if client:
        db.delete(client)
        db.commit()
    return client