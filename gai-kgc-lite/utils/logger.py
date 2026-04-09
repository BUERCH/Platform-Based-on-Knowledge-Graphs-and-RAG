# import logging
# import os 

# def setup_logger(logger_name, log_file, overwrite=False ,log_level=logging.INFO):
#     """
#     设置一个 logger，以将日志信息写入指定的文件。

#     :param logger_name: logger 的名称
#     :param log_file: 要写入的日志文件路径
#     :param log_level: 日志级别
#     :return: logger 实例
#     """
#     # 创建日志目录（如果不存在的话）
#     log_dir = os.path.dirname(log_file)
#     if not os.path.exists(log_dir) and log_dir:
#         os.makedirs(log_dir)
#     if os.path.exists(log_file):
#         if not overwrite:
#             print("existing log file")
#             return logging.getLogger(logger_name)
#         else: os.system(f"cat /dev/null > {log_file}")

#     # 创建 logger
#     logger = logging.getLogger(logger_name)
#     logger.setLevel(log_level)

#     # 创建文件处理器
#     file_handler = logging.FileHandler(log_file, encoding="utf-8")
#     file_handler.setLevel(log_level)

#     # 创建格式器并将其设置到处理器
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     file_handler.setFormatter(formatter)

#     # 将处理器添加到 logger
#     logger.addHandler(file_handler)

#     return logger
import logging
import os
import sys

def setup_logger(logger_name, log_file, overwrite=False, log_level=logging.INFO):
    """
    设置一个 logger，同时输出到【文件】和【控制台】。
    修复了 Windows 兼容性问题，并防止重复添加 Handler。
    """
    # 1. 创建日志目录
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir) and log_dir:
        os.makedirs(log_dir)

    # 2. 如果需要覆盖，且文件存在，使用 Python 原生方式清空文件
    if overwrite and os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.truncate(0) # 清空内容
            
    # 3. 获取 logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # 4. 【关键】检查是否已经添加过处理器
    # 如果已经有处理器，说明是重复调用，直接返回，防止一条日志打印两遍
    if logger.handlers:
        return logger

    # 5. 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 6. 创建文件处理器 (FileHandler) -> 写文件
    # mode='a' 表示追加，'w' 表示覆盖。如果不overwrite，默认追加
    mode = 'w' if overwrite else 'a'
    file_handler = logging.FileHandler(log_file, mode=mode, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 7. 【关键】创建控制台处理器 (StreamHandler) -> 输出到屏幕
    # 让你能实时看到进度，而不是盯着黑屏发呆
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger