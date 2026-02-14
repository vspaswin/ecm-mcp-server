# ECM MCP Server

A Model Context Protocol (MCP) server for interacting with Enterprise Content Management (ECM) REST APIs. This server enables AI assistants and other MCP clients to seamlessly manage documents, folders, metadata, versions, workflows, and perform advanced search operations within enterprise content management systems.

## Features

### Document Management
- Upload documents with metadata
- Download documents by ID
- Get document information
- Delete documents
- Update document metadata

### Search Capabilities
- Full-text search across documents
- Advanced search with filters (date range, document type, tags)
- Metadata-based search
- Folder-scoped search

### Folder Management
- Create hierarchical folder structures
- List folder contents (documents and subfolders)
- Move documents between folders
- Get folder tree structure
- Delete folders (with recursive option)

### Metadata Management
- Get document metadata
- Update metadata fields
- View metadata schemas by document type

### Version Control
- View version history
- Create new versions (major/minor)
- Restore previous versions
- Version comments and tracking

### Workflow Management
- Start workflows on documents
- Get workflow status
- Approve workflow steps
- Reject workflow steps with reasons

## Architecture

```
ecm-mcp-server/
├── src/
│   ├── server.py              # Main MCP server entry point
│   ├── client/
│   │   └── ecm_client.py      # HTTP client for ECM API
│   ├── config/
│   │   └── settings.py        # Configuration management
│   └── tools/
│       ├── documents.py       # Document operations
│       ├── search.py          # Search operations
│       ├── folders.py         # Folder management
│       ├── metadata.py        # Metadata operations
│       ├── versions.py        # Version control
│       └── workflows.py       # Workflow management
├── tests/                     # Test suite
├── examples/                  # Usage examples
├── .env.example              # Environment variables template
└── requirements.txt          # Python dependencies
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Access to an ECM system with REST API
- API credentials (username/password or API key)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/vspaswin/ecm-mcp-server.git
   cd ecm-mcp-server
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your ECM API credentials
   ```

5. **Configure .env file**
   ```env
   ECM_API_URL=https://your-ecm-system.com/api/v1
   ECM_USERNAME=your_username
   ECM_PASSWORD=your_password
   # Or use API key authentication:
   # ECM_API_KEY=your_api_key
   ```

## Usage

### Running the Server

```bash
python src/server.py
```

The server runs on stdio transport and can be integrated with any MCP-compatible client.

### Integration with Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ecm": {
      "command": "python",
      "args": ["/path/to/ecm-mcp-server/src/server.py"],
      "env": {
        "ECM_API_URL": "https://your-ecm-system.com/api/v1",
        "ECM_USERNAME": "your_username",
        "ECM_PASSWORD": "your_password"
      }
    }
  }
}
```

### Available Tools

#### Health & Info
- `ecm_health_check` - Check API connectivity and status
- `ecm_get_api_info` - Get API version and capabilities

#### Documents
- `ecm_upload_document` - Upload a new document
- `ecm_get_document` - Get document information
- `ecm_download_document` - Download document content
- `ecm_delete_document` - Delete a document

#### Search
- `ecm_search_documents` - Full-text search
- `ecm_advanced_search` - Search with filters

#### Folders
- `ecm_create_folder` - Create new folder
- `ecm_list_folder_contents` - List folder contents
- `ecm_move_document` - Move document to folder
- `ecm_get_folder_tree` - Get folder hierarchy
- `ecm_delete_folder` - Delete folder

#### Metadata
- `ecm_get_metadata` - Get document metadata
- `ecm_update_metadata` - Update metadata fields
- `ecm_get_metadata_schema` - Get metadata schema

#### Versions
- `ecm_get_versions` - Get version history
- `ecm_create_version` - Create new version
- `ecm_restore_version` - Restore previous version

#### Workflows
- `ecm_start_workflow` - Start workflow on document
- `ecm_get_workflow_status` - Get workflow status
- `ecm_approve_workflow` - Approve workflow step
- `ecm_reject_workflow` - Reject workflow step

## Example Usage

Once connected to an MCP client like Claude:

```
User: Upload a contract document
Assistant: *uses ecm_upload_document tool*

User: Search for all invoices from 2024
Assistant: *uses ecm_advanced_search with date filters*

User: Create a folder structure for Q1 2024 reports
Assistant: *uses ecm_create_folder tool*

User: Start approval workflow on document ID 12345
Assistant: *uses ecm_start_workflow tool*
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|----------|
| `ECM_API_URL` | Base URL of ECM API | Yes | - |
| `ECM_USERNAME` | API username | Yes* | - |
| `ECM_PASSWORD` | API password | Yes* | - |
| `ECM_API_KEY` | API key (alternative auth) | Yes* | - |
| `REQUEST_TIMEOUT` | Request timeout in seconds | No | 30 |
| `MAX_RETRIES` | Max retry attempts | No | 3 |
| `LOG_LEVEL` | Logging level | No | INFO |

*Either username/password OR API key is required

### Customization

The server is designed to be adaptable to different ECM systems:

1. **API Endpoints**: Modify endpoint paths in tool files to match your ECM API
2. **Authentication**: Update `ecm_client.py` for different auth methods
3. **Response Parsing**: Adjust response handling in tool implementations
4. **Custom Tools**: Add new tools in `src/tools/` directory

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

- **client/ecm_client.py**: Handles HTTP communication, authentication, error handling
- **tools/**: Each file contains related tool implementations
- **config/settings.py**: Centralized configuration management
- **server.py**: Main server initialization and tool registration

### Adding New Tools

1. Create new file in `src/tools/` (e.g., `permissions.py`)
2. Implement tools using `@mcp.tool()` decorator
3. Register tools in `src/server.py`

```python
def register_permission_tools(mcp: FastMCP, client: ECMClient):
    @mcp.tool()
    async def ecm_set_permissions(document_id: str, permissions: dict):
        # Implementation
        pass
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify credentials in `.env` file
   - Check API URL is correct
   - Ensure network connectivity to ECM system

2. **Tool Not Found**
   - Verify tool is registered in `server.py`
   - Check tool decorator syntax
   - Restart MCP server

3. **Timeout Errors**
   - Increase `REQUEST_TIMEOUT` in configuration
   - Check network latency to ECM system
   - Verify ECM API performance

## Security Considerations

- **Credentials**: Store in environment variables, never commit to version control
- **API Keys**: Use API key authentication when available
- **HTTPS**: Always use HTTPS for ECM API connections
- **Validation**: Implement input validation for all parameters
- **Logging**: Avoid logging sensitive data (passwords, tokens)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/vspaswin/ecm-mcp-server/issues
- Documentation: See `/examples` directory for detailed usage examples

## Roadmap

- [ ] Support for additional authentication methods (OAuth, SAML)
- [ ] Bulk operations (batch upload/download)
- [ ] Advanced permission management
- [ ] Document templates
- [ ] Audit log retrieval
- [ ] Integration with additional ECM systems
- [ ] Performance optimizations and caching
- [ ] Web UI for server management

## Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [httpx](https://www.python-httpx.org/) - Modern HTTP client
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings management
