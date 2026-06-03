package com.infopulse.app.data

import com.infopulse.app.domain.Briefing
import com.infopulse.app.domain.Category
import com.infopulse.app.domain.NewsItem

/**
 * 本地占位（mock）数据 —— 用于 UI 落地阶段。
 * 后续由后端真实接口（博查 Bocha 搜索 + DeepSeek 提炼）替换，结构保持一致。
 */
object MockData {

    val briefing = Briefing(
        reportDate = "2026-06-02",
        weekday = "星期一",
        generatedAt = "2026-06-03 06:02",
        categories = listOf(
            Category(
                id = "cat_ai",
                name = "AI 大模型",
                icon = "🤖",
                summary = "DeepSeek、智谱、Kimi 当日均有动态，国产模型继续发力",
                items = listOf(
                    NewsItem(
                        tag = "DeepSeek · 深度求索",
                        title = "DeepSeek 开源新一代推理模型，数学评测刷新国产纪录",
                        media = "机器之心",
                        date = "2026-06-02",
                        content = "深度求索发布 R 系列升级版，参数量 671B（MoE 激活 37B），在 AIME 2025 数学竞赛评测得分较上一代提升 9 个百分点，并同步开放权重与技术报告。",
                        extra = "▸ 模型：R-Next · 671B(MoE) · 对标 o3-mini",
                    ),
                    NewsItem(
                        tag = "GLM · 智谱AI",
                        title = "智谱 GLM 接入某国有大行智能客服，日均处理超百万次咨询",
                        media = "36氪",
                        date = "2026-06-02",
                        content = "智谱宣布 GLM-4 系列落地某国有大型银行，覆盖信用卡、理财问答场景，上线首周日均调用量突破 120 万次，意图识别准确率达 94%。",
                        extra = "▸ 合作：金融业 · 智能客服 · 百万级日调用",
                    ),
                    NewsItem(
                        tag = "Kimi · Moonshot AI",
                        title = "Kimi 上线长文档批量解析，免费用户单次可传 50 份文件",
                        media = "量子位",
                        date = "2026-06-02",
                        content = "月之暗面更新 Kimi 网页与 App 端，新增多文件批量上传与跨文档问答能力，免费用户单次最多 50 份、付费用户 200 份，已面向全量用户开放。",
                        extra = "▸ 新功能：多文档解析 · 全量上线 · 免费/付费分级",
                    ),
                ),
            ),
            Category(
                id = "cat_ev",
                name = "新能源车企",
                icon = "🚗",
                summary = "小米、比亚迪交付数据出炉，蔚来发布换电新进展",
                items = listOf(
                    NewsItem(
                        tag = "比亚迪 · BYD",
                        title = "比亚迪 5 月新能源销量公布，单月再创历史新高",
                        media = "财联社",
                        date = "2026-06-02",
                        content = "比亚迪发布 5 月产销快报，新能源汽车销量同比增长约 18%，海外出口占比首次突破 25%，DM 混动与纯电车型贡献接近五五开。",
                        extra = "▸ 数据：销量同比 +18% · 出口占比 >25%",
                    ),
                    NewsItem(
                        tag = "小米汽车 · Xiaomi",
                        title = "小米 SU7 系列累计交付突破新里程碑，二期工厂提速",
                        media = "界面新闻",
                        date = "2026-06-02",
                        content = "小米汽车公布最新交付数据，SU7 系列累计交付跨过新台阶；为缓解产能，北京二期工厂量产进度提前，月产能预计再上一个台阶。",
                        extra = "▸ 产能：二期工厂提速 · 月产能上调",
                    ),
                ),
            ),
            Category(
                id = "cat_internet",
                name = "互联网大厂",
                icon = "🏢",
                summary = "腾讯、阿里发布 AI 战略更新，字节加码出海",
                items = listOf(
                    NewsItem(
                        tag = "阿里巴巴 · Alibaba",
                        title = "阿里云通义上线企业知识库一体机，主打私有化部署",
                        media = "第一财经",
                        date = "2026-06-02",
                        content = "阿里云发布面向中大型企业的通义知识库一体机，支持本地私有化部署与国产芯片适配，主打数据不出域，已在制造、政务客户试点。",
                        extra = "▸ 产品：私有化一体机 · 国产芯片适配",
                    ),
                    NewsItem(
                        tag = "腾讯 · Tencent",
                        title = "微信测试 AI 搜索新入口，灰度向部分用户开放",
                        media = "晚点LatePost",
                        date = "2026-06-02",
                        content = "腾讯在微信内灰度测试由混元模型驱动的 AI 搜索入口，可直接对公众号与视频号内容做摘要问答，目前面向部分安卓用户开放。",
                        extra = "▸ 灰度：微信AI搜索 · 混元驱动 · 部分安卓",
                    ),
                ),
            ),
        ),
    )
}
