# Enhanced File Search

This document provides detailed information about the enhanced file search capabilities added to the AI agent solution.

## Overview

The enhanced file search feature improves the AI agent's ability to search and retrieve information from various file formats, providing more accurate and relevant responses with proper citations. This feature focuses on:

1. **Multiple file format support**
2. **Enhanced citation handling**
3. **File categorization**
4. **Relevance scoring**
5. **Semantic chunking**

## Supported File Formats

The enhanced file search supports the following file formats:

| Format | Extensions | Details |
|--------|------------|---------|
| JSON   | .json      | Structured data with automatic metadata extraction |
| Markdown | .md      | Text-based format with header and section parsing |
| Plain Text | .txt   | Basic text format with limited metadata |
| PDF    | .pdf       | Full text extraction with metadata support (requires PyPDF2) |
| Word   | .docx, .doc | Document parsing with properties extraction (requires python-docx) |

## Installation

To enable support for all file formats, install the required dependencies:

```bash
pip install -r src/requirements-enhanced.txt
```

## Technical Implementation

### File Parsing

The `FileParser` class in `src/api/file_parser.py` provides methods to parse different file formats and extract content and metadata. Each file type has a specialized parser that handles format-specific features:

- **JSON Parser**: Extracts structured data and looks for specific metadata fields
- **Markdown Parser**: Parses headers and sections to identify document structure
- **PDF Parser**: Extracts text and document properties from PDF files
- **Word Parser**: Parses document content and core properties from Word documents

### File Categorization

Files are automatically categorized based on:

1. **Explicit categories**: Categories defined within the file content or metadata
2. **File type**: Automatic categorization by file format
3. **Content analysis**: Identification of key themes and topics
4. **Metadata fields**: Brand, author, and other metadata properties

### Citation System

The enhanced citation system provides detailed references to source documents, including:

- File name or document title
- Section or page number
- Additional metadata (author, brand, ID)
- Relevance context

Citations are formatted as:

```
[Source: Document Name, Section X, Additional Metadata]
```

### Relevance Scoring

The relevance scoring algorithm considers several factors:

1. **Term frequency**: How often query terms appear in the document
2. **Phrase matching**: Exact matches to query phrases
3. **Metadata matching**: Query terms matching document metadata
4. **Document length normalization**: Preventing bias toward longer documents

### Semantic Chunking

Documents are divided into meaningful chunks to provide better context for citations:

1. **Paragraph-based chunking**: Using natural paragraph boundaries
2. **Sentence-based chunking**: Fallback to sentence boundaries if paragraphs are too long
3. **Overlap between chunks**: Maintaining context between adjacent chunks
4. **Size-based limits**: Ensuring chunks are neither too small nor too large

## Usage in Agent Instructions

The agent instructions have been updated to include guidelines for using the enhanced file search capabilities, with specific citation formats for each personality type.

## Extending Support

To add support for additional file formats:

1. Create a new parser method in `FileParser` class
2. Register the new file extension in the `supported_formats` list
3. Implement metadata extraction for the new format
4. Update the documentation to include the new format

## Performance Considerations

- File parsing happens at index creation time to minimize runtime overhead
- Content and metadata are cached to improve search performance
- Chunking uses semantic boundaries to maintain context quality
- Large files are processed incrementally to manage memory usage
