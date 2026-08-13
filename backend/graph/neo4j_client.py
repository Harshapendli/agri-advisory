from neo4j import AsyncGraphDatabase
from typing import List, Dict, Any, Optional
from config import settings

class Neo4jClient:
    _instance = None
    _driver = None

    @classmethod
    async def get_instance(cls) -> "Neo4jClient":
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance.connect()
        return cls._instance

    async def connect(self):
        try:
            self._driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            await self._driver.verify_connectivity()
            print("Neo4j connected successfully")
        except Exception as e:
            print(f"Neo4j connection failed: {e}")
            self._driver = None

    async def close(self):
        if self._driver:
            await self._driver.close()

    async def run_query(self, cypher: str, params: Dict = None) -> List[Dict[str, Any]]:
        if not self._driver:
            return []
        try:
            async with self._driver.session() as session:
                result = await session.run(cypher, params or {})
                records = await result.data()
                return records
        except Exception as e:
            print(f"Neo4j query error: {e}")
            return []

neo4j_client = Neo4jClient()
