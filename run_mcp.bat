@echo off
cd /d "C:\path\to\your\sql-server-mcp"
call venv\Scripts\activate.bat
set SQL_SERVER_HOST=192.168.1.117
set SQL_SERVER_DATABASE=EM_Data
set SQL_SERVER_USERNAME=benhg
set SQL_SERVER_PASSWORD=
set SQL_SERVER_PORT=1433
python -m sql_server_mcp.server 