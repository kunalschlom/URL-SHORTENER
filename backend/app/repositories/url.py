from typing import Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URL

class URLRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, original_url: str, short_code: str) -> URL:
        db_url = URL(original_url=original_url, short_code=short_code)
        self.db.add(db_url) # remeeber to add it into the db
        await self.db.commit() # coomit the changes to db
        await self.db.refresh(db_url) # synchronise the python and the postgres 
        return db_url # returen the URL object  

    async def get_by_short_code(self, short_code: str) -> URL | None:
        query = select(URL).where(URL.short_code == short_code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() # finds the url object or none

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[URL]:
        query = select(URL).offset(skip).limit(limit)  #skip rows and limit is the number of rows to get 
        result = await self.db.execute(query)
        return result.scalars().all() # reeturns all the objects 

    async def delete(self, short_code: str) -> bool:
        db_url = await self.get_by_short_code(short_code)
        if db_url is None:
            return False
        
        await self.db.delete(db_url)
        await self.db.commit()
        return True

    async def save(self, url: URL) -> URL: # it is to create updates in the orm
        self.db.add(url)
        await self.db.commit()
        await self.db.refresh(url)
        return url

    async def delete_by_id(self, id: UUID) -> bool:
        db_url = await self.db.get(URL, id)
        if db_url is None:
            return False
        
        await self.db.delete(db_url)
        await self.db.commit()
        return True
