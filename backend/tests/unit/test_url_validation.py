import pytest
from app.ingestion.cloner import validate_github_url
from app.core.exceptions import ValidationError

def test_validate_github_url_success():
    owner, repo = validate_github_url("https://github.com/fastapi/fastapi")
    assert owner == "fastapi"
    assert repo == "fastapi"

def test_validate_github_url_with_git_suffix():
    owner, repo = validate_github_url("https://github.com/psf/requests.git")
    assert owner == "psf"
    assert repo == "requests"

def test_validate_github_url_trailing_slash():
    owner, repo = validate_github_url("https://github.com/owner/my-repo/")
    assert owner == "owner"
    assert repo == "my-repo"

def test_validate_github_url_invalid():
    with pytest.raises(ValidationError):
        validate_github_url("https://gitlab.com/owner/repo")

    with pytest.raises(ValidationError):
        validate_github_url("not-a-url")

    with pytest.raises(ValidationError):
        validate_github_url("http://github.com/insecure/repo")
