# DevLens Local ZIP Repository Analysis

## Purpose

Users can analyze either a public GitHub repository or a ZIP file of a local project.
Both input methods run the same scan, technology detection, Tree-sitter parser,
dependency analysis, module graph, source context selection, and Ollama explanation.

## API endpoints

**GitHub**: `POST /analyze`, JSON `{"repository_url":"https://github.com/user/repo"}`.

**Local ZIP**: `POST /analyze/upload`, `multipart/form-data`, field name `file`, containing a `.zip` archive.

Response: `project_name`, `statistics`, `files`, `directories`, `technology`, `code_analysis`, `ai_insights`. The GitHub response includes `repository_url`; ZIP response includes `source_type: "zip"` and has no repository URL.

## Supported local input and limits

- ZIP file, at most 25 MB compressed and 100 MB uncompressed.
- Up to 2,000 files and 3,000 ZIP entries.
- Single top-level folder is accepted and treated as the project root.
- Traversal paths, symbolic links, and unsupported file types in archives are rejected.
- Generated dependency directories such as `.git`, `node_modules`, `venv`, and `.venv` are ignored during extraction.
- Extracted content is kept in a temporary server-side directory for the duration of the request, then deleted.
- Ollama runs locally, but source contents may be supplied to your local model for explanation. Do not upload projects containing confidential credentials.

## Not supported

- Directly entering a Windows folder address into the browser (the web page cannot open arbitrary local paths).
- True browser folder selection without zipping (possible as a future separate upload mode).
- Automatic running/testing of the uploaded application.
- Authentication or persistent upload history.
