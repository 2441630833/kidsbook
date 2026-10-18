# kidsbook

> **KidsBook 3D** — 基于 Blender 3D 与 WebGL 技术打造的 3D 儿童故事书绘本网站，致敬 Amazon 经典高人气绘本触感与互动体验。100% 甄选世界公有领域经典童话，杜绝任何知识产权风险，支持中英双语、自然语音朗读与睡前陪伴模式，一键发布至 GitHub Pages。

---

## 🌟 项目亮点

- 🎨 **Amazon 榜单级艺术设计**：深度拆解 Amazon 儿童绘本终身畅销榜（如《好饿的毛毛虫》《晚安，月亮》）的触感、互动与舒缓色彩，重构 3D 微缩立体绘本。
- ⚖️ **严格规避知识产权侵犯（100% Public Domain）**：精选 1902 年出版的比阿特丽克斯·波特名作《彼得兔的故事》（*The Tale of Peter Rabbit*），全球公有领域授权，零版权隐患。
- 🪄 **Blender MCP 全自动化 3D 搭建**：通过 Python/Blender 自动化脚本，程序化构建 4 大高精度立体微缩模型场景（树根地洞、麦格雷戈菜园、醋栗丛险境、温暖卧室），并导出轻量级 WebGL GLB 模型。
- 📖 **3D 拟真翻页与弹跳立体偶秀**：页面翻转伴随 3D 模型弹性绽放弹起，支持 360° 拖动视角与探索。
- 🔊 **纯前端无版权 Web Audio 合成音效**：实时算法合成纸张翻动声、胡萝卜清脆咀嚼声、水花飞溅声、小鸟鸣叫与经典勃拉姆斯摇篮曲，无需外接音频文件。
- 🗣️ **中英双语自然语音伴读（TTS）**：集成 Web Speech API，支持中英双语朗读，朗读时实时荧光高亮当前词汇。
- 🌙 **晚安睡眠守护模式**：一键切换柔和低蓝光夜景滤镜，调暗场景光照，点亮暖黄烛光并循环柔和摇篮曲。
- 🚀 **GitHub Pages 开箱即用**：纯静态前端设计，内置 GitHub Actions 自动化 CI/CD 流水线，推送即上线。

---

## 📊 Amazon 畅销儿童绘本市场调研与设计拆解

我们对 Amazon **Children's Picture Books** 分类下的长期畅销榜进行了系统分析：

| 畅销榜经典作品 | 创作者 & 年代 | 畅销核心机制 | 版权状态分析 | 本项目借鉴与转化 |
| :--- | :--- | :--- | :--- | :--- |
| **《好饿的毛毛虫》** (*The Very Hungry Caterpillar*) | Eric Carle (1969) | 洞洞书物理互动、食物穿插感、认知探索 | ⚠️ 受版权保护（至 2064 年后） | **交互触感复刻**：将手指抠洞转化为 3D 场景中点击胡萝卜咀嚼、点击喷水壶喷水、小兔跳跃的趣味实时互动 |
| **《晚安，月亮》** (*Goodnight Moon*) | Margaret Wise Brown (1947) | 温暖绿色大房间、睡前心理仪式感、节奏韵律 | ⚠️ 受版权保护（至 2042 年后） | **晚安模式复刻**：第 4 章《洋甘菊茶与安睡》重现窗外月亮、夜间烛火与柔和星光，搭配舒缓算法摇篮曲 |
| **《彼得兔的故事》** (*The Tale of Peter Rabbit*) | Beatrix Potter (1902) | 调皮小兔的菜园冒险、精美田园自然画风 | ✅ **全球公有领域 (Public Domain)** | **本项目主打核心**：完美结合动物冒险、色彩柔和与全球知名度，合法合规数字化再造 |
| **《野兽国》** (*Where the Wild Things Are*) | Maurice Sendak (1963) | 想象力释放、情绪宣泄与温馨安全感 | ⚠️ 受版权保护 | 借鉴其“冒险冲刺—安全归家”的经典故事弧线设计 |

---

## ⚖️ 知识产权与公有领域合规声明

为确保本项目在全球范围内免受侵权索赔：
1. **作品著作权**：英国作者 Beatrix Potter 于 1943 年逝世，根据伯尔尼公约及多数国家法律（作者逝世后 70 年进入公有领域），其 1902 年发表的《彼得兔的故事》原著小说及原始形象已全面进入**公有领域（Public Domain）**。
2. **原创 3D 资产**：本项目中所有 3D 模型网格、材质贴图、灯光方案与渲染帧，均由本地 Blender 程序化自动化脚本独立创作生成，属于新创作品，享有独立发布许可。
3. **音频无外部素材**：所有翻页音效、咀嚼音、水滴音、提灯光芒声及背景摇篮曲，全部采用浏览器原生 Web Audio API 振荡器频率合成，不使用任何商业版权音效库。

---

## 🛠️ Blender 3D 场景管线（Blender MCP 规范）

本项目依托本地 Blender 5.2.2 LTS 环境与自动化脚本，构建了规范化的模型生成与导出管线：

```
blender_pipeline/
└── build_storybook_assets.py    # 自动化场景生成、材质配置、相机预设与 GLB 导出
assets/
├── models/
│   ├── peter_rabbit.glb         # 经典穿蓝夹克彼得兔角色模型 (190 KB)
│   ├── storybook_master.glb     # 3D 精装绘本立体外壳模型 (17 KB)
│   ├── scene1_burrow.glb        # 第1章：冷杉树根下的温馨沙洞 (406 KB)
│   ├── scene2_garden.glb        # 第2章：麦格雷戈的蔬菜园与胡萝卜 (440 KB)
│   ├── scene3_adventure.glb     # 第3章：醋栗丛网罩与遗落的蓝夹克 (361 KB)
│   └── scene4_bedtime.glb       # 第4章：夜幕卧室、月光与洋甘菊茶 (317 KB)
└── renders/
    ├── book_cover.png           # 绘本 3D 封面渲染图
    ├── chapter1_burrow.png      # 第1章 4K 场景插画渲染
    ├── chapter2_garden.png      # 第2章 4K 场景插画渲染
    ├── chapter3_adventure.png   # 第3章 4K 场景插画渲染
    └── chapter4_bedtime.png     # 第4章 4K 场景插画渲染
```

### 重新运行或自定义生成 3D 场景：
```powershell
& "E:\blender.exe" --background --python blender_pipeline/build_storybook_assets.py
```

---

## 🌐 网站架构与技术栈

- **3D 渲染引擎**：Three.js (WebGL, PBR 材质, ACES Filmic 色调映射, PCF 柔和阴影)
- **交互控制器**：Three.js OrbitControls (专为儿童与触屏优化的阻尼和视角限制)
- **音频架构**：Web Audio API (实时白噪声滤波纸张声、FM 频段水滴声、双振荡器钢片琴乐音)
- **语音朗读**：Web Speech API (支持中文 `zh-CN` 与英文 `en-US` 语速微调与分词位置跟踪)
- **UI 风格**：温暖水粉纸质感（Parchment & Gouache）、高圆角触摸按钮、完全响应式适配（手机、iPad 平板、电脑）

---

## 🚀 部署到 GitHub Pages

项目已内置自动化工作流配置文件 `.github/workflows/deploy.yml`。

### 方式一：GitHub Actions 自动部署（推荐）
1. 在 GitHub 仓库设置中：`Settings` -> `Pages` -> `Build and deployment` -> `Source` 选择 **GitHub Actions**。
2. 每次 `git push origin main` 即可自动完成构建与全球 CDN 部署。

### 方式二：经典分支部署
1. 在 GitHub 仓库设置中：`Settings` -> `Pages` -> `Source` 选择 **Deploy from a branch**。
2. 分支选择 `main`，目录选择 `/ (root)`，点击 **Save**。
3. 访问 `https://2441630833.github.io/kidsbook/` 即可浏览。

---

## 💻 本地运行预览

无需任何 Node.js 构建步骤，任何静态 HTTP 服务器均可立即启动：

```bash
# 使用 Python 启动本地测试服务器
python -m http.server 8080

# 随后在浏览器中打开：
http://localhost:8080
```

---

## 📜 许可证

- 故事文本与经典设定：**Public Domain** (公有领域)
- 3D 模型、代码与网页设计：**MIT License**
