from app.config import settings
from neo4j import GraphDatabase

driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
driver.verify_connectivity()
print("Neo4j connected!")
driver.close()
