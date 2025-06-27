#!/usr/bin/env python3
"""
Test script for SQL Server MCP Server
Run this to verify your setup works correctly
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from sql_server_mcp.server import SQLServerMCP

async def test_connection():
    """Test the MCP server connection"""
    print("🔧 Testing SQL Server MCP Connection...")
    print("-" * 50)
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Create MCP server instance
        mcp_server = SQLServerMCP()
        
        # Test connection
        print("1. Testing database connection...")
        result = await mcp_server.check_connection()
        
        if result.get("connected"):
            print("✅ Database connection successful!")
            print(f"   Server: {result.get('server_name')}")
            print(f"   Database: {result.get('database_name')}")
            print(f"   Version: {result.get('server_version', '')[:50]}...")
        else:
            print("❌ Database connection failed!")
            print(f"   Error: {result.get('error')}")
            return False
        
        # Test schema retrieval
        print("\n2. Testing schema retrieval...")
        schema_result = await mcp_server.get_schema()
        
        if "error" not in schema_result:
            table_count = schema_result.get("table_count", 0)
            print(f"✅ Schema retrieved successfully!")
            print(f"   Found {table_count} tables")
            
            # Show first few table names
            tables = schema_result.get("tables", [])
            if tables:
                print("   Sample tables:")
                for table in tables[:5]:
                    print(f"     - {table.get('table_name')}")
                if len(tables) > 5:
                    print(f"     ... and {len(tables) - 5} more")
        else:
            print("❌ Schema retrieval failed!")
            print(f"   Error: {schema_result.get('error')}")
        
        # Test simple query
        print("\n3. Testing query execution...")
        query_result = await mcp_server.execute_query("SELECT @@VERSION as version")
        
        if query_result.get("success"):
            print("✅ Query execution successful!")
            print(f"   Returned {query_result.get('row_count')} rows")
        else:
            print("❌ Query execution failed!")
            print(f"   Error: {query_result.get('error')}")
        
        print("\n" + "=" * 50)
        print("🎉 MCP Server test completed successfully!")
        print("Your SQL Server MCP is ready to use with Claude!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        print("\nCommon issues:")
        print("1. Make sure SQL Server is running and accessible")
        print("2. Verify your credentials in the .env file")
        print("3. Check if ODBC Driver 17 is installed")
        print("4. Ensure network connectivity to the SQL Server")
        return False

async def test_tools():
    """Test available MCP tools"""
    print("\n🔧 Testing MCP Tools...")
    print("-" * 30)
    
    try:
        mcp_server = SQLServerMCP()
        
        # Test tools list (this doesn't require DB connection)
        tools = await mcp_server.server._handler.list_tools()
        
        print(f"✅ Found {len(tools)} available tools:")
        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool.name} - {tool.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tools test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 SQL Server MCP Test Suite")
    print("=" * 50)
    
    # Test tools first (no DB required)
    asyncio.run(test_tools())
    
    # Test database connection
    success = asyncio.run(test_connection())
    
    if success:
        print("\n📝 Next Steps:")
        print("1. Update your password in the .env file if you haven't already")
        print("2. Configure Claude Desktop using claude_desktop_config.json")
        print("3. Start using the MCP server with: python -m sql_server_mcp.server")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file configuration")
        print("2. Verify SQL Server is running and accessible")
        print("3. Test connection with SQL Server Management Studio first")
