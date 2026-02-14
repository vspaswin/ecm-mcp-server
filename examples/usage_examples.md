# ECM MCP Server Usage Examples

This document provides practical examples of using the ECM MCP Server with an AI assistant.

## Document Management

### Uploading Documents

```
User: Upload the contract.pdf file to the Legal folder

Assistant will:
1. Use ecm_search_documents to find the Legal folder
2. Use ecm_upload_document with:
   - file_path: "contract.pdf"
   - title: "contract.pdf"
   - folder_id: <legal_folder_id>
   - metadata: {"documentType": "contract"}
```

### Finding Documents

```
User: Find all invoices from January 2024

Assistant will use ecm_advanced_search:
- query: "invoice"
- date_from: "2024-01-01"
- date_to: "2024-01-31"
- document_type: "invoice"
```

### Document Information

```
User: What are the details of document ID 12345?

Assistant will use ecm_get_document:
- document_id: "12345"

Returns: title, size, created date, author, metadata, version info
```

## Folder Organization

### Creating Folder Structure

```
User: Create a folder structure for Q1 2024 reports

Assistant will:
1. ecm_create_folder(name="Q1 2024", parent_folder_id=None)
2. ecm_create_folder(name="January", parent_folder_id=<q1_folder_id>)
3. ecm_create_folder(name="February", parent_folder_id=<q1_folder_id>)
4. ecm_create_folder(name="March", parent_folder_id=<q1_folder_id>)
```

### Moving Documents

```
User: Move document 12345 to the Archive folder

Assistant will:
1. ecm_search_documents(query="Archive", search_type="folder")
2. ecm_move_document(document_id="12345", target_folder_id=<archive_id>)
```

### Browsing Folders

```
User: Show me what's in the Contracts folder

Assistant will:
1. Find folder: ecm_search_documents(query="Contracts", search_type="folder")
2. List contents: ecm_list_folder_contents(folder_id=<contracts_id>)

Returns: List of documents and subfolders
```

## Metadata Management

### Viewing Metadata

```
User: What metadata does document 12345 have?

Assistant will use ecm_get_metadata:
- document_id: "12345"

Returns: All metadata fields and values
```

### Updating Metadata

```
User: Set the department to "Finance" and status to "Approved" for document 12345

Assistant will use ecm_update_metadata:
- document_id: "12345"
- metadata: {
    "department": "Finance",
    "status": "Approved"
  }
```

### Understanding Metadata Schema

```
User: What metadata fields are available for invoice documents?

Assistant will use ecm_get_metadata_schema:
- document_type: "invoice"

Returns: Available fields, types, required fields, validation rules
```

## Version Control

### Viewing Version History

```
User: Show me the version history of document 12345

Assistant will use ecm_get_versions:
- document_id: "12345"

Returns: List of versions with dates, authors, comments, version numbers
```

### Creating New Version

```
User: Create a new major version of document 12345 with comment "Updated for Q1"

Assistant will use ecm_create_version:
- document_id: "12345"
- comment: "Updated for Q1"
- major: true
```

### Restoring Previous Version

```
User: Restore document 12345 to version 2.0

Assistant will:
1. ecm_get_versions(document_id="12345") to find version ID
2. ecm_restore_version(document_id="12345", version_id=<v2.0_id>)
```

## Workflow Management

### Starting a Workflow

```
User: Start an approval workflow on document 12345

Assistant will use ecm_start_workflow:
- document_id: "12345"
- workflow_name: "approval"
- parameters: {
    "approvers": ["manager@company.com"],
    "priority": "high"
  }
```

### Checking Workflow Status

```
User: What's the status of workflow WF-789?

Assistant will use ecm_get_workflow_status:
- workflow_id: "WF-789"

Returns: Current step, status, history, pending actions
```

### Approving Workflow

```
User: Approve workflow WF-789 with comment "Looks good"

Assistant will use ecm_approve_workflow:
- workflow_id: "WF-789"
- comment: "Looks good"
```

### Rejecting Workflow

```
User: Reject workflow WF-789 because the document needs revisions

Assistant will use ecm_reject_workflow:
- workflow_id: "WF-789"
- reason: "Document needs revisions"
```

## Advanced Search Examples

### Complex Search Query

```
User: Find PDF documents in the Legal folder created in 2024 with tag "contract"

Assistant will use ecm_advanced_search:
- query: ""
- folder_id: <legal_folder_id>
- document_type: "pdf"
- date_from: "2024-01-01"
- tags: ["contract"]
```

### Full-Text Search

```
User: Search for documents containing "quarterly revenue report"

Assistant will use ecm_search_documents:
- query: "quarterly revenue report"
- max_results: 20
```

## Batch Operations

### Bulk Document Upload

```
User: Upload all PDF files from the reports folder

Assistant will:
1. List local files
2. For each file:
   - ecm_upload_document with appropriate metadata
3. Report results
```

### Organizing Multiple Documents

```
User: Move all documents tagged "2023" to the Archive folder

Assistant will:
1. ecm_advanced_search(tags=["2023"])
2. Find Archive folder
3. For each document:
   - ecm_move_document to Archive folder
```

## Health Checks and Monitoring

### System Health

```
User: Check if the ECM system is working

Assistant will use ecm_health_check:

Returns:
- API connectivity status
- Authentication status
- API response time
```

### API Information

```
User: What version of the ECM API are we using?

Assistant will use ecm_get_api_info:

Returns:
- API version
- Available endpoints
- Supported features
```

## Common Workflows

### Document Review Process

```
1. User uploads document
2. Set metadata (author, department, type)
3. Move to Review folder
4. Start approval workflow
5. Workflow routes to approvers
6. Upon approval, move to Published folder
7. Update status metadata to "Published"
```

### Version Management

```
1. User requests document update
2. Create new version with comment
3. Update content
4. Update metadata if needed
5. Notify stakeholders
6. If issues found, restore previous version
```

### Audit Trail

```
1. Get document information
2. Get version history
3. Get metadata history
4. Get workflow history
5. Compile audit report
```

## Error Handling Examples

### Document Not Found

```
User: Get information for document 99999

Assistant will:
- Attempt ecm_get_document(document_id="99999")
- Receive error: "Document not found"
- Inform user: "I couldn't find document 99999. Would you like to search for it?"
```

### Invalid Folder

```
User: Upload file to folder XYZ123

Assistant will:
- Verify folder exists
- If not found, suggest: "Folder XYZ123 doesn't exist. Would you like me to:
  1. Create it
  2. List available folders
  3. Search for similar folder names"
```

## Performance Tips

1. **Use Advanced Search**: When filtering, use `ecm_advanced_search` instead of `ecm_search_documents` + filtering

2. **Limit Results**: Specify `max_results` to avoid large data transfers

3. **Folder Tree Depth**: Use appropriate `max_depth` when getting folder trees

4. **Batch Operations**: Group related operations to minimize API calls

## Integration Patterns

### With Email
```
User: Save this email attachment to ECM

1. Extract attachment from email
2. Upload to ECM with metadata from email
3. Tag with sender, subject, date
4. File in appropriate folder based on rules
```

### With Calendar
```
User: Archive all meeting notes from last quarter

1. Query calendar for Q1 meetings
2. Search ECM for related documents
3. Update metadata with meeting details
4. Move to quarterly archive folder
```

### With Project Management
```
User: Link this project document to JIRA ticket

1. Upload document to ECM
2. Store JIRA ticket ID in metadata
3. Add link in JIRA ticket comments
4. Set up workflow based on ticket status
```
