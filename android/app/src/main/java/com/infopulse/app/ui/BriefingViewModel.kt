package com.infopulse.app.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.infopulse.app.data.BriefingRepository
import com.infopulse.app.domain.Briefing
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * 看板 ViewModel：负责从后端加载简报、下拉/按钮刷新。
 * API 不可用时不清空已有数据；首次失败由 UI 决定回退到 MockData。
 */
class BriefingViewModel(
    private val repo: BriefingRepository = BriefingRepository(),
) : ViewModel() {

    private val _briefing = MutableStateFlow<Briefing?>(null)
    val briefing: StateFlow<Briefing?> = _briefing.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing: StateFlow<Boolean> = _isRefreshing.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    /** 首次/普通加载：直接读后端已生成的简报（秒开）。 */
    fun loadBriefing() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            try {
                _briefing.value = repo.loadBriefing()
            } catch (e: Exception) {
                _error.value = e.message ?: "加载失败"
            } finally {
                _isLoading.value = false
            }
        }
    }

    /** 刷新：触发所有分类重新生成 → 轮询完成 → 重新加载。 */
    fun refreshAll() {
        viewModelScope.launch {
            _isRefreshing.value = true
            _error.value = null
            try {
                val cats = _briefing.value?.categories.orEmpty()
                for (cat in cats) {
                    val taskId = runCatching { repo.triggerRefresh(cat.id) }.getOrNull() ?: continue
                    repo.pollUntilDone(taskId)
                }
                _briefing.value = repo.loadBriefing()
            } catch (e: Exception) {
                _error.value = e.message ?: "刷新失败"
            } finally {
                _isRefreshing.value = false
            }
        }
    }
}
