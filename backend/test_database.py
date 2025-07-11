import os
from sqlalchemy import create_engine, Table, Column, String, Float, MetaData
from datetime import datetime

def test_database():
    # Get connection string from environment or use a test one
    database_url = os.getenv('DATABASE_URL', 'sqlite:///test.db')
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful!")
            
            # Create test table
            metadata = MetaData()
            test_table = Table(
                'test_table', metadata,
                Column('id', String, primary_key=True),
                Column('message', String),
                Column('timestamp', String)
            )
            metadata.create_all(engine)
            
            # Insert test data
            test_data = {
                'id': f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'message': 'Database connection test successful',
                'timestamp': datetime.now().isoformat()
            }
            
            conn.execute(test_table.insert(), test_data)
            print("✅ Test data inserted successfully!")
            
            # Query test data
            result = conn.execute(test_table.select())
            rows = result.fetchall()
            print(f"✅ Retrieved {len(rows)} rows from test table")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_database() 