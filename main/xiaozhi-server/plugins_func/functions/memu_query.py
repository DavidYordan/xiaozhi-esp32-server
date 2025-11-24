from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action

TAG = __name__
logger = setup_logging()

MEMU_QUERY_FUNCTION_DESC = {
    "type": "function",
    "function": {
        "name": "memu_query",
        "description": (
            "查询长期记忆以辅助回答。当需要补充背景、关系、偏好或历史事件时调用，"
            "参数 query 传入用户当前问题或希望检索的主题关键词。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "查询内容或主题关键词，例如：‘她最近喜欢的音乐’",
                }
            },
            "required": ["query"],
        },
    },
}


@register_function("memu_query", MEMU_QUERY_FUNCTION_DESC, ToolType.SYSTEM_CTL)
def memu_query(conn, query: str):
    try:
        if not query or len(query.strip()) == 0:
            return ActionResponse(Action.REQLLM, None, "查询内容为空")
        if not hasattr(conn, "memory") or conn.memory is None:
            return ActionResponse(Action.REQLLM, None, "记忆未开启或不可用")

        future = None
        try:
            future = conn.loop and __import__("asyncio").run_coroutine_threadsafe(
                conn.memory.query_memory(query), conn.loop
            )
        except Exception as e:
            logger.bind(tag=TAG).error(f"提交记忆查询失败: {e}")
            return ActionResponse(Action.REQLLM, None, "记忆查询提交失败")

        try:
            result = future.result() if future else ""
        except Exception as e:
            logger.bind(tag=TAG).error(f"记忆查询执行失败: {e}")
            return ActionResponse(Action.REQLLM, None, "记忆查询失败")

        if not result:
            return ActionResponse(Action.REQLLM, "未检索到相关长期记忆", None)
        return ActionResponse(Action.REQLLM, result, None)
    except Exception as e:
        logger.bind(tag=TAG).error(f"memu_query工具错误: {e}")
        return ActionResponse(Action.ERROR, response=str(e))

