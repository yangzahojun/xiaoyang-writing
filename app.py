# -*- coding: utf-8 -*-
"""
小羊爱写作 — 教育学学术写作训练智能体
运行方式：python -m streamlit run app.py
"""

import json
from pathlib import Path

import streamlit as st
from prompts import WRITING_TYPES, STAGES, MODES, build_system_prompt, build_intro_message
import llm

# 历史对话持久化文件（本地，不提交到 GitHub）
HISTORY_FILE = Path(__file__).parent / "history.json"


def load_history():
    """从本地文件加载历史对话，失败或不存在时返回空列表。"""
    try:
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_history(messages):
    """把历史对话保存到本地文件。"""
    try:
        HISTORY_FILE.write_text(
            json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass

# ============================================================
# 页面设置
# ============================================================
st.set_page_config(
    page_title="小羊爱写作",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 温暖可爱风自定义样式
# ============================================================
def inject_css():
    st.markdown(
        """
        <style>
        /* ---------- 全局 ---------- */
        :root {
            --cream: #FFF8EE;
            --cream-2: #FFFDF7;
            --orange: #F59E6B;
            --orange-soft: #FDE8D4;
            --pink: #FF8FA8;
            --pink-soft: #FFE3EA;
            --brown: #4A3F35;
            --brown-soft: #8A7A6A;
            --card-border: #F3E3CF;
        }

        .stApp {
            background: linear-gradient(180deg, var(--cream) 0%, var(--cream-2) 100%);
        }

        /* ---------- 统一字号：所有文字同一大小，强调仅用加粗 ---------- */
        html, body, .stApp,
        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li,
        .hero-card, .hero-title, .hero-sub, .hero-tag {
            font-size: 16px !important;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            font-size: 16px !important;
            font-weight: 700 !important;
        }
        [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {
            font-size: 16px !important;
        }

        /* ---------- 侧边栏 ---------- */
        [data-testid="stSidebar"] {
            background: #FFFDF7;
            border-right: 2px solid var(--card-border);
        }
        [data-testid="stSidebar"] > div {
            padding-top: 1.2rem;
        }

        /* ---------- 主区标题卡片 ---------- */
        .hero-card {
            background: linear-gradient(135deg, #FFE9D6 0%, #FFE3EA 60%, #FFF2E6 100%);
            border: 2px solid var(--card-border);
            border-radius: 22px;
            padding: 1.6rem 1.8rem;
            margin-bottom: 0.6rem;
            box-shadow: 0 6px 18px rgba(245, 158, 107, 0.12);
        }
        .hero-title {
            font-weight: 700;
            color: var(--brown);
            letter-spacing: 0.5px;
            margin: 0;
        }
        .hero-sub {
            color: var(--brown-soft);
            margin-top: 0.35rem;
        }
        .hero-tag {
            display: inline-block;
            background: #FFFFFF;
            border: 1.5px solid var(--card-border);
            border-radius: 999px;
            padding: 0.3rem 0.9rem;
            margin: 0.55rem 0.4rem 0 0;
            color: var(--brown);
            font-weight: 600;
        }

        /* ---------- 聊天气泡 ---------- */
        [data-testid="stChatMessage"] {
            background: #FFFFFF;
            border: 1.5px solid var(--card-border);
            border-radius: 18px;
            box-shadow: 0 2px 8px rgba(74, 63, 53, 0.05);
            padding: 0.2rem 0.4rem;
        }

        /* ---------- 输入框 ---------- */
        [data-testid="stChatInput"] {
            border: 2px solid var(--card-border);
            border-radius: 16px;
        }
        [data-testid="stChatInput"] textarea {
            color: var(--brown);
        }

        /* ---------- 按钮 ---------- */
        .stButton > button {
            border-radius: 12px;
            border: 1.5px solid var(--card-border);
            background: #FFFFFF;
            color: var(--brown);
            font-weight: 600;
            transition: all 0.15s ease;
        }
        .stButton > button:hover {
            border-color: var(--orange);
            background: var(--orange-soft);
            color: var(--brown);
        }

        /* ---------- 侧边栏下拉框标签 ---------- */
        [data-testid="stSidebar"] .stSelectbox label {
            color: var(--brown);
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()

# ============================================================
# 侧边栏：选择任务
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:0.4rem;">
            <div style="font-weight:700; color:#4A3F35;">小羊爱写作</div>
            <div style="color:#8A7A6A;">教育学本科生 · 教练式写作训练</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    writing_type = st.selectbox(
        "① 写作类型",
        list(WRITING_TYPES.keys()),
        format_func=lambda k: WRITING_TYPES[k],
    )
    stage = st.selectbox(
        "② 当前阶段",
        list(STAGES.keys()),
        format_func=lambda k: STAGES[k],
    )
    mode = st.selectbox(
        "③ 模式",
        list(MODES.keys()),
        format_func=lambda k: MODES[k],
    )

    st.divider()

    # 显示当前模型配置状态（不显示 Key 明文）
    try:
        cfg = llm.load_config()
        provider = (cfg.get("provider") or "").strip()
        api_key = (cfg.get("api_key") or "").strip()
        model = (cfg.get("model") or "").strip()
        if not api_key or "替换" in api_key or "api key" in api_key.lower():
            st.warning("尚未配置 API Key")
        else:
            st.caption(f"当前模型：{provider} / {model or '默认'}")
    except Exception as e:
        st.warning(f"读取配置失败：{e}")

    st.caption("提示：切换类型/阶段/模式会追加新一轮引导，历史对话保留")

    if st.button("清空当前对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_key = ""
        save_history([])
        st.rerun()

# ============================================================
# 会话状态初始化（从本地文件加载历史，实现持久保存）
# ============================================================
key = f"{writing_type}|{stage}|{mode}"

if "messages" not in st.session_state:
    # 首次：尝试从本地文件加载历史对话
    st.session_state.messages = load_history()
    # 有历史则视为当前任务的延续，不再重复加开场白
    st.session_state.current_key = key if st.session_state.messages else ""

# ============================================================
# 检测任务切换：追加新的开场引导（不清空历史）
# ============================================================
if key != st.session_state.current_key:
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": build_intro_message(writing_type, stage, mode),
            "is_intro": True,
        }
    )
    st.session_state.current_key = key
    save_history(st.session_state.messages)

# ============================================================
# 主区
# ============================================================
st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-title">小羊爱写作</div>
        <div class="hero-sub">陪你一步步，把论文写扎实。</div>
        <div>
            <span class="hero-tag">{WRITING_TYPES[writing_type]}</span>
            <span class="hero-tag">{STAGES[stage]}</span>
            <span class="hero-tag">{MODES[mode]}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================================
# 用户输入
# ============================================================
if user_input := st.chat_input("在这里写下你的想法、初稿或问题……"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    system_prompt = build_system_prompt(writing_type, stage, mode)
    # 过滤掉开场引导，只保留真实问答，作为 AI 上下文
    history = [
        m for m in st.session_state.messages
        if m["role"] in ("user", "assistant") and not m.get("is_intro")
    ]

    with st.chat_message("assistant"):
        with st.spinner("小羊正在认真思考……"):
            try:
                # AI 只记最近 6 轮（12 条消息），控制上下文长度
                reply = llm.chat(system_prompt, history, max_history_messages=12)
                st.markdown(reply)
            except Exception as e:
                reply = f"出错了：{e}"
                st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_history(st.session_state.messages)
