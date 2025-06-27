# Dockerfile
FROM python:3.11-slim

# Install system dependencies for SQL Server
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY sql_server_mcp/ ./sql_server_mcp/
COPY pyproject.toml .

# Install the package
RUN pip install -e .

# Set environment variables (override these with actual values)
ENV SQL_SERVER_HOST=localhost
ENV SQL_SERVER_DATABASE=EM_Data
ENV SQL_SERVER_USERNAME=sa
ENV SQL_SERVER_PASSWORD=
ENV SQL_SERVER_PORT=1433
ENV LOG_LEVEL=INFO

# Run the MCP server
CMD ["python", "-m", "sql_server_mcp.server"]
