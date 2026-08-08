-- PostgreSQL initialization script for IoT Platform
-- Runs once when the postgres container is first created.

-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ensure the database exists (already created by POSTGRES_DB env var,
-- but this guards against re-runs)
SELECT 'CREATE DATABASE iot_platform'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'iot_platform')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE iot_platform TO iot_user;
