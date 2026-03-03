# 前端界面使用说明

## 功能特性

### 📁 文件上传区域
- **拖拽上传**: 支持直接将文件拖拽到上传区域
- **点击上传**: 点击上传区域选择文件
- **文件类型**: 支持 .txt, .md, .pdf 文件
- **上传状态**: 实时显示上传进度和成功提示
- **文件列表**: 显示已上传文件，支持移除

### 💬 智能问答界面
- **聊天历史**: 清晰显示用户问题和 AI 回答
- **Markdown 支持**: 支持代码块、表格、粗体等 Markdown 格式
- **自动滚动**: 消息自动滚动到最新内容
- **输入反馈**: 发送按钮在处理时会显示加载状态

### 🎨 设计特点
- **现代设计**: 类似 ChatGPT 的简洁界面
- **渐变背景**: 紫色渐变背景，视觉效果出色
- **响应式**: 适配桌面和移动设备
- **动画效果**: 流畅的过渡动画

## 使用方法

### 1. 启动后端服务器

确保后端服务器正在运行：
```bash
python main.py
```

### 2. 打开前端页面

在浏览器中打开 `index.html` 文件：
```bash
# Windows
start index.html

# Mac
open index.html

# Linux
xdg-open index.html
```

或者直接双击 `index.html` 文件。

### 3. 上传文件

1. 将文件拖拽到左侧上传区域
2. 或者点击上传区域选择文件
3. 等待上传完成（约 1-3 秒）
4. 文件会上传到服务器并创建向量索引

### 4. 提问

1. 在右侧输入框输入问题
2. 点击"发送"按钮或按 Enter 键
3. 等待 AI 基于上传的文件回答问题
4. 回答会以 Markdown 格式显示

## API 接口

前端通过以下接口与后端通信：

- **上传文件**: `POST http://localhost:8000/upload`
  - 参数: `file` (FormData)
  - 响应: 包含文件信息和文本块数量

- **语义搜索**: `POST http://localhost:8000/ask?question={question}`
  - 参数: `question` (query parameter)
  - 响应: 包含相关文本块

- **健康检查**: `GET http://localhost:8000/health`
  - 响应: 服务状态和文档数量

## 注意事项

1. **跨域问题**: 如果直接打开 HTML 文件，需要配置 CORS。建议使用 HTTP 服务器运行。

2. **服务器地址**: 默认连接到 `http://localhost:8000`，如需修改请在 `index.html` 中更新 `API_BASE` 常量。

3. **文件大小**: 上传大文件可能需要更长时间处理。

4. **网络连接**: 首次运行时需要下载嵌入模型（95MB），请确保网络通畅。

## 技术栈

- **HTML5**: 语义化标签
- **CSS3**: 现代样式、渐变、动画、响应式布局
- **JavaScript (ES6+)**: Fetch API、异步处理、DOM 操作
- **无依赖**: 纯原生实现，无需安装任何框架

## 文件结构

```
fastapi-file-upload/
├── index.html      # 前端界面
├── main.py         # 后端服务
├── requirements.txt # 依赖列表
└── README.md       # 项目说明
```

## 自定义配置

### 修改 API 地址

在 `index.html` 中修改：
```javascript
const API_BASE = 'http://your-server:port';
```

### 修改主题颜色

在 `index.html` 的 CSS 部分修改渐变色：
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### 调整上传区域大小

在 `index.html` 中修改：
```css
.sidebar {
    width: 350px;
}
```

## 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

需要支持 ES6+ 和 Fetch API。

## 故障排除

### 无法连接到服务器
- 确认后端服务正在运行
- 检查端口号是否正确
- 查看浏览器控制台错误信息

### 文件上传失败
- 检查文件类型是否支持
- 确认文件未损坏
- 查看后端日志

### 无法显示 Markdown
- 检查浏览器是否支持 Markdown 渲染
- 查看浏览器控制台错误信息

## 未来改进

- [ ] 添加文件预览功能
- [ ] 支持批量上传
- [ ] 添加文件编辑功能
- [ ] 支持深色模式
- [ ] 添加语音输入
- [ ] 集成 LLM 生成最终答案
- [ ] 添加对话保存和恢复功能
