import logging


def setup_logging() -> None:
    """Configure logging for the entire application.
    
    Logs are displayed with timestamp, level, module name, and message.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
