from pathlib import Path

from app.core.config import Settings, load_yaml_file


def test_load_yaml_file_reads_models_config() -> None:
    data = load_yaml_file(Path("configs/models.yaml"))

    assert "models" in data
    assert len(data["models"]) >= 3


def test_settings_parse_cors_from_csv() -> None:
    settings = Settings(cors_allowed_origins="http://a.test,http://b.test")

    assert settings.cors_allowed_origins == ["http://a.test", "http://b.test"]

