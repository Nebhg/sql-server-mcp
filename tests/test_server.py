"""
Tests for SQL Server MCP Server
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy import create_engine, text
import pandas as pd

# Import the MCP server class
import sys
sys.path.append('..')
from sql_server_mcp.server import SQLServerMCP


class TestSQLServerMCP:
    """Test cases for SQL Server MCP"""
    
    @pytest.fixture
    def mcp_server(self):
        """Create MCP server instance for testing"""
        return SQLServerMCP()
    
    @pytest.fixture
    def mock_engine(self):
        """Mock SQLAlchemy engine"""
        engine = Mock()
        connection = Mock()
        result = Mock()
        
        # Mock connection context manager
        engine.connect.return_value.__enter__.return_value = connection
        engine.connect.return_value.__exit__.return_value = None
        
        # Mock query execution
        connection.execute.return_value = result
        result.fetchall.return_value = [('test_value',)]
        result.keys.return_value = ['test_column']
        result.returns_rows = True
        result.rowcount = 1
        
        return engine
    
    @pytest.mark.asyncio
    async def test_connect_success(self, mcp_server):
        """Test successful database connection"""
        with patch.dict(os.environ, {
            'SQL_SERVER_HOST': 'localhost',
            'SQL_SERVER_DATABASE': 'test_db',
            'SQL_SERVER_USERNAME': 'test_user',
            'SQL_SERVER_PASSWORD': 'test_pass',
            'SQL_SERVER_PORT': '1433'
        }):
            with patch('sql_server_mcp.server.create_engine') as mock_create_engine:
                mock_engine = Mock()
                mock_create_engine.return_value = mock_engine
                
                # Mock successful connection test
                mock_connection = Mock()
                mock_engine.connect.return_value.__enter__.return_value = mock_connection
                mock_engine.connect.return_value.__exit__.return_value = None
                
                await mcp_server.connect()
                
                assert mcp_server.engine is not None
                mock_create_engine.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_query_select(self, mcp_server, mock_engine):
        """Test executing SELECT query"""
        mcp_server.engine = mock_engine
        
        query = "SELECT * FROM test_table"
        result = await mcp_server.execute_query(query)
        
        assert result["success"] is True
        assert "data" in result
        assert "columns" in result
        assert result["row_count"] == 1
    
    @pytest.mark.asyncio
    async def test_check_connection_success(self, mcp_server, mock_engine):
        """Test successful connection check"""
        mcp_server.engine = mock_engine
        
        # Mock version query result
        mock_result = Mock()
        mock_result.fetchone.return_value = ('Microsoft SQL Server 2019', 'SERVER01', 'TestDB')
        mock_engine.connect.return_value.__enter__.return_value.execute.return_value = mock_result
        
        result = await mcp_server.check_connection()
        
        assert result["connected"] is True
        assert "server_version" in result
        assert "server_name" in result
        assert "database_name" in result


# Run tests
if __name__ == "__main__":
    pytest.main([__file__])
