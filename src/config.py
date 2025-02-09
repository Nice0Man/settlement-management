DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/settlement_management"
)
CRITICAL_THRESHOLD = 50
ENERGY_LIMIT = 500

DB_CONFIG = {
    "user": "postgres",
    "password": "postgres",
    "database": "settlement_management",
    "host": "localhost",
    "port": 5432,
}

TABLES = [
    "resource_operations",
    "resource_plans",
    "incidents",
    "events",
    "notifications",
    "tasks",
    "personnel",
    "sensors_devices",
    "energy_systems",
    "infrastructure",
    "resources",
    "geozones",
    "routes",
    "logistic_routes",
    "transport_vehicles",
    "settlements",
]
