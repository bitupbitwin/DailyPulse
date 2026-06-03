package com.infopulse.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.windowsizeclass.ExperimentalMaterial3WindowSizeClassApi
import androidx.compose.material3.windowsizeclass.calculateWindowSizeClass
import com.infopulse.app.ui.InfoPulseApp
import com.infopulse.app.ui.theme.InfoPulseTheme

class MainActivity : ComponentActivity() {
    @OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            InfoPulseTheme {
                // 通过 WindowSizeClass 自动判断手机/平板，无需用户手动切换
                val windowSizeClass = calculateWindowSizeClass(this)
                InfoPulseApp(windowSizeClass)
            }
        }
    }
}
