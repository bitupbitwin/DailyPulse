package com.infopulse.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.NavigationRail
import androidx.compose.material3.NavigationRailItem
import androidx.compose.material3.NavigationRailItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.windowsizeclass.WindowSizeClass
import androidx.compose.material3.windowsizeclass.WindowWidthSizeClass
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.infopulse.app.data.MockData
import com.infopulse.app.domain.Briefing
import com.infopulse.app.domain.Category
import com.infopulse.app.domain.NewsItem
import com.infopulse.app.ui.components.AppHeader
import com.infopulse.app.ui.components.BriefingCard
import com.infopulse.app.ui.theme.Accent
import com.infopulse.app.ui.theme.BadgeGreen
import com.infopulse.app.ui.theme.Bg
import com.infopulse.app.ui.theme.BodyText
import com.infopulse.app.ui.theme.Card
import com.infopulse.app.ui.theme.Card2
import com.infopulse.app.ui.theme.Line
import com.infopulse.app.ui.theme.NavBg
import com.infopulse.app.ui.theme.SubText
import com.infopulse.app.ui.theme.TextMain

/** 应用入口：根据屏幕宽度自动选择手机 / 平板布局，数据由 ViewModel 从后端拉取。 */
@Composable
fun InfoPulseApp(
    windowSizeClass: WindowSizeClass,
    vm: BriefingViewModel = viewModel(),
) {
    val briefing by vm.briefing.collectAsState()
    val isLoading by vm.isLoading.collectAsState()
    val isRefreshing by vm.isRefreshing.collectAsState()
    val error by vm.error.collectAsState()

    LaunchedEffect(Unit) { vm.loadBriefing() }

    // 后端不可用时回退到 MockData，保证界面始终有内容
    val usingMock = briefing == null
    val display = briefing ?: MockData.briefing

    Surface(Modifier.fillMaxSize(), color = Bg) {
        when {
            usingMock && isLoading -> LoadingScreen()
            windowSizeClass.widthSizeClass == WindowWidthSizeClass.Compact ->
                PhoneLayout(display, isRefreshing, usingMock, error) { vm.refreshAll() }
            else -> TabletLayout(display, isRefreshing) { vm.refreshAll() }
        }
    }
}

@Composable
private fun LoadingScreen() {
    Column(
        Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(160.dp))
        CircularProgressIndicator(color = Accent)
        Spacer(Modifier.height(16.dp))
        Text("正在加载今日简报…", color = SubText, fontSize = 13.sp)
    }
}

@Composable
private fun MockBanner(error: String? = null) {
    val msg = if (error.isNullOrBlank()) {
        "⚠️ 未连接后端，当前显示的是示例数据。请确认后端已启动，再点右下角刷新。"
    } else {
        "⚠️ 后端连接失败（$error），当前显示示例数据。请确认后端已启动后点刷新。"
    }
    Box(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp, vertical = 6.dp)
            .background(Color(0x22F59E0B), RoundedCornerShape(10.dp))
            .padding(horizontal = 12.dp, vertical = 8.dp)
    ) {
        Text(msg, color = BodyText, fontSize = 12.sp, lineHeight = 18.sp)
    }
}

/* ----------------------------- 手机布局 ----------------------------- */

@Composable
private fun PhoneLayout(
    briefing: Briefing,
    isRefreshing: Boolean = false,
    usingMock: Boolean = false,
    error: String? = null,
    onRefresh: () -> Unit = {},
) {
    var tab by remember { mutableIntStateOf(0) }        // 0=看板 1=配置 2=我的
    var openedCat by remember { mutableIntStateOf(-1) }  // -1=看板首页

    Scaffold(
        containerColor = Bg,
        floatingActionButton = {
            if (tab == 0) {
                FloatingActionButton(
                    onClick = { if (!isRefreshing) onRefresh() },
                    containerColor = Accent,
                ) {
                    if (isRefreshing) {
                        CircularProgressIndicator(color = Color.White, strokeWidth = 2.dp, modifier = Modifier.width(20.dp))
                    } else {
                        Text("🔄", fontSize = 18.sp)
                    }
                }
            }
        },
        bottomBar = {
            NavigationBar(containerColor = NavBg) {
                val entries = listOf("🏠" to "看板", "⚙️" to "订阅配置", "👤" to "我的")
                entries.forEachIndexed { i, (icon, label) ->
                    NavigationBarItem(
                        selected = tab == i,
                        onClick = { tab = i },
                        icon = { Text(icon, fontSize = 18.sp) },
                        label = { Text(label, fontSize = 11.sp) },
                        colors = NavigationBarItemDefaults.colors(
                            selectedIconColor = Accent,
                            selectedTextColor = Accent,
                            unselectedIconColor = SubText,
                            unselectedTextColor = SubText,
                            indicatorColor = Color(0x223B82F6),
                        ),
                    )
                }
            }
        },
    ) { pad ->
        Column(Modifier.padding(pad).fillMaxSize()) {
            when (tab) {
                0 -> {
                    AppHeader(briefing)
                    if (usingMock) MockBanner(error)
                    if (openedCat < 0) {
                        DashboardList(briefing.categories) { openedCat = it }
                    } else {
                        PhoneCategory(briefing.categories, openedCat) { openedCat = it }
                    }
                }
                1 -> Placeholder("⚙️ 订阅配置", "在这里增删分类、编辑关键词与自定义提示词（二期开放）")
                else -> Placeholder("👤 我的", "账号、推送、缓存与离线管理（二期开放）")
            }
        }
    }
}

@Composable
private fun DashboardList(categories: List<Category>, onOpen: (Int) -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
        Text(
            "今日各领域简报",
            color = SubText,
            fontSize = 13.sp,
            modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 14.dp, bottom = 6.dp),
        )
        categories.forEachIndexed { i, c -> OverviewCard(c) { onOpen(i) } }
        Spacer(Modifier.height(20.dp))
    }
}

@Composable
private fun OverviewCard(c: Category, onClick: () -> Unit) {
    Column(
        Modifier
            .fillMaxWidth()
            .padding(horizontal = 14.dp, vertical = 6.dp)
            .background(Card, RoundedCornerShape(16.dp))
            .border(1.dp, Line, RoundedCornerShape(16.dp))
            .clickable(onClick = onClick)
            .padding(16.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(c.icon, fontSize = 22.sp)
            Spacer(Modifier.width(10.dp))
            Text(
                c.name,
                color = TextMain,
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.weight(1f),
            )
            Box(
                Modifier
                    .background(Color(0x2222C55E), RoundedCornerShape(10.dp))
                    .padding(horizontal = 8.dp, vertical = 3.dp)
            ) {
                Text("已更新", color = BadgeGreen, fontSize = 11.sp)
            }
        }
        Spacer(Modifier.height(8.dp))
        Text(c.summary, color = SubText, fontSize = 13.sp, lineHeight = 20.sp)
        Spacer(Modifier.height(10.dp))
        Text("${c.items.size} 条 · 点击查看 ›", color = SubText, fontSize = 11.5.sp)
    }
}

@Composable
private fun PhoneCategory(categories: List<Category>, selected: Int, onSelect: (Int) -> Unit) {
    Column(Modifier.fillMaxSize()) {
        Row(
            Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState())
                .padding(horizontal = 12.dp, vertical = 12.dp)
        ) {
            categories.forEachIndexed { i, c ->
                val on = i == selected
                Box(
                    Modifier
                        .padding(end = 8.dp)
                        .background(if (on) Accent else Card2, RoundedCornerShape(20.dp))
                        .clickable { onSelect(i) }
                        .padding(horizontal = 14.dp, vertical = 7.dp)
                ) {
                    Text(
                        "${c.icon} ${c.name}",
                        color = if (on) Color.White else SubText,
                        fontSize = 13.sp,
                    )
                }
            }
        }
        val cat = categories[selected]
        Text(
            "【${cat.name}】 动态简报",
            color = SubText,
            fontSize = 13.sp,
            modifier = Modifier.padding(start = 16.dp, end = 16.dp, top = 4.dp, bottom = 4.dp),
        )
        LazyColumn(Modifier.fillMaxSize()) {
            items(cat.items) { item ->
                BriefingCard(item, Modifier.padding(horizontal = 14.dp, vertical = 6.dp))
            }
            item { Spacer(Modifier.height(20.dp)) }
        }
    }
}

@Composable
private fun Placeholder(title: String, desc: String) {
    Column(
        Modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(80.dp))
        Text(title, color = TextMain, fontSize = 20.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(12.dp))
        Text(desc, color = SubText, fontSize = 13.sp, lineHeight = 20.sp)
    }
}

/* ----------------------------- 平板布局 ----------------------------- */

@Composable
private fun TabletLayout(
    briefing: Briefing,
    isRefreshing: Boolean = false,
    onRefresh: () -> Unit = {},
) {
    var selCat by remember { mutableIntStateOf(0) }
    var selItem by remember { mutableIntStateOf(0) }
    val categories = briefing.categories
    if (categories.isEmpty()) {
        Placeholder("暂无分类", "后端未返回分类数据，请检查配置或点击刷新。")
        return
    }
    val cat = categories[selCat.coerceIn(0, categories.size - 1)]

    Row(Modifier.fillMaxSize()) {
        // 左侧导航栏
        NavigationRail(containerColor = NavBg) {
            Spacer(Modifier.height(8.dp))
            categories.forEachIndexed { i, c ->
                NavigationRailItem(
                    selected = selCat == i,
                    onClick = { selCat = i; selItem = 0 },
                    icon = { Text(c.icon, fontSize = 20.sp) },
                    label = { Text(c.name, fontSize = 10.sp) },
                    colors = NavigationRailItemDefaults.colors(
                        selectedIconColor = Accent,
                        selectedTextColor = Accent,
                        unselectedIconColor = SubText,
                        unselectedTextColor = SubText,
                        indicatorColor = Color(0x223B82F6),
                    ),
                )
            }
            NavigationRailItem(
                selected = false,
                onClick = { if (!isRefreshing) onRefresh() },
                icon = { Text(if (isRefreshing) "⏳" else "🔄", fontSize = 20.sp) },
                label = { Text("刷新", fontSize = 10.sp) },
            )
            NavigationRailItem(
                selected = false,
                onClick = {},
                icon = { Text("⚙️", fontSize = 20.sp) },
                label = { Text("配置", fontSize = 10.sp) },
            )
        }

        // 中间：新闻列表
        Column(Modifier.width(330.dp).fillMaxHeight().background(Bg)) {
            ColumnHeader("${cat.icon} ${cat.name}", "${briefing.reportDate} · ${cat.items.size} 条")
            HorizontalDivider(color = Line)
            LazyColumn(Modifier.fillMaxSize()) {
                itemsIndexed(cat.items) { i, item ->
                    ListRow(item, i == selItem) { selItem = i }
                    HorizontalDivider(color = Line)
                }
            }
        }

        // 右侧：简报详情（分类可能无当日新闻，做空态兜底避免越界）
        val safeItem = selItem.coerceIn(0, (cat.items.size - 1).coerceAtLeast(0))
        val current = cat.items.getOrNull(safeItem)
        Column(Modifier.weight(1f).fillMaxHeight().background(Bg)) {
            if (current == null) {
                ColumnHeader("简报详情", "${cat.name} · 今日暂无符合条件的新闻")
                HorizontalDivider(color = Line)
                Text(
                    "📭 今日该领域暂无符合条件的新闻",
                    color = SubText, fontSize = 13.sp,
                    modifier = Modifier.padding(16.dp),
                )
                return@Column
            }
            ColumnHeader("简报详情", "来源：${current.media} | 日期：${current.date}")
            HorizontalDivider(color = Line)
            Column(
                Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(14.dp)
            ) {
                BriefingCard(current)
                Spacer(Modifier.height(12.dp))
                Box(
                    Modifier
                        .fillMaxWidth()
                        .background(Card, RoundedCornerShape(14.dp))
                        .border(1.dp, Line, RoundedCornerShape(14.dp))
                        .padding(14.dp)
                ) {
                    Text(
                        "💬 想深入了解这条？可在此基于本篇素材继续追问（二期功能）。",
                        color = BodyText,
                        fontSize = 13.sp,
                        lineHeight = 21.sp,
                    )
                }
            }
        }
    }
}

@Composable
private fun ColumnHeader(title: String, subtitle: String) {
    Column(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 14.dp)) {
        Text(title, color = TextMain, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(3.dp))
        Text(subtitle, color = SubText, fontSize = 12.sp)
    }
}

@Composable
private fun ListRow(item: NewsItem, selected: Boolean, onClick: () -> Unit) {
    Column(
        Modifier
            .fillMaxWidth()
            .background(if (selected) Color(0x1A3B82F6) else Color.Transparent)
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 13.dp)
    ) {
        Box(
            Modifier
                .background(Card2, RoundedCornerShape(5.dp))
                .padding(horizontal = 7.dp, vertical = 2.dp)
        ) {
            Text(item.tag, color = com.infopulse.app.ui.theme.PillText, fontSize = 10.5.sp)
        }
        Spacer(Modifier.height(7.dp))
        Text(item.title, color = TextMain, fontSize = 13.5.sp, fontWeight = FontWeight.Medium, lineHeight = 19.sp)
        Spacer(Modifier.height(4.dp))
        Text("${item.media} · ${item.date}", color = SubText, fontSize = 11.sp)
    }
}
