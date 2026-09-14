# 小羊爱写作 🐑（教育学学术写作训练智能体）

一个网页应用，帮助你（教育学本科生）系统训练学术写作能力，覆盖 **课程论文 / 毕业论文 / 期刊论文** 三类写作，内置 **6 个训练阶段**，支持**切换多个 AI 模型**，既可**本地运行**，也可**免费部署到公网分享**。

> 它的定位是「教练」，不是「代写」——它会引导你先动手思考，再给你结构化反馈，帮你真正提升写作能力。

---

## 一、功能一览

- **三类写作**：课程论文/作业、毕业论文、期刊/投稿论文
- **六个阶段**：选题 → 文献综述 → 提纲/框架 → 写作 → 批改 → 规范检查
- **两种模式**：
  - 🧑‍🏫 **训练模式**（推荐）：引导式，先提问再反馈，逼你动手
  - 🛠️ **辅助模式**：直接给示范、范例段落和建议
- **多模型切换**：Claude / DeepSeek / 智谱GLM / 通义千问，改一行配置即可切换
- **教育学专业知识**：内置教育学核心理论、研究方法、GB/T 7714 与 APA 7 引用规范

---

## 二、准备工作（只需做一次）

### 1. 安装 Python

1. 打开官网 <https://www.python.org/downloads/>，下载最新版 Python（3.10 或以上）。
2. 安装时**务必勾选**「`Add python.exe to PATH`」，然后一路「下一步」装完。

> 装好后，打开「命令提示符」（开始菜单搜 `cmd`），输入 `python --version`，如果显示版本号（如 `Python 3.12.1`）就说明装好了。

### 2. 注册一个 AI 模型的 API Key（任选一家即可）

| 模型 | 官网 | 价格 | 说明 |
|---|---|---|---|
| **DeepSeek** | <https://platform.deepseek.com> | 极便宜 | 中文好，推荐入门首选 |
| **Claude** | <https://console.anthropic.com> | 按量付费 | 写作辅导质量最高 |
| **智谱 GLM** | <https://open.bigmodel.cn> | 便宜 | 国产 |
| **通义千问** | <https://dashscope.aliyun.com> | 便宜 | 阿里 |

> 注册后，在对应平台的「API 密钥 / API Keys」页面创建一个 Key，复制保存好（它通常是一串以 `sk-` 开头的字符）。**不要泄露给别人**。

---

## 三、安装与配置

在「命令提示符」中，先进入本项目文件夹：

```bash
cd /d "d:\桌面\学术写作智能体"
```

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

> 如果 `pip` 提示不是内部命令，试试 `python -m pip install -r requirements.txt`。

### 2. 填写 API Key

用记事本打开本目录下的 `config.json`，把它改成类似这样（以 DeepSeek 为例）：

```json
{
  "provider": "deepseek",
  "api_key": "sk-你的真实密钥粘贴到这里",
  "model": "deepseek-chat",
  "base_url": ""
}
```

- `provider`：模型厂商，可选 `claude` / `deepseek` / `glm` / `qwen`
- `api_key`：你注册获得的密钥
- `model`：留空则用默认模型；想换可填具体模型名
- `base_url`：留空即可，会自动使用该厂商默认端点

> 想换成 Claude？把 `provider` 改成 `claude`、`api_key` 换成 Anthropic 的 Key 即可，其余不用动。

---

## 四、启动运行

```bash
python -m streamlit run app.py
```

> 如果上面这条提示 `streamlit` 不是内部命令，就用 `python -m streamlit run app.py`（推荐，两种环境都通用）。

运行后浏览器会自动打开一个网页。如果没自动打开，复制命令行里提示的网址（通常是 `http://localhost:8501`）粘贴到浏览器即可。

**使用流程**：
1. 在左侧栏选择「写作类型」「当前阶段」「模式」。
2. 右侧会出现教练的开场引导，按它的问题写下你的想法、初稿或疑问。
3. 智能体会给你结构化反馈，反复迭代直到满意。

---

## 五、部署到公网分享（Streamlit Cloud，免费）

> ⚠️ **务必先读这段安全提醒**：
> 公网部署后，**任何拿到网址的人都能使用它，并消耗你的 API Key 额度（费用由你承担）**。建议只在「短期分享给同学」时部署，用完可在平台暂停应用；不要在 Key 里充值大额余额。

### 1. 注册 GitHub 并上传代码

1. 注册 GitHub 账号：<https://github.com>（免费）。
2. 在 GitHub 新建一个仓库（**建议设为 Private 私有**，避免代码被别人看到），名字随意，如 `xiaoyang-writing`。
3. 把本项目文件夹里的文件（`app.py`、`llm.py`、`prompts.py`、`knowledge.py`、`requirements.txt`、`.streamlit/`、`.gitignore`）上传到该仓库。
   - ⚠️ **不要上传 `config.json` 和 `secrets.toml`**（`.gitignore` 已帮你排除，上传前再确认一下）。

### 2. 在 Streamlit Cloud 部署

1. 打开 <https://share.streamlit.io>，用 GitHub 账号登录。
2. 点 **New app** → 选择你刚建的仓库、分支 `main`、主文件 `app.py` → **Deploy**。
3. 部署成功后，你会得到一个公网网址：`https://你的应用名.streamlit.app`。

### 3. 配置密钥（Secrets）

1. 在应用页点 **Settings → Secrets**，粘贴以下内容（换成你的真实 Key）：

```toml
provider = "deepseek"
api_key = "sk-你的真实密钥"
model = "deepseek-chat"
base_url = ""
```

2. 保存后应用会自动重启，即可正常使用。

> 参考模板见 `secrets.toml.example`。本地开发仍用 `config.json`，二者互不影响（代码会自动判断优先级）。

---

## 六、文件说明

| 文件 | 作用 |
|---|---|
| `app.py` | 主程序（网页界面，含温暖可爱风 UI） |
| `llm.py` | 多模型调用层（自动识别 Secrets 或 config.json） |
| `prompts.py` | 提示词模板（阶段 × 类型 × 模式） |
| `knowledge.py` | 教育学知识库（可自行增删知识点） |
| `config.json` | 本地运行的配置（**不提交到 GitHub**） |
| `requirements.txt` | 依赖清单 |
| `.streamlit/config.toml` | Streamlit 主题与外观配置 |
| `.gitignore` | 排除密钥文件，防止误传 GitHub |
| `secrets.toml.example` | 公网部署密钥模板（复制改名后使用） |

---

## 七、常见问题

**Q1：运行时报错「还没有配置 API Key」？**
说明 `config.json` 里的 `api_key` 还是占位符，请按第三节填写真实密钥。

**Q2：提示 `streamlit` 不是内部命令？**
正常现象——`streamlit.exe` 没有加入系统 PATH。直接改用 `python -m streamlit run app.py` 即可（推荐）。

**Q3：想换模型但不想重启？**
直接修改 `config.json` 后，在网页侧边栏点「清空当前对话」即可生效（或关闭后重新 `streamlit run`）。

**Q4：担心费用？**
DeepSeek 等国产模型非常便宜，个人日常训练通常一个月几块钱以内。训练模式（先问再答）比直接代写更省 token。

**Q5：AI 回复不理想？**
- 把「模式」切到辅助模式，让 AI 更主动地给示范；
- 在对话里把问题说得更具体（你的专业、题目、卡在哪一步）；
- 反复追问「为什么」「还能怎么改」。

---

## 八、后续可扩展方向（可选）

- 把每次对话导出为 Markdown 存档
- 增加教育学范文/语料库作为可检索知识库
- 跨阶段记住你的选题，延续上下文
- 给分享版加一个简单的访问口令，进一步保护 Key 与额度
