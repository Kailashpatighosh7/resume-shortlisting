import asyncio
from sqlalchemy import text
from app.database.session import engine

async def test():
    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public'
                ORDER BY table_name;
            """)
        )

        for row in result:
            print(row[0])

asyncio.run(test())