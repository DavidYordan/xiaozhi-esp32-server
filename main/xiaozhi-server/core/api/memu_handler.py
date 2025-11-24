import os
from aiohttp import web
from config.logger import setup_logging
from config.config_loader import get_project_dir

TAG = __name__


class MemuResourceHandler:
    def __init__(self, config: dict):
        self.config = config
        self.logger = setup_logging()
        data_dir = self.config.get("log", {}).get("data_dir", "data")
        self.base_dir = os.path.join(get_project_dir(), data_dir, "memu_resources")
        os.makedirs(self.base_dir, exist_ok=True)

    async def handle_get(self, request: web.Request):
        rid = request.match_info.get("rid", "")
        if not rid:
            return web.Response(status=400, text="invalid id")
        fpath = os.path.join(self.base_dir, rid)
        self.logger.bind(tag=TAG).info(f"MemU resource fetch: rid={rid}, path={fpath}")
        if not os.path.exists(fpath):
            return web.Response(status=404, text="not found")
        try:
            text = open(fpath, "r", encoding="utf-8").read()
            return web.Response(text=text, content_type="text/plain; charset=utf-8")
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Read resource failed: {e}")
            return web.Response(status=500, text="error")
