from loguru import logger
from sys import stderr
from functools import wraps
import time
from pathlib import Path  
import pandas as pd


logger.remove()

logger.add(
                sink=stderr,
                format="{time} <r>{level}</r> <g>{message}</g> {file}",
                level="INFO"
            )

logger.add(
                "meu_arquivo_de_logs.log",
                format="{time} {level} {message} {file}",
                level="INFO"
            )


def log_decorator(func):
    def wrapper(*args, **kwargs):
        # Extrair caminho do arquivo a partir de argumentos usuais
        pasta = kwargs.get("pasta") or (args[0] if args else "")
        nome_arquivo = kwargs.get("arquivo") or "funcionarios.csv"
        caminho_arquivo = Path("desafio02_acelera") / nome_arquivo

        inicio = time.time()
        logger.info(f"Início '{func.__name__}' às {inicio:.6f} | caminho={caminho_arquivo}")
        logger.info(f"Início '{func.__name__}' caminho={caminho_arquivo}")

        try:
            df = func(*args, **kwargs)
            # Se a função não carregou ainda, mas quer medir linhas do arquivo, pode ler aqui:
            # df = pd.read_csv(caminho_arquivo)  # conforme design da função
            qtd_linhas = len(df) if isinstance(df, pd.DataFrame) else None
            fim = time.time()
            logger.info(f"Fim '{func.__name__}' às {fim:.6f} | linhas={qtd_linhas}")
            return df
        except Exception as e:
            fim = time.time()
            logger.exception(f"Erro em '{func.__name__}' | fim={fim:.6f} | duração={fim - inicio:.6f}s | caminho={caminho_arquivo}")
            raise
    return wrapper

# def log_decorator(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         logger.info(f"Chamando função '{func.__name__}' com args {args} e kwargs {kwargs}")
#         logger.info(f"Chamando função '{func.__name__}' com inicio as {time.time}")
#         logger.info(f"Chamando função '{func.__name__}' com fim as {time.time}")        
#         logger.info(f"Chamando função '{func.__name__}' com leitura do arquivo no caminho {pathlib.Path}")

#         try:
#             result = func(*args, **kwargs)
#             logger.info(f"Função '{func.__name__}' retornou {result}")
#             return result
#         except Exception as e:
#             logger.exception(f"Exceção capturada em '{func.__name__}': {e}")
#             raise  # Re-lança a exceção para não alterar o comportamento da função decorada
#     return wrapper