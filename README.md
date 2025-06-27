# SQL Server MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with SQL Server database access capabilities.

## Features

- Execute SQL queries with automatic safety limits
- Database schema inspection and exploration
- Table statistics and performance monitoring
- Advanced search capabilities for tables and columns
- Table backup functionality
- Data insertion with conflict handling
- Query execution plan analysis
- Connection health monitoring

## Quick Start

### 1. Setup Environment

```bash
# Navigate to project directory
cd C:\Users\benha\Desktop\sql-server-mcp

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database Connection

Edit the `.env` file with your SQL Server credentials:

```env
SQL_SERVER_HOST=192.168.1.117
SQL_SERVER_DATABASE=EM_Data
SQL_SERVER_USERNAME=benhg
SQL_SERVER_PASSWORD=your_actual_password
SQL_SERVER_PORT=1433
```

### 3. Test the Server

```bash
python -m sql_server_mcp.server
```

## Integration with AI Tools

### Claude Desktop

Add to your Claude Desktop configuration file:

**Location**: 
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Configuration**:
```json
{
  "mcpServers": {
    "sql-server": {
      "command": "python",
      "args": ["-m", "sql_server_mcp.server"],
      "cwd": "C:\\Users\\benha\\Desktop\\sql-server-mcp",
      "env": {
        "SQL_SERVER_HOST": "192.168.1.117",
        "SQL_SERVER_DATABASE": "EM_Data",
        "SQL_SERVER_USERNAME": "benhg",
        "SQL_SERVER_PASSWORD": "your_password_here",
        "SQL_SERVER_PORT": "1433"
      }
    }
  }
}
```

### VS Code

1. Install the "Model Context Protocol" extension
2. Add to VS Code settings.json:

```json
{
  "mcp.servers": {
    "sql-server": {
      "command": "python",
      "args": ["-m", "sql_server_mcp.server"],
      "cwd": "C:\\Users\\benha\\Desktop\\sql-server-mcp"
    }
  }
}
```

### Cursor

Add to Cursor MCP configuration:

```json
{
  "mcp": {
    "servers": {
      "sql-server": {
        "command": "python",
        "args": ["-m", "sql_server_mcp.server"],
        "cwd": "C:\\Users\\benha\\Desktop\\sql-server-mcp"
      }
    }
  }
}
```

## Available Tools

1. **execute_query** - Run SQL queries with safety limits
2. **get_schema** - Inspect database structure
3. **get_table_info** - Detailed table information with samples
4. **explain_query** - Query execution plans
5. **check_connection** - Database connectivity status
6. **get_table_stats** - Table size and performance metrics
7. **search_tables** - Find tables and columns by name
8. **backup_table** - Create table backups
9. **insert_data** - Insert data with conflict handling

## Usage Examples

Once integrated with Claude, you can ask:

- "Show me the schema of my SeriesRecord table"
- "Execute: SELECT TOP 10 * FROM SeriesRecord WHERE Source = 'NBP'"
- "What tables do I have in my database?"
- "Create a backup of my SeriesRecord table"
- "Search for any tables containing 'GDP'"
- "Show me statistics for all my tables"

## Security Features

- Automatic query limits (TOP 1000 by default)
- Parameterized query support
- Environment-based configuration
- Connection pooling and health checks
- Comprehensive error handling

## Development

### Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/
```

### Project Structure

```
sql-server-mcp/
├── sql_server_mcp/
│   ├── __init__.py
│   └── server.py
├── tests/
│   ├── __init__.py
│   └── test_server.py
├── requirements.txt
├── pyproject.toml
├── .env
└── README.md
```

## Troubleshooting

### Common Issues

1. **ODBC Driver Not Found**: Install Microsoft ODBC Driver 17 for SQL Server
2. **Connection Failed**: Verify server address, credentials, and network connectivity
3. **Permission Denied**: Ensure database user has appropriate permissions

### Testing Connection

```python
# Test ODBC drivers
import pyodbc
print(pyodbc.drivers())

# Test basic connection
from sqlalchemy import create_engine, text
engine = create_engine('mssql+pyodbc://user@server:port/database?driver=ODBC+Driver+17+for+SQL+Server')
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Connection successful!')
```

## License

MIT License - see LICENSE file for details.
