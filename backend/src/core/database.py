"""MongoDB and Beanie database setup."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from beanie import init_beanie

from src.core.config import get_settings
from src.models.audit import AuditLog
from src.models.auth import RefreshToken, Role, User
from src.models.driver import Driver, DriverActivityLog
from src.models.expense import Expense, ExpenseActivityLog
from src.models.fuel import FuelLog, FuelLogActivityLog
from src.models.maintenance import Maintenance, MaintenanceLog
from src.models.notification import Notification
from src.models.trip import Trip, TripActivityLog as TripAuditLog
from src.models.vehicle import Vehicle, VehicleActivityLog
from src.repositories.auth import RoleRepository

mongo_client: AsyncIOMotorClient | None = None
mongo_database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> AsyncIOMotorDatabase | None:
    """Initialize the MongoDB connection and Beanie ODM."""

    global mongo_client, mongo_database

    settings = get_settings()

    if not settings.mongo_enabled:
        return None

    mongo_client = AsyncIOMotorClient(settings.mongo_uri, uuidRepresentation="standard")
    mongo_database = mongo_client[settings.mongo_db]
    await init_beanie(
        database=mongo_database,
        document_models=[Role, User, RefreshToken, Vehicle, VehicleActivityLog, Driver, DriverActivityLog, Trip, TripAuditLog, Maintenance, MaintenanceLog, FuelLog, FuelLogActivityLog, Expense, ExpenseActivityLog, AuditLog, Notification],
    )
    await RoleRepository().ensure_default_roles()
    return mongo_database


async def close_mongo_connection() -> None:
    """Close the MongoDB connection if it was opened."""

    global mongo_client, mongo_database

    if mongo_client is not None:
        mongo_client.close()
        mongo_client = None
        mongo_database = None


def get_database() -> AsyncIOMotorDatabase:
    """Return the active MongoDB database handle."""

    if mongo_database is None:
        raise RuntimeError("MongoDB connection has not been initialized")

    return mongo_database
