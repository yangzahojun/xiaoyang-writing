# -*- coding: utf-8 -*-
"""
多模型调用层：读 config.json，根据 provider 调用对应的 AI API。
支持：Claude（anthropic SDK）、DeepSeek / 智谱GLM / 通义千问（openai 兼容接口）。
换模型 = 改 config.json 一行，代码不用动。
"""

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

# 各 provider 的默认端点与默认模型
PROVIDERS = {
    "claude": {
        "base_url": None,  # 用官方默认端点
        "default_model": "claude-sonnet-4-6",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
    },
    "glm": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4-plus",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
    },
}


def load_config() -> dict:
    """读取配置。

    优先级：
    1. 公网部署时 —— 从 Streamlit Secrets 读取（Key 存在部署平台后台，不进代码库）；
    2. 本地运行时 —— 从 config.json 读取。
    """
    # 尝试从 Streamlit Secrets 读取
    try:
        import streamlit as st
        if st.secrets.get("api_key"):
            return {
                "provider": st.secrets.get("provider", "deepseek"),
                "api_key": st.secrets["api_key"],
                "model": st.secrets.get("model", ""),
                "base_url": st.secrets.get("base_url", ""),
            }
    except Exception:
        pass

    # 回退到本地 config.json
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_config(config: dict):
    """校验配置，返回 (provider, api_key, model, base_url)。"""
    provider = (config.get("provider") or "").strip().lower()
    api_key = (config.get("api_key") or "").strip()
    model = (config.get("model") or "").strip()
    base_url = (config.get("base_url") or "").strip()

    if provider not in PROVIDERS:
        raise ValueError(
            f"config.json 中的 provider「{provider}」不支持。"
            f"可选值：{', '.join(PROVIDERS.keys())}"
        )

    if not api_key or "替换" in api_key or "api key" in api_key.lower():
        raise ValueError(
            "还没有配置 API Key。请打开 config.json，把 api_key 替换成你自己的密钥。"
        )

    # 未填 model / base_url 时，用该 provider 的默认值
    if not model:
        model = PROVIDERS[provider]["default_model"]
    if not base_url:
        base_url = PROVIDERS[provider]["base_url"]

    return provider, api_key, model, base_url


def chat(system_prompt: str, history: list, temperature: float = 0.7, max_history_messages: int = 12) -> str:
    """
    调用 AI 模型，返回文本回复。

    :param system_prompt: 系统提示词（教练的角色设定）
    :param history: 对话历史，格式 [{"role": "user"/"assistant", "content": "..."}]
    :param temperature: 随机性（0=更稳定，1=更发散）
    :param max_history_messages: 发送给模型的最多历史消息条数（默认 12 条 ≈ 最近 6 轮问答）
    :return: 模型的文本回复
    """
    provider, api_key, model, base_url = _resolve_config(load_config())

    # 过滤出合法的角色，保证不会把 system 混进历史
    messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m.get("role") in ("user", "assistant") and m.get("content")
    ]
    if not messages:
        raise ValueError("对话内容为空，无法调用模型。")

    # 只保留最近 N 条消息，控制上下文长度、节省 token
    if len(messages) > max_history_messages:
        messages = messages[-max_history_messages:]

    if provider == "claude":
        return _chat_claude(api_key, model, system_prompt, messages, temperature)
    else:
        return _chat_openai_compatible(api_key, model, base_url, system_prompt, messages, temperature)


def _chat_claude(api_key, model, system_prompt, messages, temperature):
    import inspect
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    # Claude 要求 messages 首条必须是 user 角色
    if messages[0]["role"] == "assistant":
        messages.insert(0, {"role": "user", "content": "（开场）请开始。"})

    kwargs = dict(
        model=model,
        system=system_prompt,
        messages=messages,
        max_tokens=4096,
    )
    # 兼容不同版本的 anthropic SDK：旧版支持 temperature，新版（1.5+）已移除
    if "temperature" in inspect.signature(client.messages.create).parameters:
        kwargs["temperature"] = temperature

    resp = client.messages.create(**kwargs)
    # 拼接所有文本块
    return "".join(block.text for block in resp.content if hasattr(block, "text"))


def _chat_openai_compatible(api_key, model, base_url, system_prompt, messages, temperature):
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    resp = client.chat.completions.create(
        model=model,
        messages=full_messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content
