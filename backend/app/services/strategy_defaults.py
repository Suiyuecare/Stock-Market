from app.schemas import MVPStrategyDefaults


class StrategyDefaultsService:
    """Expose the MVP strategy default configuration as a typed object."""

    def mvp_defaults(self) -> MVPStrategyDefaults:
        return MVPStrategyDefaults()
