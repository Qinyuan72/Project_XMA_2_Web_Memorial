import os
import re
import json

# 输入 .ini 文件的路径
ini_file_path = "Data/Chat_Raw/第二个小棉袄.ini"  # 替换为你的路径

# 初始化 JSON 数据结构
dialog_data = {"dialogs": [], "groups": []}

# 定义正则表达式分类
categories = {
    "Greeting": r"\b(hi|hello|hey|你好|早上好|晚上好|下午好)\b",
    "Thanks": r"\b(thank you|thanks|感激|谢谢|多谢)\b",
    "Question": r"\b(what|where|when|why|how|who|请问|是什么|在哪里|如何|为什么)\b",
    "Affirmative": r"\b(yes|yeah|right|ok|好|行|正确|没错|对的)\b",
    "Negative": r"\b(no|not|never|别|不|不是|拒绝|无法|没办法)\b",
    "Emotion": r"\b(happy|sad|angry|excited|难过|开心|愤怒|激动|害怕|孤单)\b",
    "HelpRequest": r"\b(help|support|assist|能不能帮|需要帮助|请帮我|我需要|建议)\b",
    "Learning": r"\b(learn|study|know|知识|学习|了解|明白|理解|技能)\b",
    "Farewell": r"\b(bye|goodbye|see you|再见|晚安|结束|结束聊天)\b",
    "Filler": r"\b(um|uh|啊|嗯|呃|呀|唉)\b",
    "Offensive": r"\b(fuck|damn|shit|垃圾|混蛋|讨厌|仇视)\b",
    "Storyline": r"\b(车被偷|报警|警察|国家|治安|抽象)\b"
}

# 初始化变量
current_group = "Group_1"
group_index = 1
dialog_count = 0
group_limit = 20
global_sequence_no = 0
group_sequences = {current_group: 0}
current_dialog = None  # 初始化为空，避免未定义错误

# 读取 .ini 文件
with open(ini_file_path, "r", encoding="utf-8") as file:
    ini_content = file.readlines()

# 解析逻辑
for line in ini_content:
    line = line.strip()
    if line:
        if line.startswith("[") and line.endswith("]"):
            # 新组逻辑，手动切换组
            if dialog_count >= group_limit:
                group_index += 1
                dialog_count = 0
                current_group = f"Group_{group_index}"
                group_sequences[current_group] = 0
            dialog_data["groups"].append({"Group": current_group, "Index": group_index})
        elif line.lower() in ["user", "chatgpt"]:
            global_sequence_no += 1
            group_sequences[current_group] += 1
            current_dialog = {
                "tag": line,
                "group": current_group,
                "content": "",
                "emotion_weight": 0.5,
                "display_probability": 1.0,
                "category": "Uncategorized",
                "global_sequence_no": global_sequence_no,
                "group_sequence_no": group_sequences[current_group]
            }
        else:
            if current_dialog:
                current_dialog["content"] = line
                # 分类逻辑
                for category, pattern in categories.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        current_dialog["category"] = category
                        current_dialog["emotion_weight"] = 0.8 if category == "Offensive" else 0.5
                        break
                dialog_data["dialogs"].append(current_dialog)
                current_dialog = None
                dialog_count += 1
                # 检查组大小
                if dialog_count >= group_limit:
                    group_index += 1
                    dialog_count = 0
                    current_group = f"Group_{group_index}"
                    group_sequences[current_group] = 0

# 输出到 JSON 文件
json_file_path = "Data/Chat_JSON/dialog_data.json"
os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(dialog_data, json_file, ensure_ascii=False, indent=4)

print(f"整合完成后的 JSON 数据已成功保存到 {json_file_path}")
