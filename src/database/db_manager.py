import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.inspection import inspect
from .models import Base


class DatabaseManager:
    def __init__(self, database_url, data_source):
        self.database_url = database_url
        self.data_source = data_source
        self.engine = self._init_db()
        self.Session = sessionmaker(bind=self.engine)

    def _init_db(self):
        """Initialize or update the database schema."""
        db_path = self.database_url.split('://')[1]

        if not os.path.exists(db_path):
            engine = create_engine(self.database_url)
            Base.metadata.create_all(engine)
            print(f"New {self.data_source} database created: {db_path}")
        else:
            engine = create_engine(self.database_url)
            self._update_schema(engine)
            print(f"Existing {self.data_source} database updated: {db_path}")

        return engine

    def _update_schema(self, engine):
        """Update existing database schema if needed."""
        inspector = inspect(engine)
        with engine.connect() as connection:
            if 'daily_summaries' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('daily_summaries')]
                if 'data_source' not in columns:
                    connection.execute(
                        "ALTER TABLE daily_summaries ADD COLUMN data_source STRING"
                    )

    def get_session(self):
        """Get a new database session."""
        return self.Session()
