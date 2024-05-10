from sqlalchemy import select, delete, update, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./shortcut_report.db"
# engine = create_async_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
SQLALCHEMY_DATABASE_URL = "sqlite:///./shortcut_report.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine,
                            class_=Session, expire_on_commit=False)

Base = declarative_base()


async def update_saved(db: Session, db_class: Base,
                       new_items: list[Base],
                       remove_missing=True):
    old_items = db.execute(select(db_class))
    old_items = old_items.scalars()
    old_items = {
        item.id: item
        for item in old_items
    }
    new_items = {
        item.id: item
        for item in new_items
    }

    remove_items = set(old_items.keys()) - set(new_items.keys())
    add_items = set(new_items.keys()) - set(old_items.keys())
    update_items = set(new_items.keys()).intersection(old_items.keys())
    if add_items:
        db.add_all([l for _id, l in new_items.items() if _id in add_items])
    if remove_missing and remove_items:
        delete_query = delete(db_class).where(db_class.id.in_(remove_items))
        db.execute(delete_query)
    for uid in update_items:
        db.merge(new_items[uid])
    db.commit()
    return list(db.scalars(select(db_class)))
