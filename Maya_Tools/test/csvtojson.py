import csv
import json
import os

# === 配置路径 ===
csv_path = r"C:\Users\justcause\Desktop\20250523_LOfacial-test_4\LOfacial-test_4_iPhone.csv"
output_dir = r"C:\Users\justcause\Desktop\20250523_LOfacial-test_4"
json_path = os.path.join(output_dir, "LOfacial-test_4_iPhone.json")
audio_path = ""  # 如有音频路径可填写

# === 读取CSV ===
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    headers = next(reader)
    data = list(reader)

# === 提取 blendshape 名称和数据 ===
blendshape_start_idx = 2  # 从 EyeBlinkLeft 开始
facs_names = headers[blendshape_start_idx:]

weight_mat = []
for row in data:
    weights = [float(val) for val in row[blendshape_start_idx:]]
    weight_mat.append(weights)

# === 构造 JSON 数据 ===
json_data = {
    "exportFps": 60,
    "trackPath": audio_path,
    "numPoses": len(facs_names),
    "numFrames": len(weight_mat),
    "facsNames": [name[0].lower() + name[1:] for name in facs_names],
    "weightMat": weight_mat
}

# === 保存为 JSON ===
with open(json_path, 'w', encoding='utf-8') as jsonfile:
    json.dump(json_data, jsonfile, indent=4)

print("✅ 转换完成，输出文件：", json_path)
