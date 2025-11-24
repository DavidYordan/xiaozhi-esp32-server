import os
import sys
import importlib
from config.logger import setup_logging

logger = setup_logging()

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def create_instance(class_name, *args, **kwargs):
    class_name = str(class_name).strip().lower()
    lib_name = f"core.providers.memory.{class_name}.{class_name}"
    try:
        if lib_name not in sys.modules:
            sys.modules[lib_name] = importlib.import_module(lib_name)
        logger.info(f"加载记忆服务类型: {class_name}")
        return sys.modules[lib_name].MemoryProvider(*args, **kwargs)
    except Exception as e:
        provider_file = os.path.join(
            project_root, "core", "providers", "memory", class_name, f"{class_name}.py"
        )
        logger.error(f"记忆服务加载失败: {class_name} - {e} - 路径尝试: {provider_file}")
        raise ValueError(f"不支持的记忆服务类型: {class_name}")
