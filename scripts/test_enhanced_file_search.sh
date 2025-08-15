#!/bin/bash
# Test script for enhanced file search feature

echo "Testing Enhanced File Search Feature"
echo "==================================="

# Check for required dependencies
echo "Checking dependencies..."
python -c "
try:
    import PyPDF2
    print('PyPDF2 is installed')
except ImportError:
    print('PyPDF2 is NOT installed. Install with: pip install PyPDF2')

try:
    import docx
    print('python-docx is installed')
except ImportError:
    print('python-docx is NOT installed. Install with: pip install python-docx')
"

# Test file parser functionality
echo ""
echo "Testing file parser..."
python -c "
import sys
import os
sys.path.append('/workspaces/get-started-with-ai-agents/src')
from api.file_parser import FileParser

# Test with JSON file
json_file = '/workspaces/get-started-with-ai-agents/src/files/customer_info_1.json'
content, metadata = FileParser.parse_file(json_file)
print(f'JSON Test - File: {os.path.basename(json_file)}')
print(f'Metadata: {metadata}')
print(f'Content length: {len(content)} characters')

# Test with Markdown file
md_file = '/workspaces/get-started-with-ai-agents/src/files/product_info_1.md'
content, metadata = FileParser.parse_file(md_file)
print(f'\nMarkdown Test - File: {os.path.basename(md_file)}')
print(f'Metadata: {metadata}')
print(f'Content length: {len(content)} characters')

# Test chunking
print('\nTesting text chunking...')
text = 'This is paragraph one.\n\nThis is paragraph two with more content.\n\nThis is paragraph three with even more content to demonstrate chunking functionality.'
chunks = FileParser.chunk_text(text, chunk_size=50, overlap=10)
print(f'Chunked text into {len(chunks)} chunks:')
for i, chunk in enumerate(chunks):
    print(f'Chunk {i+1}: {chunk[:30]}... ({len(chunk)} chars)')

# Test citation formatting
print('\nTesting citation formatting...')
metadata = {
    'file_name': 'example.json',
    'title': 'Example Document',
    'brand': 'Test Brand',
    'document_id': '12345'
}
citation = FileParser.format_citation(metadata, 'Introduction')
print(f'Citation: {citation}')
"

# Test enhanced file search
echo ""
echo "Testing enhanced file search..."
python -c "
import sys
import os
sys.path.append('/workspaces/get-started-with-ai-agents/src')
from api.enhanced_file_search import EnhancedFileSearch

# Initialize enhanced search
search = EnhancedFileSearch()
print('Scanning files directory...')
file_metadata = search.scan_files()
print(f'Found {len(file_metadata)} files')

# Test categorization
print('\nTesting file categorization...')
categories = search.categorize_files()
print(f'Found {len(categories)} categories:')
for category, files in categories.items():
    print(f'- {category}: {len(files)} files')

# Test search functionality
print('\nTesting search functionality...')
query = 'tent camping outdoor'
results = search.search(query, top_k=3)
print(f'Search for \"{query}\" returned {len(results)} results:')
for i, result in enumerate(results):
    print(f'\nResult {i+1}:')
    print(f'File: {os.path.basename(result["file_path"])}')
    print(f'Score: {result["score"]:.2f}')
    print(f'Citation: {result["citation"]}')
    print(f'Content preview: {result["content"][:100]}...')
"

echo ""
echo "Enhanced file search test complete"
