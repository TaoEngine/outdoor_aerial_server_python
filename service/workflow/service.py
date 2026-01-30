from openai import OpenAI

client = OpenAI(
    base_url="https://api.siliconflow.cn/",
    api_key="sk-lgkzijwlgtwwyuecrfigyyljniqkyjztmtspigfliqvertpt",
)

message = client.chat.completions.create(
    model="Qwen/Qwen3-Omni-30B-A3B-Instruct",
    messages=[]
)
print(message.choices)
