from sqlalchemy import create_engine
from models import Base
from database import DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(bind=engine)

# Print confirmation message
print("✅ Tables have been created successfully.")
