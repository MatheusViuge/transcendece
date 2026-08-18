import os

# Test modules import application configuration during collection. Provide safe,
# disposable defaults without depending on a developer's local `.env`.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-jwt-secret-that-is-long-enough-123456")
