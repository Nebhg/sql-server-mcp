#!/bin/bash
cd /home/ben/sql-server-mcp
source venv/bin/activate
export SQL_SERVER_HOST="192.168.1.117"
export SQL_SERVER_DATABASE="EM_Data"
export SQL_SERVER_USERNAME="benhg"
export SQL_SERVER_PASSWORD=""
export SQL_SERVER_PORT="1433"
python -m sql_server_mcp.server