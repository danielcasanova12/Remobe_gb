import logging
import logging.handlers
import os
from pathlib import Path
from src.core.config import settings

def setup_logging():
    """
    Configura sistema de logging com:
    - Rotação automática de arquivos
    - Separação por níveis (info, error, debug)
    - Formatação rica
    - Logs no console para desenvolvimento
    """
    # Criar diretório de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar nível de log baseado no ambiente
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Formato detalhado para arquivos
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Formato simplificado para console
    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Limpar handlers existentes
    root_logger.handlers.clear()
    
    # 1. Handler para console (desenvolvimento)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 2. Handler para arquivo geral (INFO e acima) com rotação
    general_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    general_handler.setLevel(logging.INFO)
    general_handler.setFormatter(file_formatter)
    root_logger.addHandler(general_handler)
    
    # 3. Handler para erros (ERROR e CRITICAL) com rotação
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "errors.log",
        maxBytes=5 * 1024 * 1024,   # 5MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # 4. Handler para debug (apenas quando DEBUG=True) com rotação
    if settings.DEBUG:
        debug_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "debug.log",
            maxBytes=20 * 1024 * 1024,  # 20MB
            backupCount=3,
            encoding="utf-8"
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(file_formatter)
        root_logger.addHandler(debug_handler)
    
    # Log de inicialização
    logging.info(f"Sistema de logging configurado - Nível: {logging.getLevelName(level)}")
    logging.info(f"Logs sendo salvos em: {log_dir.absolute()}")
    if settings.DEBUG:
        logging.debug("Modo DEBUG ativo - logs detalhados habilitados")
