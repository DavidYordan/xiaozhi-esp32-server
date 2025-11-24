import os
import uuid
import time
import json
import asyncio
from typing import List
import httpx
import re
from ..base import MemoryProviderBase, logger
from core.utils.util import get_local_ip
from config.config_loader import get_project_dir, load_config

TAG = __name__


class MemoryProvider(MemoryProviderBase):
    def __init__(self, config, summary_memory=None):
        super().__init__(config)
        self.memu_base_url = str(config.get("base_url", "")).strip()
        self.modality = str(config.get("modality", "conversation")).strip()
        self.serve_port = int(config.get("serve_port", 8765))
        self.http_port = int(load_config().get("server", {}).get("http_port", 8003))
        self.resources_dir = os.path.join(get_project_dir(), "data", "memu_resources")
        os.makedirs(self.resources_dir, exist_ok=True)
        self.use_memu = bool(self.memu_base_url)

    def _format_dialogue_text(self, msgs: List):
        lines = []
        for m in msgs:
            if getattr(m, "role", "") == "system":
                continue
            role = "User" if m.role == "user" else ("Assistant" if m.role == "assistant" else m.role)
            content = getattr(m, "content", "") or ""
            if content:
                lines.append(f"{role}: {content}")
        tstr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        lines.append(f"Time: {tstr}")
        return "\n".join(lines)

    def _write_resource_file(self, text: str) -> str:
        safe_role = re.sub(r"[^A-Za-z0-9._-]", "_", str(self.role_id or "role"))
        fname = f"{safe_role}_{uuid.uuid4().hex}.txt"
        fpath = os.path.join(self.resources_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(text)
        return fname

    async def save_memory(self, msgs):
        if not self.use_memu:
            return None
        if not msgs or len(msgs) < 2:
            return None

        text = self._format_dialogue_text(msgs)
        try:
            fname = self._write_resource_file(text)
        except Exception as e:
            logger.bind(tag=TAG).error(f"Write resource failed: {e}")
            return None
        resource_url = f"http://{get_local_ip()}:{self.http_port}/memu/resources/{fname}"
        payload = {"text": text, "modality": self.modality, "summary_prompt": None}
        try:
            logger.bind(tag=TAG).info(f"MemU memorize direct text, base: {self.memu_base_url}")
            async with httpx.AsyncClient(timeout=30) as client:
                await client.post(f"{self.memu_base_url}/memorize", json=payload)
            logger.bind(tag=TAG).info(f"Memorize success - Role: {self.role_id}")
        except Exception as e:
            logger.bind(tag=TAG).error(f"Memorize failed: {e}")
            return None
        return resource_url

    async def query_memory(self, query: str) -> str:
        if not self.use_memu:
            return ""
        if not query or not str(query).strip():
            return ""
        try:
            queries = [{"role": "user", "content": {"text": query or ""}}]
            logger.bind(tag=TAG).info(f"MemU retrieve base: {self.memu_base_url}, qlen: {len(query or '')}")
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(f"{self.memu_base_url}/retrieve", json={"queries": queries})
                r.raise_for_status()
                data = r.json()
        except Exception as e:
            logger.bind(tag=TAG).error(f"Retrieve failed: {e}")
            return ""

        parts = []
        cats = data.get("categories", []) or []
        items = data.get("items", []) or []
        resources = data.get("resources", []) or []
        if cats:
            parts.append("[Categories]")
            for c in cats[:5]:
                name = c.get("name", "")
                summary = c.get("summary") or c.get("description") or ""
                parts.append(f"- {name}: {summary}")
        if items:
            parts.append("[Memory Items]")
            for it in items[:8]:
                mtype = it.get("memory_type", "")
                summary = it.get("summary", "")
                parts.append(f"- ({mtype}) {summary}")
        if resources:
            parts.append("[Resources]")
            for r in resources[:5]:
                caption = r.get("caption") or r.get("url") or ""
                parts.append(f"- {caption}")
        return "\n".join(parts)
