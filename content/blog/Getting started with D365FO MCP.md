---
title: "Getting Started with D365FO MCP Server"
date: "2025-01-06"
excerpt: "A comprehensive guide to setting up and using the D365 Finance & Operations Model Context Protocol (MCP) server for AI-powered business insights and automation."
tags: ["d365", "mcp", "ai", "finance", "operations", "claude"]
---

# Getting Started with D365FO MCP Server

The D365 Finance & Operations MCP (Model Context Protocol) Server is a production-ready bridge between AI assistants like Claude and your Microsoft Dynamics 365 Finance & Operations environment. This guide will walk you through everything you need to know to get started.

## What is the D365FO MCP Server?

The D365FO MCP Server provides AI assistants with intelligent access to your D365FO data through a clean, standardized interface. Instead of manually writing complex OData queries or navigating through multiple D365 screens, you can simply ask questions in natural language and get immediate, accurate responses.

### Key Features

🔍 **Smart Entity Discovery** - Find the right D365 entities and fields using natural language search  
🔗 **Entity Relationships** - Automatically understand how D365 entities connect to each other  
📋 **Advanced Enum Support** - Get proper enum values with correct OData syntax  
⚡ **Robust Operations** - Reliable CRUD operations with automatic error handling  
🧠 **Learning System** - Remembers successful patterns and improves over time  
🔐 **Enterprise Security** - Production-grade OAuth authentication with automatic token refresh  

## Prerequisites

Before you begin, you'll need:

1. **D365 Finance & Operations Environment** (Sandbox or Production)
2. **Azure AD Application Registration** with appropriate permissions
3. **Python 3.10+** installed on your system
4. **Claude Desktop** (optional, for direct AI integration)

## Installation

### 1. Clone and Set Up the Environment

```bash
# Clone the repository
git clone https://github.com/your-username/d365fo-mcp
cd d365fo-mcp

# Create and activate virtual environment (using uv - recommended)
uv venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv sync
```

### 2. Configure Azure AD Application

You need to create an Azure AD application to authenticate with D365FO:

1. **Go to Azure Portal** → Azure Active Directory → App registrations
2. **Click "New registration"**
3. **Set the name**: "D365FO MCP Server"
4. **Leave other defaults** and click "Register"
5. **Note the Application (client) ID and Directory (tenant) ID**
6. **Go to "Certificates & secrets"** → Create a new client secret
7. **Copy the secret value** (you won't be able to see it again)

### 3. Configure D365FO Permissions

In your D365FO environment, you need to grant permissions:

1. **System Administration** → Security → Users
2. **Find your service principal** (same name as your Azure AD app)
3. **Assign appropriate security roles** (typically "System user" + business-specific roles)

### 4. Create Configuration File

Copy the example configuration and fill in your details:

```bash
cp .env.example .env
```

Edit the `.env` file:

```bash
# D365 Authentication (Required)
AZURE_CLIENT_ID=your-client-id-from-azure
AZURE_CLIENT_SECRET=your-client-secret-from-azure
AZURE_TENANT_ID=your-tenant-id-from-azure

# D365 Instance Configuration (Required)  
D365_BASE_URL=https://your-env.sandbox.operations.dynamics.com

# Optional Configuration
DATAAREAID=usmf                    # Your default company/legal entity
DATABASE_PATH=./data/d365fo-mcp.db # Local cache location
METADATA_CACHE_HOURS=24            # How long to cache metadata
LOG_LEVEL=info                     # Logging verbosity
```

## First Run and Validation

### 1. Validate Your Configuration

Before running the server, validate your setup:

```bash
python -m d365fo_mcp.main --validate-config
```

This will:
- Test your Azure AD authentication
- Verify D365FO connectivity
- Check that all required permissions are in place
- Validate your configuration settings

### 2. Initialize the Database

Set up the local SQLite database for metadata caching:

```bash
python -m d365fo_mcp.main --init-db
```

### 3. Run Manual Metadata Sync (Optional)

For faster first-time setup, manually sync D365 metadata:

```bash
python scripts/manual_sync.py
```

This downloads and processes your D365FO metadata (~40-50MB) and stores it locally for fast searches. The process typically takes 15-30 seconds.

## Running the Server

### Standalone Mode

For testing and development:

```bash
python -m d365fo_mcp.main
```

The server runs in STDIO mode and waits for MCP protocol messages.

### Claude Desktop Integration

For seamless AI integration, add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/mcp.json`  
**Windows**: `%APPDATA%\Claude\mcp.json`

```json
{
  "mcpServers": {
    "D365FO MCP Server": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "d365fo_mcp.main"],
      "cwd": "/absolute/path/to/d365fo-mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/d365fo-mcp",
        "AZURE_CLIENT_ID": "your-client-id",
        "AZURE_CLIENT_SECRET": "your-client-secret",
        "AZURE_TENANT_ID": "your-tenant-id",
        "D365_BASE_URL": "https://your-env.sandbox.operations.dynamics.com",
        "DATAAREAID": "usmf",
        "DATABASE_PATH": "/absolute/path/to/d365fo-mcp/data/d365fo-mcp.db"
      }
    }
  }
}
```

⚠️ **Important**: Use absolute paths for all file paths in Claude Desktop configuration.

## Basic Usage Examples

Once configured, you can interact with your D365FO system using natural language. Here are some examples:

### Entity Discovery

```
"Find customer entities in D365"
```
The server will search through 4,000+ entities and return relevant matches with descriptions.

### Data Queries

```
"Show me all customers in the RETAIL group"
```
The server will:
1. Find the appropriate entity (CustomersV3)
2. Construct the proper OData query
3. Return formatted results

### Financial Data Analysis

```
"Get trial balance data for account 50111 in July 2025"
```
The server will identify the correct financial entity and return detailed balance information.

### Entity Relationships

```
"What fields are available in the Customer entity and how does it relate to other entities?"
```
Get comprehensive field definitions and relationship mappings.

## Advanced Features

### Learning System

The server remembers successful query patterns:

```python
# Successful queries are automatically saved
# The server learns from your usage patterns
# Future similar requests become faster and more accurate
```

### Company Context

Handle multi-company scenarios:

```python
# Queries can target specific companies
# Automatic company filtering when needed
# Cross-company reporting capabilities
```

### Error Recovery

Robust error handling:

- **Token expiration**: Automatic refresh and retry
- **Connection issues**: Intelligent retry with backoff
- **Invalid queries**: Helpful error messages with suggestions

## Monitoring and Maintenance

### Log Files

Monitor server activity:

```bash
# Server logs show all interactions
tail -f logs/d365fo-mcp.log

# Set LOG_LEVEL=debug for detailed diagnostics
```

### Metadata Refresh

The server automatically refreshes metadata every 24 hours (configurable). For manual refresh:

```bash
python scripts/manual_sync.py
```

### Performance Optimization

The server includes several performance optimizations:

- **Local SQLite cache** for fast entity searches
- **Connection pooling** for D365FO requests  
- **Background metadata sync** to avoid blocking requests
- **Query result caching** for frequently accessed data

## Troubleshooting

### Common Issues

**Authentication Error (401)**
- Verify Azure AD credentials in `.env`
- Check that the service principal exists in D365FO
- Ensure proper security roles are assigned

**Connection Timeout**
- Verify D365_BASE_URL is correct and accessible
- Check firewall/proxy settings
- Ensure D365FO environment is running

**No Metadata Found**
- Run manual metadata sync: `python scripts/manual_sync.py`
- Check database file permissions
- Verify DATAAREAID setting

**Claude Desktop Not Working**
- Use absolute paths in configuration
- Check file permissions on database and script locations
- Restart Claude Desktop after configuration changes

### Getting Help

1. **Check the logs** - Enable debug logging for detailed information
2. **Validate configuration** - Use `--validate-config` flag
3. **Test manually** - Run `scripts/manual_sync.py` to verify connectivity
4. **Review documentation** - See `APPROACH.md` for architectural details

## Next Steps

Now that your D365FO MCP Server is running, you can:

1. **Explore your data** - Ask questions about your D365FO entities and relationships
2. **Build reports** - Create complex financial and operational reports through natural language
3. **Automate workflows** - Use the learning system to build reusable query patterns
4. **Extend functionality** - Customize the server for your specific business needs

The D365FO MCP Server transforms how you interact with your ERP data, making complex queries as simple as asking a question. Start exploring and discover the power of AI-driven business intelligence!

## Architecture Overview

The server uses a modern, enterprise-ready architecture:

- **Dependency Injection** - Clean, testable, extensible design
- **Repository Pattern** - Pluggable storage backends (SQLite, future cloud options)
- **Service Layer** - Business logic separated from data access
- **Factory Pattern** - Configuration-driven component creation
- **Background Processing** - Non-blocking metadata synchronization

For detailed technical information, see the [APPROACH.md](https://github.com/your-username/d365fo-mcp/blob/main/APPROACH.md) documentation.

---

*Ready to supercharge your D365FO experience with AI? Get started today and transform how you work with your enterprise data!*