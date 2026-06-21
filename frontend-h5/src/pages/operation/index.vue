<template>
  <view class="home-page">
    <!-- 顶部区域 -->
    <view class="top-section">
      <view class="status-bar" />
      <view class="top-row">
        <view class="user-card">
          <view class="avatar">补</view>
          <view class="user-text">
            <text class="greeting">上午好</text>
            <text class="name">欢迎回来</text>
          </view>
        </view>
        <view class="logout-btn" @click="handleLogout">退出</view>
      </view>

      <!-- 统计卡片 -->
      <view class="stats">
        <view class="stat">
          <text class="stat-num">0</text>
          <text class="stat-label">我的申报</text>
        </view>
        <view class="stat">
          <text class="stat-num">0</text>
          <text class="stat-label">审核中</text>
        </view>
        <view class="stat">
          <text class="stat-num">0</text>
          <text class="stat-label">已通过</text>
        </view>
      </view>
    </view>

    <!-- 快捷入口 -->
    <view class="service-section">
      <view class="section-title">快捷服务</view>
      <view class="service-grid">
        <view class="service-item" @click="handleClick('apply')">
          <view class="svc-icon blue">管</view>
          <text class="svc-label">数据管理</text>
        </view>
        <view class="service-item" @click="handleClick('progress')">
          <view class="svc-icon green">查</view>
          <text class="svc-label">进度查询</text>
        </view>
        <view class="service-item" @click="handleClick('history')">
          <view class="svc-icon orange">历</view>
          <text class="svc-label">历史记录</text>
        </view>
        <view class="service-item" @click="handleClick('policy')">
          <view class="svc-icon purple">告</view>
          <text class="svc-label">政策公告</text>
        </view>
      </view>
    </view>

    <!-- 最近动态 -->
    <view class="feed-section">
      <view class="section-title">
        <text>最近动态</text>
        <text class="more" @click="handleClick('more')">更多</text>
      </view>
      <view class="empty-box">
        <text class="empty-text">暂无动态</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { connectWebSocket, disconnectWebSocket } from '@/hooks/useWebSocket'

const userStore = useUserStore()

onMounted(() => {
  if (userStore.token) {
    connectWebSocket(userStore.token)
  }
})

onUnmounted(() => {
  disconnectWebSocket()
})

function handleLogout() {
  userStore.logout()
  uni.reLaunch({ url: '/pages/login/index' })
}

function handleClick(type: string) {
  const map: Record<string, string> = {
    apply: '数据管理',
    progress: '进度查询',
    history: '历史记录',
    policy: '政策公告',
    more: '最近动态',
  }
  uni.showToast({ title: map[type] || '功能开发中', icon: 'none' })
}
</script>

<style lang="scss" scoped>
.home-page {
  min-height: 100vh;
  background: #f0f4f8;
}

/* 顶部区域 */
.top-section {
  background: linear-gradient(155deg, #1b5e8a 0%, #153e5c 100%);
  padding: 0 36rpx 48rpx;
  border-radius: 0 0 40rpx 40rpx;
}
.status-bar {
  height: var(--status-bar-height, 44px);
}
.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 24rpx;
}
.user-card {
  display: flex;
  align-items: center;
}
.avatar {
  width: 76rpx;
  height: 76rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(255,255,255,0.28), rgba(255,255,255,0.08));
  border: 2rpx solid rgba(255,255,255,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34rpx;
  font-weight: 700;
  color: #fff;
  margin-right: 22rpx;
}
.user-text {
  display: flex;
  flex-direction: column;
}
.greeting {
  font-size: 24rpx;
  color: rgba(255,255,255,0.65);
  margin-bottom: 2rpx;
}
.name {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}
.logout-btn {
  font-size: 24rpx;
  color: rgba(255,255,255,0.7);
  padding: 12rpx 24rpx;
  border-radius: 12rpx;
  background: rgba(255,255,255,0.1);
  &:active {
    background: rgba(255,255,255,0.2);
  }
}

/* 统计卡片 */
.stats {
  display: flex;
  gap: 20rpx;
  margin-top: 36rpx;
}
.stat {
  flex: 1;
  background: rgba(255,255,255,0.12);
  border-radius: 20rpx;
  padding: 28rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  backdrop-filter: blur(4px);
}
.stat-num {
  font-size: 40rpx;
  font-weight: 700;
  color: #fff;
  margin-bottom: 6rpx;
}
.stat-label {
  font-size: 22rpx;
  color: rgba(255,255,255,0.65);
}

/* 快捷服务 */
.service-section {
  margin: 32rpx 32rpx 0;
}
.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1d2129;
  margin-bottom: 20rpx;
}
.service-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx;
}
.service-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 28rpx 0 24rpx;
  background: #fff;
  border-radius: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  &:active { background: #f5f7fa; transform: scale(0.97); }
}
.svc-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 700;
  color: #fff;
  margin-bottom: 10rpx;
}
.blue  { background: linear-gradient(135deg, #4da8da, #1b5e8a); }
.green { background: linear-gradient(135deg, #52c41a, #389e0d); }
.orange { background: linear-gradient(135deg, #fa8c16, #d46b08); }
.purple { background: linear-gradient(135deg, #a77dff, #722ed1); }
.svc-label {
  font-size: 24rpx;
  color: #4e5969;
}

/* 动态 */
.feed-section {
  margin: 32rpx 32rpx 0;
}
.more {
  font-size: 24rpx;
  color: #86909c;
  font-weight: 400;
}
.empty-box {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 72rpx 0;
  background: #fff;
  border-radius: 20rpx;
}
.empty-text {
  font-size: 26rpx;
  color: #c9cdd4;
}
</style>
