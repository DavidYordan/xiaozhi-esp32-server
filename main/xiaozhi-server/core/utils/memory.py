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
    provider_file = os.path.join(
        project_root, "core", "providers", "memory", class_name, f"{class_name}.py"
    )
    if os.path.exists(provider_file):
        lib_name = f"core.providers.memory.{class_name}.{class_name}"
        if lib_name not in sys.modules:
            sys.modules[lib_name] = importlib.import_module(f"{lib_name}")
        return sys.modules[lib_name].MemoryProvider(*args, **kwargs)

    logger.error(f"不支持的记忆服务类型: {class_name} - 路径不存在: {provider_file}")
    raise ValueError(f"不支持的记忆服务类型: {class_name}")
