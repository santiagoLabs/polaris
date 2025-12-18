import asyncpg                                                                                                    
from asyncpg import Pool                                                                                          
                                                                                                                    
from app.config import settings 

class Database:
    def __init__(self):
        self.pool: Pool | None = None
        self._search_path = f"SET search_path TO {settings.db_schema}, extensions"                                


    async def connect(self):
        self.pool = await asyncpg.create_pool(
            dsn = settings.database_url, 
            min_size = 2,
            max_size = 10,
            statement_cache_size=0,
        )
        print(f"Conneted to database, schema {settings.db_schema}")
    
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            print("Database connection closed")
    
    async def fetch(self, query: str, *args):                                                                     
        #Returns all rows
        async with self.pool.acquire() as conn:
            async with conn.transaction(): 
                await conn.execute(self._search_path)                                                                  
                return await conn.fetch(query, *args)                                                                 
                                                                                                                    
    async def fetchrow(self, query: str, *args):                                                                  
        async with self.pool.acquire() as conn:
            async with conn.transaction(): 
                await conn.execute(self._search_path)                                                                   
                return await conn.fetchrow(query, *args)                                                              
                                                                                                                    
    async def execute(self, query: str, *args):                                                                   
        async with self.pool.acquire() as conn:
            async with conn.transaction(): 
                await conn.execute(self._search_path)     
                return await conn.execute(query, *args)  

db = Database()