# Database Configuration
# Update this with your Neon connection string

# Option 1: Neon PostgreSQL (recommended for production)
NEON_DATABASE_URL = "postgresql://your_username:your_password@your_host:port/your_database"

# Option 2: SQLite (for local testing)
SQLITE_DATABASE_URL = "sqlite:///football_predictions.db"

# Current database URL (change this to switch between databases)
DATABASE_URL = NEON_DATABASE_URL  # Change to SQLITE_DATABASE_URL for local testing 