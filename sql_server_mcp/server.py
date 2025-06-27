#!/usr/bin/env python3
"""
SQL Server MCP Server
A Model Context Protocol server for SQL Server database operations.
Provides tools for querying, schema inspection, and data manipulation.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence, Union
from datetime import datetime, date
import decimal

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

import pyodbc
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sql-server-mcp")

class SQLServerMCP:
    """SQL Server MCP Server implementation"""
    
    def __init__(self):
        self.server = Server("sql-server-mcp")
        self.engine = None
        self.setup_tools()
        
    def setup_tools(self):
        """Register all available tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available SQL Server tools"""
            return [
                types.Tool(
                    name="execute_query",
                    description="Execute a SQL query against the SQL Server database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute"
                            },
                            "params": {
                                "type": "object",
                                "description": "Parameters for parameterized queries",
                                "default": {}
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of rows to return",
                                "default": 1000
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_schema",
                    description="Get database schema information including tables, columns, and relationships",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Specific table name (optional - if not provided, returns all tables)"
                            },
                            "include_columns": {
                                "type": "boolean",
                                "description": "Include column details",
                                "default": True
                            },
                            "include_indexes": {
                                "type": "boolean",
                                "description": "Include index information",
                                "default": False
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_table_info",
                    description="Get detailed information about a specific table including schema, indexes, and sample data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to inspect"
                            },
                            "sample_rows": {
                                "type": "integer",
                                "description": "Number of sample rows to return",
                                "default": 5
                            }
                        },
                        "required": ["table_name"]
                    }
                ),
                types.Tool(
                    name="explain_query",
                    description="Get the execution plan for a SQL query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to explain"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="check_connection",
                    description="Test database connection and return connection status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_table_stats",
                    description="Get statistics about table size, row count, and disk usage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Table name (optional - if not provided, returns stats for all tables)"
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="search_tables",
                    description="Search for tables and columns by name or pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_term": {
                                "type": "string",
                                "description": "Search term or pattern"
                            },
                            "search_type": {
                                "type": "string",
                                "description": "Search type: 'table' or 'column' or 'both'",
                                "enum": ["table", "column", "both"],
                                "default": "both"
                            }
                        },
                        "required": ["search_term"]
                    }
                ),
                types.Tool(
                    name="backup_table",
                    description="Create a backup copy of a table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Source table name"
                            },
                            "backup_name": {
                                "type": "string",
                                "description": "Backup table name (optional - auto-generated if not provided)"
                            }
                        },
                        "required": ["table_name"]
                    }
                ),
                types.Tool(
                    name="insert_data",
                    description="Insert data into a table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Target table name"
                            },
                            "data": {
                                "type": "array",
                                "description": "Array of objects representing rows to insert",
                                "items": {
                                    "type": "object"
                                }
                            },
                            "on_conflict": {
                                "type": "string",
                                "description": "How to handle conflicts: 'ignore' or 'replace'",
                                "enum": ["ignore", "replace"],
                                "default": "ignore"
                            }
                        },
                        "required": ["table_name", "data"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent]:
            """Handle tool execution"""
            
            if not arguments:
                arguments = {}
                
            try:
                if name == "execute_query":
                    result = await self.execute_query(
                        arguments["query"],
                        arguments.get("params", {}),
                        arguments.get("limit", 1000)
                    )
                elif name == "get_schema":
                    result = await self.get_schema(
                        arguments.get("table_name"),
                        arguments.get("include_columns", True),
                        arguments.get("include_indexes", False)
                    )
                elif name == "get_table_info":
                    result = await self.get_table_info(
                        arguments["table_name"],
                        arguments.get("sample_rows", 5)
                    )
                elif name == "explain_query":
                    result = await self.explain_query(arguments["query"])
                elif name == "check_connection":
                    result = await self.check_connection()
                elif name == "get_table_stats":
                    result = await self.get_table_stats(arguments.get("table_name"))
                elif name == "search_tables":
                    result = await self.search_tables(
                        arguments["search_term"],
                        arguments.get("search_type", "both")
                    )
                elif name == "backup_table":
                    result = await self.backup_table(
                        arguments["table_name"],
                        arguments.get("backup_name")
                    )
                elif name == "insert_data":
                    result = await self.insert_data(
                        arguments["table_name"],
                        arguments["data"],
                        arguments.get("on_conflict", "ignore")
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
                return [types.TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def connect(self):
        """Initialize database connection"""
        try:
            # Get connection details from environment variables
            server = os.getenv("SQL_SERVER_HOST", "192.168.1.117")
            database = os.getenv("SQL_SERVER_DATABASE", "EM_Data")
            username = os.getenv("SQL_SERVER_USERNAME", "benhg")
            password = os.getenv("SQL_SERVER_PASSWORD", "")
            port = os.getenv("SQL_SERVER_PORT", "1433")
            
            # Create connection string
            connection_string = (
                f"mssql+pyodbc://{username}@{server}:{port}/{database}"
                "?driver=ODBC+Driver+17+for+SQL+Server"
            )
            
            self.engine = create_engine(
                connection_string,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            logger.info("Successfully connected to SQL Server")
            
        except Exception as e:
            logger.error(f"Failed to connect to SQL Server: {str(e)}")
            raise

    def json_serializer(self, obj):
        """JSON serializer for complex objects"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif hasattr(obj, '__str__'):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    async def execute_query(self, query: str, params: dict = None, limit: int = 1000) -> dict:
        """Execute a SQL query and return results"""
        if not self.engine:
            await self.connect()
            
        try:
            with self.engine.connect() as conn:
                # Add LIMIT equivalent for SQL Server if not present
                if limit and "TOP" not in query.upper() and "OFFSET" not in query.upper():
                    if query.strip().upper().startswith("SELECT"):
                        query = query.replace("SELECT", f"SELECT TOP {limit}", 1)
                
                result = conn.execute(text(query), params or {})
                
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = list(result.keys())
                    
                    # Convert to list of dictionaries
                    data = []
                    for row in rows:
                        data.append(dict(zip(columns, row)))
                    
                    return {
                        "success": True,
                        "row_count": len(data),
                        "columns": columns,
                        "data": data,
                        "query": query
                    }
                else:
                    return {
                        "success": True,
                        "message": f"Query executed successfully. Rows affected: {result.rowcount}",
                        "query": query
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    async def get_schema(self, table_name: str = None, include_columns: bool = True, include_indexes: bool = False) -> dict:
        """Get database schema information"""
        if not self.engine:
            await self.connect()
            
        try:
            inspector = inspect(self.engine)
            
            if table_name:
                # Get specific table info
                if table_name not in inspector.get_table_names():
                    return {"error": f"Table '{table_name}' not found"}
                
                table_info = {
                    "table_name": table_name,
                    "columns": [],
                    "primary_keys": inspector.get_pk_constraint(table_name)["constrained_columns"],
                    "foreign_keys": [
                        {
                            "columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"]
                        }
                        for fk in inspector.get_foreign_keys(table_name)
                    ]
                }
                
                if include_columns:
                    for column in inspector.get_columns(table_name):
                        table_info["columns"].append({
                            "name": column["name"],
                            "type": str(column["type"]),
                            "nullable": column["nullable"],
                            "default": column["default"]
                        })
                
                if include_indexes:
                    table_info["indexes"] = [
                        {
                            "name": idx["name"],
                            "columns": idx["column_names"],
                            "unique": idx["unique"]
                        }
                        for idx in inspector.get_indexes(table_name)
                    ]
                
                return table_info
            else:
                # Get all tables
                tables = []
                for table in inspector.get_table_names():
                    table_info = {"table_name": table}
                    
                    if include_columns:
                        table_info["columns"] = [
                            {
                                "name": col["name"],
                                "type": str(col["type"]),
                                "nullable": col["nullable"]
                            }
                            for col in inspector.get_columns(table)
                        ]
                    
                    tables.append(table_info)
                
                return {
                    "database": self.engine.url.database,
                    "table_count": len(tables),
                    "tables": tables
                }
                
        except Exception as e:
            return {"error": str(e)}

    async def get_table_info(self, table_name: str, sample_rows: int = 5) -> dict:
        """Get detailed table information with sample data"""
        if not self.engine:
            await self.connect()
            
        try:
            # Get schema info
            schema_info = await self.get_schema(table_name, include_columns=True, include_indexes=True)
            
            if "error" in schema_info:
                return schema_info
            
            # Get row count
            with self.engine.connect() as conn:
                count_result = conn.execute(text(f"SELECT COUNT(*) as count FROM [{table_name}]"))
                row_count = count_result.fetchone()[0]
                
                # Get sample data
                sample_result = conn.execute(text(f"SELECT TOP {sample_rows} * FROM [{table_name}]"))
                sample_data = []
                columns = list(sample_result.keys())
                
                for row in sample_result.fetchall():
                    sample_data.append(dict(zip(columns, row)))
            
            return {
                **schema_info,
                "row_count": row_count,
                "sample_data": sample_data
            }
            
        except Exception as e:
            return {"error": str(e)}

    async def explain_query(self, query: str) -> dict:
        """Get execution plan for a query"""
        if not self.engine:
            await self.connect()
            
        try:
            with self.engine.connect() as conn:
                # Get execution plan
                conn.execute(text("SET SHOWPLAN_ALL ON"))
                plan_result = conn.execute(text(query))
                plan_data = plan_result.fetchall()
                
                conn.execute(text("SET SHOWPLAN_ALL OFF"))
                
                return {
                    "query": query,
                    "execution_plan": [dict(row._mapping) for row in plan_data]
                }
                
        except Exception as e:
            return {"error": str(e)}

    async def check_connection(self) -> dict:
        """Test database connection"""
        try:
            if not self.engine:
                await self.connect()
            
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT @@VERSION as version, @@SERVERNAME as server_name, DB_NAME() as database_name"))
                info = result.fetchone()
                
                return {
                    "connected": True,
                    "server_version": info[0],
                    "server_name": info[1],
                    "database_name": info[2]
                }
                
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }

    async def get_table_stats(self, table_name: str = None) -> dict:
        """Get table statistics"""
        if not self.engine:
            await self.connect()
            
        try:
            with self.engine.connect() as conn:
                if table_name:
                    query = """
                    SELECT 
                        t.name as table_name,
                        p.rows as row_count,
                        CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS total_space_mb,
                        CAST(ROUND(((SUM(a.used_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS used_space_mb,
                        CAST(ROUND(((SUM(a.total_pages) - SUM(a.used_pages)) * 8) / 1024.00, 2) AS NUMERIC(36, 2)) AS unused_space_mb
                    FROM sys.tables t
                    INNER JOIN sys.indexes i ON t.object_id = i.object_id
                    INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
                    INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
                    WHERE t.name = :table_name
                    GROUP BY t.name, p.rows
                    """
                    result = conn.execute(text(query), {"table_name": table_name})
                else:
                    query = """
                    SELECT 
                        t.name as table_name,
                        p.rows as row_count,
                        CAST(ROUND(((SUM(a.total_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS total_space_mb,
                        CAST(ROUND(((SUM(a.used_pages) * 8) / 1024.00), 2) AS NUMERIC(36, 2)) AS used_space_mb,
                        CAST(ROUND(((SUM(a.total_pages) - SUM(a.used_pages)) * 8) / 1024.00, 2) AS NUMERIC(36, 2)) AS unused_space_mb
                    FROM sys.tables t
                    INNER JOIN sys.indexes i ON t.object_id = i.object_id
                    INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
                    INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
                    GROUP BY t.name, p.rows
                    ORDER BY total_space_mb DESC
                    """
                    result = conn.execute(text(query))
                
                stats = []
                columns = list(result.keys())
                for row in result.fetchall():
                    stats.append(dict(zip(columns, row)))
                
                return {
                    "success": True,
                    "statistics": stats
                }
                
        except Exception as e:
            return {"error": str(e)}

    async def search_tables(self, search_term: str, search_type: str = "both") -> dict:
        """Search tables and columns by name"""
        if not self.engine:
            await self.connect()
            
        try:
            results = {"tables": [], "columns": []}
            
            with self.engine.connect() as conn:
                if search_type in ["table", "both"]:
                    # Search table names
                    table_query = """
                    SELECT table_name, table_schema
                    FROM information_schema.tables
                    WHERE table_name LIKE :search_term
                    """
                    table_result = conn.execute(text(table_query), {"search_term": f"%{search_term}%"})
                    
                    for row in table_result.fetchall():
                        results["tables"].append({
                            "table_name": row[0],
                            "schema": row[1]
                        })
                
                if search_type in ["column", "both"]:
                    # Search column names
                    column_query = """
                    SELECT table_name, column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE column_name LIKE :search_term
                    ORDER BY table_name, column_name
                    """
                    column_result = conn.execute(text(column_query), {"search_term": f"%{search_term}%"})
                    
                    for row in column_result.fetchall():
                        results["columns"].append({
                            "table_name": row[0],
                            "column_name": row[1],
                            "data_type": row[2],
                            "is_nullable": row[3]
                        })
            
            return {
                "success": True,
                "search_term": search_term,
                "results": results
            }
            
        except Exception as e:
            return {"error": str(e)}

    async def backup_table(self, table_name: str, backup_name: str = None) -> dict:
        """Create a backup copy of a table"""
        if not self.engine:
            await self.connect()
            
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{table_name}_backup_{timestamp}"
            
            with self.engine.connect() as conn:
                # Create backup table
                query = f"SELECT * INTO [{backup_name}] FROM [{table_name}]"
                conn.execute(text(query))
                conn.commit()
                
                # Get row count
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM [{backup_name}]"))
                row_count = count_result.fetchone()[0]
            
            return {
                "success": True,
                "original_table": table_name,
                "backup_table": backup_name,
                "rows_copied": row_count
            }
            
        except Exception as e:
            return {"error": str(e)}

    async def insert_data(self, table_name: str, data: list, on_conflict: str = "ignore") -> dict:
        """Insert data into a table"""
        if not self.engine:
            await self.connect()
            
        try:
            if not data:
                return {"error": "No data provided"}
            
            # Convert data to DataFrame for easier handling
            df = pd.DataFrame(data)
            
            # Determine conflict handling
            if_exists = "append" if on_conflict == "ignore" else "replace"
            
            # Insert data
            rows_affected = df.to_sql(
                table_name,
                self.engine,
                if_exists=if_exists,
                index=False,
                method='multi'
            )
            
            return {
                "success": True,
                "table_name": table_name,
                "rows_inserted": len(data),
                "conflict_handling": on_conflict
            }
            
        except Exception as e:
            return {"error": str(e)}

async def main():
    """Main entry point"""
    # Initialize MCP server
    mcp_server = SQLServerMCP()
    
    # Connect to database
    await mcp_server.connect()
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await mcp_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sql-server-mcp",
                server_version="1.0.0",
                capabilities=mcp_server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
