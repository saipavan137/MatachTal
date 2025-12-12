"""
Database configuration and connection management
"""
from motor.motor_asyncio import AsyncIOMotorClient
from src.config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Global database client
client: AsyncIOMotorClient = None
database = None


async def connect_db():
    """Connect to MongoDB"""
    global client, database
    
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=20,  # Maximum number of connections in the pool
            minPoolSize=1,  # Minimum number of connections (start with 1, grow as needed)
            maxIdleTimeMS=30000,  # Close idle connections after 30 seconds
            connectTimeoutMS=10000,  # Time to wait for connection
            socketTimeoutMS=30000,  # Time to wait for socket operations
        )
        
        # Test connection
        await client.admin.command('ping')
        
        db_name = settings.MONGODB_DATABASE
        database = client[db_name]
        
        # Create indexes
        await create_indexes()
        
        logger.info(f"Connected to MongoDB: {settings.MONGODB_URI.replace('//', '//***:***@') if '@' in settings.MONGODB_URI else settings.MONGODB_URI}")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_db():
    """Close MongoDB connection"""
    global client
    
    if client:
        client.close()
        logger.info("MongoDB connection closed")


async def create_indexes():
    """Create database indexes for performance"""
    try:
        # Candidate profile indexes
        await database.candidate_profiles.create_index("userId", unique=True)
        await database.candidate_profiles.create_index([("organizationId", 1), ("createdAt", -1)])
        await database.candidate_profiles.create_index("skills")
        await database.candidate_profiles.create_index("location")
        await database.candidate_profiles.create_index("isActive")
        
        # Resume metadata indexes
        await database.resume_metadata.create_index([("profileId", 1), ("isActive", 1)])
        await database.resume_metadata.create_index("s3Key", unique=True)
        await database.resume_metadata.create_index([("uploadedAt", -1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Error creating indexes: {e}")


def get_database():
    """Get database instance.

    In normal app runtime, this is initialised in connect_db() (called from lifespan).
    In some test contexts, connect_db() may not have run yet, so we lazily create
    a client/database here to avoid returning None.
    """
    global client, database

    if database is None:
        # Lazy initialisation – primarily for tests
        try:
            from motor.motor_asyncio import AsyncIOMotorClient  # local import to avoid cycles

            client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=20,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                connectTimeoutMS=10000,
                socketTimeoutMS=30000,
            )
            db_name = (
                settings.MONGODB_TEST_DATABASE
                if settings.ENVIRONMENT.lower() == "test"
                else settings.MONGODB_DATABASE
            )
            database = client[db_name]
            logger.info(f"Lazy MongoDB init for get_database() using DB '{db_name}'")
        except Exception as e:
            logger.error(f"Failed lazy MongoDB init in get_database: {e}")
            # Propagate so callers see a clear failure instead of AttributeError on None
            raise

    return database

