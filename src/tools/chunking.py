"""
Utilities for handling large code insertions by chunking.

When inserting large amounts of code, JSON serialization can fail or
exceed token limits. This module provides helpers to split insertions
into manageable chunks.
"""


def split_large_insertion(text: str, chunk_size: int = 2000) -> list[dict]:
    """
    Split a large code insertion into multiple smaller insertions.
    
    Args:
        text: The code to insert
        chunk_size: Maximum characters per chunk (default 2000)
    
    Returns:
        List of dicts with 'text' and 'is_last' keys for sequential insertion
    
    Example:
        >>> chunks = split_large_insertion(long_code, chunk_size=1000)
        >>> for chunk in chunks:
        ...     insert_tool(filepath, line, chunk['text'])
    """
    if len(text) <= chunk_size:
        return [{"text": text, "is_last": True, "chunk_num": 1, "total_chunks": 1}]
    
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_size = 0
    chunk_num = 0
    
    for line in lines:
        line_with_newline = line + '\n'
        if current_size + len(line_with_newline) > chunk_size and current_chunk:
            # Emit current chunk
            chunk_text = ''.join(current_chunk)
            chunk_num += 1
            chunks.append({
                "text": chunk_text,
                "is_last": False,
                "chunk_num": chunk_num,
                "total_chunks": None  # Will update after we know total
            })
            current_chunk = [line_with_newline]
            current_size = len(line_with_newline)
        else:
            current_chunk.append(line_with_newline)
            current_size += len(line_with_newline)
    
    # Add final chunk
    if current_chunk:
        chunk_text = ''.join(current_chunk)
        chunk_num += 1
        chunks.append({
            "text": chunk_text,
            "is_last": True,
            "chunk_num": chunk_num,
            "total_chunks": chunk_num
        })
    
    # Update total_chunks for all chunks
    total = len(chunks)
    for chunk in chunks:
        chunk["total_chunks"] = total
    
    return chunks


def validate_json_serializable(obj: dict, max_size: int = 50000) -> tuple[bool, str]:
    """
    Validate that an object can be serialized to JSON without truncation.
    
    Args:
        obj: Object to validate
        max_size: Maximum JSON size in bytes (default 50KB)
    
    Returns:
        (is_valid, error_message)
    """
    import json
    
    try:
        serialized = json.dumps(obj)
        size = len(serialized.encode('utf-8'))
        
        if size > max_size:
            return False, f"JSON too large: {size} bytes (max {max_size})"
        
        return True, ""
    except Exception as e:
        return False, str(e)


def estimate_json_size(text: str) -> int:
    """
    Estimate how large a text will be when serialized to JSON.
    
    JSON encoding adds ~10-15% overhead due to escaping and quotes.
    """
    import json
    
    # Worst case: all special characters
    # Conservative estimate: 20% overhead
    base_size = len(text.encode('utf-8'))
    estimated = int(base_size * 1.2)
    return estimated

