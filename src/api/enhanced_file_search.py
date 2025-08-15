# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple

from .file_parser import FileParser

logger = logging.getLogger("azureaiapp")

class EnhancedFileSearch:
    """
    Enhanced file search capabilities for AI agent
    """
    
    def __init__(self, files_directory: str = None):
        """
        Initialize enhanced file search.
        
        :param files_directory: Directory containing files to search (default: src/files)
        """
        self.files_directory = files_directory or os.path.abspath(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files'))
        self.file_metadata_cache = {}
        self.file_content_cache = {}
        self.supported_formats = ['.json', '.md', '.txt', '.pdf', '.docx', '.doc']
    
    def scan_files(self) -> Dict[str, Dict[str, Any]]:
        """
        Scan all files in the directory and extract metadata.
        
        :return: Dictionary mapping file paths to metadata
        """
        file_metadata = {}
        
        # List all files in the directory
        for filename in os.listdir(self.files_directory):
            file_path = os.path.join(self.files_directory, filename)
            
            # Skip if not a file
            if not os.path.isfile(file_path):
                continue
                
            # Check if file format is supported
            extension = os.path.splitext(filename)[1].lower()
            if extension not in self.supported_formats:
                logger.warning(f"Skipping unsupported file format: {file_path}")
                continue
            
            try:
                # Parse file to extract content and metadata
                content, metadata = FileParser.parse_file(file_path)
                
                if content:
                    # Cache content and metadata
                    self.file_content_cache[file_path] = content
                    self.file_metadata_cache[file_path] = metadata
                    file_metadata[file_path] = metadata
                    
                    # Add relative path for easier reference
                    metadata["relative_path"] = os.path.relpath(
                        file_path, self.files_directory)
                    
                    logger.debug(f"Indexed file {filename} with metadata: {metadata}")
                else:
                    logger.warning(f"Failed to extract content from file: {file_path}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
        
        return file_metadata
    
    def categorize_files(self) -> Dict[str, List[str]]:
        """
        Categorize files based on metadata.
        
        :return: Dictionary mapping categories to file paths
        """
        categories = {}
        
        # Ensure metadata cache is populated
        if not self.file_metadata_cache:
            self.scan_files()
        
        # Group files by category
        for file_path, metadata in self.file_metadata_cache.items():
            file_categories = metadata.get("categories", [])
            
            # Add to appropriate categories
            for category in file_categories:
                if category not in categories:
                    categories[category] = []
                categories[category].append(file_path)
            
            # Also categorize by file type
            file_type = metadata.get("file_type", "unknown")
            if file_type not in categories:
                categories[file_type] = []
            categories[file_type].append(file_path)
            
            # Add brand as a category if available
            if "brand" in metadata:
                brand = metadata["brand"]
                if brand not in categories:
                    categories[brand] = []
                categories[brand].append(file_path)
        
        return categories
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.
        
        :param query: Search query
        :param top_k: Number of top results to return
        :return: List of search results with content and metadata
        """
        # Ensure caches are populated
        if not self.file_metadata_cache or not self.file_content_cache:
            self.scan_files()
            
        results = []
        query_terms = re.findall(r'\w+', query.lower())
        
        for file_path, content in self.file_content_cache.items():
            metadata = self.file_metadata_cache.get(file_path, {})
            
            # Calculate relevance score
            score = self._calculate_relevance(content, query_terms, metadata)
            
            if score > 0:
                # Chunk the content for more precise citation
                chunks = FileParser.chunk_text(content)
                
                # Find the most relevant chunk
                best_chunk_index = 0
                best_chunk_score = 0
                
                for i, chunk in enumerate(chunks):
                    chunk_score = self._calculate_relevance(chunk, query_terms, {})
                    if chunk_score > best_chunk_score:
                        best_chunk_score = chunk_score
                        best_chunk_index = i
                
                # Get the best chunk and its citation
                best_chunk = chunks[best_chunk_index]
                section = f"Section {best_chunk_index + 1}"
                
                # Format citation
                citation = FileParser.format_citation(metadata, section)
                
                results.append({
                    "content": best_chunk,
                    "metadata": metadata,
                    "score": score,
                    "file_path": file_path,
                    "citation": citation
                })
        
        # Sort by relevance and take top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _calculate_relevance(self, content: str, query_terms: List[str], 
                            metadata: Dict[str, Any]) -> float:
        """
        Calculate relevance score for content based on query terms.
        
        :param content: Document content
        :param query_terms: List of query terms
        :param metadata: Document metadata
        :return: Relevance score (higher is more relevant)
        """
        if not content or not query_terms:
            return 0
            
        score = 0
        content_lower = content.lower()
        
        # Term frequency scoring
        for term in query_terms:
            term_count = content_lower.count(term)
            score += term_count * 1.0
        
        # Exact phrase matching (higher weight)
        query_phrase = " ".join(query_terms)
        if query_phrase in content_lower:
            score += len(query_terms) * 2.0
        
        # Metadata matching (even higher weight)
        for term in query_terms:
            # Check categories
            if "categories" in metadata:
                for category in metadata["categories"]:
                    if term in category.lower():
                        score += 3.0
            
            # Check title
            if "title" in metadata and term in metadata["title"].lower():
                score += 3.0
                
            # Check brand
            if "brand" in metadata and term in metadata["brand"].lower():
                score += 2.5
        
        # Normalize by content length to avoid favoring longer documents
        score = score / (len(content) / 100)  # per 100 chars
        
        return score
