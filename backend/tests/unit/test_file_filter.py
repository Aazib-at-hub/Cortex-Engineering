from pathlib import Path
from app.ingestion.filter import should_index_file, detect_language

def test_should_process_source_code_files():
    ok, _ = should_index_file(Path("src/main.py"), file_size_bytes=500)
    assert ok is True
    ok, _ = should_index_file(Path("components/Button.tsx"), file_size_bytes=1200)
    assert ok is True
    ok, _ = should_index_file(Path("lib/utils.rs"), file_size_bytes=3000)
    assert ok is True
    ok, _ = should_index_file(Path("README.md"), file_size_bytes=800)
    assert ok is True

def test_should_ignore_directories():
    ok, _ = should_index_file(Path("node_modules/package/index.js"), file_size_bytes=500)
    assert ok is False
    ok, _ = should_index_file(Path(".git/config"), file_size_bytes=500)
    assert ok is False
    ok, _ = should_index_file(Path(".next/static/chunk.js"), file_size_bytes=500)
    assert ok is False
    ok, _ = should_index_file(Path("__pycache__/test.cpython-311.pyc"), file_size_bytes=500)
    assert ok is False

def test_should_ignore_binaries_and_media():
    ok, _ = should_index_file(Path("assets/logo.png"), file_size_bytes=500)
    assert ok is False
    ok, _ = should_index_file(Path("bundle.min.js"), file_size_bytes=500)
    assert ok is False
    ok, _ = should_index_file(Path("archive.tar.gz"), file_size_bytes=500)
    assert ok is False
    ok, _ = should_index_file(Path("package-lock.json"), file_size_bytes=500)
    assert ok is False

def test_detect_language():
    assert detect_language(Path("app/main.py")) == "python"
    assert detect_language(Path("app/page.tsx")) == "typescript"
    assert detect_language(Path("script.js")) == "javascript"
    assert detect_language(Path("main.rs")) == "rust"
    assert detect_language(Path("main.go")) == "go"
    assert detect_language(Path("unknown.xyz")) == "plaintext"
