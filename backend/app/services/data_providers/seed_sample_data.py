from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Base
from app.services.data_providers.csv_seed_loader import seed_from_sample_data


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    sample_data_dir = repo_root / "sample_data"
    engine = create_engine(get_settings().database_url)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        seed_from_sample_data(session, sample_data_dir)


if __name__ == "__main__":
    main()
