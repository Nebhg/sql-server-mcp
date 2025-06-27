@echo off
echo 🚀 Setting up SQL Server MCP in WSL...
echo =============================================
echo.
echo This script will help you set up the MCP server in WSL.
echo.
echo 📋 Steps this will perform:
echo 1. Copy the project to WSL
echo 2. Install system dependencies
echo 3. Set up Python environment
echo 4. Install ODBC drivers
echo 5. Create convenience scripts
echo.
echo ⚠️  Make sure WSL is installed and running!
echo.
pause

echo 📂 Opening WSL and running setup...
wsl bash -c "cd /mnt/c/Users/benha/Desktop/sql-server-mcp && chmod +x setup_wsl.sh && ./setup_wsl.sh"

echo.
echo 🎉 Setup complete! 
echo.
echo 📝 To continue in WSL:
echo 1. Open WSL terminal
echo 2. cd ~/sql-server-mcp
echo 3. Edit .env file: nano .env
echo 4. Test setup: ./test.sh
echo 5. Run server: ./run.sh
echo.
pause
