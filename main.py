import logging
from LLMCodePromptBuilder import LLMCodePromptBuilder
from Loggers import configure_console_logger

configure_console_logger()
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app = LLMCodePromptBuilder()
    app.mainloop()
