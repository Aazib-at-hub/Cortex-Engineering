from app.chunking.chunker import chunk_text

def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   \n\n  ") == []

def test_chunk_text_small():
    content = "line 1\nline 2\nline 3\n"
    chunks = chunk_text(content, chunk_size=500, chunk_overlap=50)
    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 3
    assert chunks[0].content == content.strip()

def test_chunk_text_multiline_split():
    # Generate 50 lines of code
    lines = [f"def function_{i}():\n    return {i}\n" for i in range(50)]
    content = "".join(lines)
    chunks = chunk_text(content, chunk_size=200, chunk_overlap=50)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.start_line > 0
        assert chunk.end_line >= chunk.start_line
        assert len(chunk.content) > 0
