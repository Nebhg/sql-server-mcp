#!/bin/bash
# WSL Setup Script for SQL Server MCP
# Run this script in WSL to set up the MCP server

echo "🚀 Setting up SQL Server MCP in WSL..."
echo "=================================================="

# Create project directory in WSL home
PROJECT_DIR="$HOME/sql-server-mcp"
echo "📁 Creating project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  Directory already exists. Backing up..."
    mv "$PROJECT_DIR" "$PROJECT_DIR.backup.$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Copy files from Windows to WSL
WINDOWS_PROJECT="/mnt/c/Users/benha/Desktop/sql-server-mcp"

if [ -d "$WINDOWS_PROJECT" ]; then
    echo "📋 Copying files from Windows to WSL..."
    cp -r "$WINDOWS_PROJECT"/* .
    
    # Fix line endings for scripts
    echo "🔧 Fixing line endings..."
    find . -type f -name "*.py" -exec dos2unix {} \; 2>/dev/null || true
    find . -type f -name "*.sh" -exec dos2unix {} \; 2>/dev/null || true
    find . -type f -name "*.txt" -exec dos2unix {} \; 2>/dev/null || true
    
    echo "✅ Files copied successfully!"
else
    echo "❌ Windows project directory not found at $WINDOWS_PROJECT"
    echo "Please check the path and try again."
    exit 1
fi

# Install system dependencies for SQL Server
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y curl apt-transport-https gnupg lsb-release

# Add Microsoft repository
echo "🔑 Adding Microsoft repository..."
curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/$(lsb_release -rs)/prod $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/mssql-release.list

# Install ODBC driver
echo "🗄️  Installing ODBC Driver 17 for SQL Server..."
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

# Install Python dependencies
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create WSL-specific environment file
echo "⚙️  Creating WSL environment configuration..."
cat > .env.wsl << EOF
# SQL Server Connection Configuration for WSL
SQL_SERVER_HOST=192.168.1.117
SQL_SERVER_DATABASE=EM_Data
SQL_SERVER_USERNAME=benhg
SQL_SERVER_PASSWORD=your_password_here
SQL_SERVER_PORT=1433

# Optional: Logging level
LOG_LEVEL=INFO
EOF

# Backup original .env and use WSL version
cp .env .env.windows.backup
cp .env.wsl .env

echo "📝 Creating WSL-specific configuration files..."

# Create WSL Claude Desktop config
WSL_PROJECT_PATH=$(pwd)
cat > claude_desktop_config_wsl.json << EOF
{
  "mcpServers": {
    "sql-server": {
      "command": "python",
      "args": ["-m", "sql_server_mcp.server"],
      "cwd": "$WSL_PROJECT_PATH",
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
EOF

# Create convenience scripts
echo "🔧 Creating convenience scripts..."

# Create activation script
cat > activate.sh << 'EOF'
#!/bin/bash
# Activate the MCP environment
source venv/bin/activate
echo "🚀 SQL Server MCP environment activated!"
echo "Current directory: $(pwd)"
echo "Python: $(which python)"
echo ""
echo "Available commands:"
echo "  python test_setup.py           - Test the setup"
echo "  python -m sql_server_mcp.server - Run the MCP server"
echo "  pytest tests/                  - Run tests"
EOF

# Create test script
cat > test.sh << 'EOF'
#!/bin/bash
# Test the MCP server setup
source venv/bin/activate
python test_setup.py
EOF

# Create run script
cat > run.sh << 'EOF'
#!/bin/bash
# Run the MCP server
source venv/bin/activate
echo "🚀 Starting SQL Server MCP Server..."
python -m sql_server_mcp.server
EOF

# Make scripts executable
chmod +x activate.sh test.sh run.sh

echo ""
echo "🎉 WSL Setup Complete!"
echo "=================================================="
echo "📍 Project location: $PROJECT_DIR"
echo ""
echo "📝 Next Steps:"
echo "1. Edit .env file and add your SQL Server password:"
echo "   nano .env"
echo ""
echo "2. Test the setup:"
echo "   ./test.sh"
echo ""
echo "3. Run the MCP server:"
echo "   ./run.sh"
echo ""
echo "4. For Claude Desktop integration, use the config from:"
echo "   claude_desktop_config_wsl.json"
echo ""
echo "5. To activate the environment manually:"
echo "   source ./activate.sh"
echo ""
echo "🔧 Important Notes:"
echo "- Make sure SQL Server is accessible from WSL"
echo "- You may need to configure Windows Firewall"
echo "- ODBC Driver 17 has been installed for SQL Server connectivity"
echo ""
