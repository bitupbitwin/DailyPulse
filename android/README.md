# 资讯脉搏 InfoPulse · Android 客户端（MVP / 本地 mock 数据）

落地阶段一：用本地占位数据跑通 UI，**手机 / 平板自动自适应**（通过 `WindowSizeClass`，无需用户手动切换）。后续接入后端真实接口（博查 Bocha 搜索 + DeepSeek 提炼）。

## 技术栈
- Jetpack Compose + Material 3
- `material3-window-size-class` 自适应手机 / 平板
- Kotlin 1.9.24 · AGP 8.5.2 · compileSdk 34 · minSdk 24
- 单 Activity + Compose；MVVM/分层将在接后端时补全（当前数据来自 `data/MockData.kt`）

## 目录
```
app/src/main/java/com/infopulse/app/
├── MainActivity.kt              # 入口，计算 WindowSizeClass
├── domain/Models.kt             # 领域模型（平台无关，便于未来 iOS 复用）
├── data/MockData.kt             # 本地占位新闻（后端接口将替换此处）
└── ui/
    ├── InfoPulseApp.kt          # 根布局：手机布局 / 平板布局
    ├── components/Components.kt # AppHeader / Banner / BriefingCard
    └── theme/                   # 深色科技风配色与主题
```

## 如何运行
### 方式一：Android Studio（推荐）
1. Android Studio（Koala 或更新）→ **Open** → 选择本 `android/` 目录。
2. 等待 Gradle 同步（首次会下载依赖；本项目已在 `settings.gradle.kts` 配置阿里云镜像，国内无需翻墙）。
3. 选择一个手机模拟器 **和** 一个平板模拟器（如 Pixel Tablet），分别 Run，观察自适应效果。

### 方式二：命令行
```bash
cd android
./gradlew assembleDebug      # 产物：app/build/outputs/apk/debug/app-debug.apk
./gradlew installDebug       # 连接设备/模拟器后安装
```
> 需要本地已安装 Android SDK，并在 `android/local.properties` 中写明：
> `sdk.dir=/你的/Android/Sdk`（Android Studio 会自动生成此文件）。

## 自适应说明
- **手机（Compact 宽度）**：底部导航（看板 / 订阅配置 / 我的）+ 顶部分类药丸切换 + 简报卡片列表。
- **平板 / 横屏（Medium & Expanded 宽度）**：左侧导航栏 + List-Detail 双栏（左列表、右详情）。
- 切换由系统窗口尺寸自动决定，旋转屏幕或分屏会实时切换。

## 占位数据
3 个分类：AI 大模型 / 新能源车企 / 互联网大厂。修改 `data/MockData.kt` 即可改预览内容。

---
⚠️ 说明：本工程在生成环境中**未做编译验证**（该环境无 Android SDK）。版本组合按已知稳定搭配选定；如首次同步报版本相关错误，按 Android Studio 提示升级 AGP/Kotlin 即可。
