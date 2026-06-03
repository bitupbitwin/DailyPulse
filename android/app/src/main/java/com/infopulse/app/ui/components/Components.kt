package com.infopulse.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.infopulse.app.domain.Briefing
import com.infopulse.app.domain.NewsItem
import com.infopulse.app.ui.theme.Accent
import com.infopulse.app.ui.theme.BodyText
import com.infopulse.app.ui.theme.Card
import com.infopulse.app.ui.theme.Card2
import com.infopulse.app.ui.theme.Green
import com.infopulse.app.ui.theme.Line
import com.infopulse.app.ui.theme.PillText
import com.infopulse.app.ui.theme.SubText
import com.infopulse.app.ui.theme.TextMain
import com.infopulse.app.ui.theme.WarnBg
import com.infopulse.app.ui.theme.WarnText

/** 顶部应用栏：品牌 + 日期 + 提示横幅 */
@Composable
fun AppHeader(briefing: Briefing) {
    Column(
        Modifier
            .fillMaxWidth()
            .padding(start = 16.dp, end = 16.dp, top = 14.dp, bottom = 12.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("资讯脉搏", color = TextMain, fontSize = 18.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.width(6.dp))
            Text(
                "InfoPulse",
                color = Accent,
                fontSize = 11.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.align(Alignment.Bottom).padding(bottom = 2.dp),
            )
            Spacer(Modifier.weight(1f))
            Text(
                "📅 ${briefing.reportDate} · ${briefing.weekday}",
                color = SubText,
                fontSize = 12.sp,
            )
        }
        Spacer(Modifier.height(10.dp))
        Banner("⚠️ 本报告仅收录 ${briefing.reportDate} 当日发布的新闻，无新闻的板块已自动省略")
    }
}

@Composable
fun Banner(text: String) {
    Box(
        Modifier
            .fillMaxWidth()
            .background(WarnBg, RoundedCornerShape(8.dp))
            .border(1.dp, WarnText.copy(alpha = 0.25f), RoundedCornerShape(8.dp))
            .padding(horizontal = 10.dp, vertical = 7.dp)
    ) {
        Text(text, color = WarnText, fontSize = 11.5.sp, lineHeight = 16.sp)
    }
}

/** 标签小药丸 */
@Composable
fun Pill(text: String, fontSize: Float = 11f) {
    Box(
        Modifier
            .background(Card2, RoundedCornerShape(6.dp))
            .padding(horizontal = 9.dp, vertical = 3.dp)
    ) {
        Text(text, color = PillText, fontSize = fontSize.sp)
    }
}

/** 单条简报卡片（手机详情 / 平板右栏共用） */
@Composable
fun BriefingCard(item: NewsItem, modifier: Modifier = Modifier) {
    Column(
        modifier
            .fillMaxWidth()
            .background(Card, RoundedCornerShape(14.dp))
            .border(1.dp, Line, RoundedCornerShape(14.dp))
            .padding(14.dp)
    ) {
        Pill(item.tag)
        Spacer(Modifier.height(8.dp))
        Text(
            "📰 ${item.title}",
            color = TextMain,
            fontSize = 15.sp,
            fontWeight = FontWeight.SemiBold,
            lineHeight = 22.sp,
        )
        Spacer(Modifier.height(6.dp))
        Text("来源：${item.media}　|　日期：${item.date}", color = SubText, fontSize = 11.5.sp)
        Spacer(Modifier.height(8.dp))
        Text(item.content, color = BodyText, fontSize = 13.sp, lineHeight = 21.sp)
        Spacer(Modifier.height(8.dp))
        Text(item.extra, color = Green, fontSize = 12.sp)
        Spacer(Modifier.height(9.dp))
        Text("查看原文 ›", color = Accent, fontSize = 12.sp)
    }
}
