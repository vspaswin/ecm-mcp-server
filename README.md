# ECM MCP Server

Enterprise Content Management (ECM) Model Context Protocol (MCP) server for seamless integration with ECM REST APIs.

## Overview

This MCP server provides a standardized interface for AI assistants to interact with Enterprise Content Management systems through their REST APIs. It abstracts the complexity of ECM APIs and exposes them as MCP tools that can be used by AI models like Claude, GPT-4, and others.

## Features

- **Document Management**: Create, read, update, and delete documents
- **Metadata Operations**: Manage document metadata and properties
- **Search & Discovery**: Advanced search capabilities across ECM repositories
- **Version Control**: Document versioning and history tracking
- **Folder Operations**: Hierarchical folder structure management
- **Workflow Management**: Trigger and monitor ECM workflows
- **Security**: OAuth 2.0, API key authentication, and role-based access control
- **Audit Logging**: Comprehensive audit trail of all operations

## Architecture

```
┌─────────────────┐
│  AI Client      │
│ (Claude, etc.)  │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│  MCP Server     │
│  (Python)       │
│                 │
│  ┌───────────┐  │
│  │ Tools     │  │
│  │ Resources │  │
│  │ Prompts   │  │
│  └───────────┘  │
└────────┬────────┘
         │ REST API
         │
┌────────▼────────┐
│  ECM System     │
│  (Your ECM)     │
└─────────────────┘
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Access to your ECM system's REST API
- ECM API credentials (API key, OAuth token, etc.)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/vspaswin/ecm-mcp-server.git
cd ecm-mcp-server
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your ECM connection:
```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your ECM details
```

## Configuration

Create a `config/config.yaml` file:

```yaml
ecm:
  base_url: "https://your-ecm-instance.com/api/v1"
  auth_type: "oauth2"  # Options: oauth2, api_key, basic
  
  # For OAuth2
  oauth:
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    token_url: "https://your-ecm-instance.com/oauth/token"
    scopes: ["read", "write"]
  
  # For API Key
  api_key:
    header_name: "X-API-Key"
    key: "your_api_key"
  
  # Request settings
  timeout: 30
  retry_attempts: 3
  rate_limit: 100  # requests per minute

server:
  name: "ecm-mcp-server"
  version: "1.0.0"
  log_level: "INFO"
  
features:
  enable_caching: true
  cache_ttl: 300  # seconds
  enable_audit_log: true
```

## Usage

### Running the Server

```bash
python src/main.py
```

The server will start in stdio mode by default, ready to receive MCP protocol messages.

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python src/main.py
```

### Integration with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ecm": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/ecm-mcp-server/src/main.py"],
      "env": {
        "ECM_CONFIG_PATH": "/path/to/config/config.yaml"
      }
    }
  }
}
```

## Available Tools

### Document Operations

- `ecm_create_document`: Create a new document in ECM
- `ecm_get_document`: Retrieve document by ID
- `ecm_update_document`: Update document content or metadata
- `ecm_delete_document`: Delete a document
- `ecm_download_document`: Download document content
- `ecm_upload_document`: Upload file content to document

### Search & Discovery

- `ecm_search_documents`: Search documents by query
- `ecm_advanced_search`: Advanced search with multiple filters
- `ecm_get_recent_documents`: Get recently modified documents

### Folder Management

- `ecm_create_folder`: Create new folder
- `ecm_list_folder_contents`: List folder contents
- `ecm_move_document`: Move document to different folder
- `ecm_get_folder_tree`: Get hierarchical folder structure

### Metadata Operations

- `ecm_get_metadata`: Get document metadata
- `ecm_update_metadata`: Update metadata fields
- `ecm_get_metadata_schema`: Get available metadata fields

### Version Control

- `ecm_get_versions`: List document versions
- `ecm_create_version`: Create new document version
- `ecm_restore_version`: Restore previous version

### Workflow Management

- `ecm_start_workflow`: Initiate workflow on document
- `ecm_get_workflow_status`: Check workflow status
- `ecm_approve_workflow`: Approve workflow step

## Resources

The server exposes ECM data as resources:

- `ecm://documents/{id}`: Individual document
- `ecm://folders/{id}`: Folder contents
- `ecm://search`: Search results
- `ecm://metadata-schemas`: Available metadata schemas

## Development

### Project Structure

```
ecm-mcp-server/
├── src/
│   ├── main.py              # Entry point
│   ├── server.py            # MCP server implementation
│   ├── tools/               # Tool implementations
│   │   ├── __init__.py
│   │   ├── documents.py
│   │   ├── search.py
│   │   ├── folders.py
│   │   ├── metadata.py
│   │   ├── versions.py
│   │   └── workflows.py
│   ├── resources/           # Resource handlers
│   │   ├── __init__.py
│   │   └── ecm_resources.py
│   ├── client/              # ECM API client
│   │   ├── __init__.py
│   │   ├── ecm_client.py
│   │   ├── auth.py
│   │   └── exceptions.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── config.py
│       ├── cache.py
│       └── logger.py
├── config/
│   ├── config.example.yaml
│   └── logging.yaml
├── tests/
│   ├── test_tools.py
│   ├── test_client.py
│   └── test_integration.py
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── CONFIGURATION.md
├── requirements.txt
├── setup.py
└── README.md
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Linting
ruff check src/

# Type checking
mypy src/

# Formatting
black src/
```

## API Mapping

This server can be adapted to various ECM systems. Here's how common ECM APIs map to MCP tools:

### Common ECM Systems

- **SharePoint**: Uses Microsoft Graph API
- **Documentum**: OpenText REST API
- **Alfresco**: Alfresco REST API
- **FileNet**: IBM FileNet REST API
- **OpenText Content Suite**: OpenText REST API

### Example Mappings

| MCP Tool | SharePoint Endpoint | Alfresco Endpoint |
|----------|---------------------|-------------------|
| create_document | POST /sites/{site}/lists/{list}/items | POST /nodes/{parent}/children |
| get_document | GET /sites/{site}/lists/{list}/items/{id} | GET /nodes/{id} |
| search_documents | POST /sites/{site}/lists/{list}/search | POST /search |
| update_metadata | PATCH /sites/{site}/lists/{list}/items/{id} | PUT /nodes/{id} |

## Security Best Practices

1. **Never commit credentials**: Use environment variables or secure vaults
2. **Enable audit logging**: Track all operations for compliance
3. **Implement rate limiting**: Prevent API abuse
4. **Use HTTPS**: Always encrypt API communications
5. **Token rotation**: Regularly rotate OAuth tokens
6. **Least privilege**: Grant minimum required permissions

## Troubleshooting

### Common Issues

**Connection Errors**
```bash
# Check ECM connectivity
curl -v https://your-ecm-instance.com/api/v1/health
```

**Authentication Failures**
- Verify credentials in config.yaml
- Check token expiration
- Validate API permissions

**Tool Errors**
- Check logs in `logs/ecm-mcp-server.log`
- Enable debug logging: `log_level: DEBUG`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [https://github.com/vspaswin/ecm-mcp-server/issues](https://github.com/vspaswin/ecm-mcp-server/issues)
- Documentation: [docs/](docs/)

## Roadmap

- [ ] Support for additional ECM systems
- [ ] GraphQL API support
- [ ] Webhook notifications
- [ ] Bulk operations
- [ ] Advanced caching strategies
- [ ] Multi-tenant support
- [ ] OpenAPI spec auto-generation
- [ ] Performance monitoring dashboard

## Acknowledgments

- Model Context Protocol by Anthropic
- FastMCP framework
- ECM API documentation and communities
