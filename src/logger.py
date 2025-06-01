import datetime
from enum import Enum
import logging
import sys 

class Logger: 
    def __init__(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"{timestamp}.log"
        
        self.dual_logger = self._setup_dual_logger()
        self.file_only_logger = self._setup_file_only_logger()

        self.dual_logger.info('adokasd')
    
    def _setup_dual_logger(self):
        """Logger that outputs to both file and stdout"""
        logger = logging.getLogger('dual_logger')
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(self.log_filename)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _setup_file_only_logger(self):
        """Logger that outputs only to file"""
        logger = logging.getLogger('file_only_logger')
        logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # File handler only
        file_handler = logging.FileHandler(self.log_filename)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        logger.addHandler(file_handler)
        
        return logger

    def log_file_only(self, message: str, level: int):
        if level == LoggingLevel.Debug:
            self.file_only_logger.debug(message)
        elif level == LoggingLevel.Error:
            self.file_only_logger.error(message)
        elif level == LoggingLevel.Info:
            self.file_only_logger.info(message)
        elif level == LoggingLevel.Fatal:
            self.file_only_logger.fatal(message)
        elif level == LoggingLevel.Warn:
            self.file_only_logger.warning(message)
        else:
            self.file_only_logger.info(message)
    def log_file_with_stdout(self, message: str, level: int):
        if level == LoggingLevel.Debug:
            self.dual_logger.debug(message)
        elif level == LoggingLevel.Error:
            self.dual_logger.error(message)
        elif level == LoggingLevel.Info:
            self.dual_logger.info(message)
        elif level == LoggingLevel.Fatal:
            self.dual_logger.fatal(message)
        elif level == LoggingLevel.Warn:
            self.dual_logger.warning(message)
        else:
            self.dual_logger.info(message)

class LoggingLevel(Enum):
    Info  = 1
    Warn  = 2 
    Debug = 3
    Error = 4
    Fatal = 5 
