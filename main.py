from src.logger import Logger, LoggingLevel


def main():
    logger = Logger()
    logger.log_file_only('this s', LoggingLevel.Info)    
    logger.log_file_with_stdout('this', LoggingLevel.Info)

if __name__ == '__main__':
    main()