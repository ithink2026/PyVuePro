<template>
  <view class="login-page">
    <!-- 顶部品牌区 -->
    <view class="header">
      <view class="logo">补</view>
      <text class="title">RBAC+WS系统</text>
      <text class="desc">企业级综合管理平台</text>
    </view>

    <!-- 登录卡片 -->
    <view class="card">
      <!-- Tab -->
      <view class="tabs">
        <view
          class="tab"
          :class="{ on: currentTab === 0 }"
          @click="onTabChange(0)"
        >
          验证码登录
        </view>
        <view
          class="tab"
          :class="{ on: currentTab === 1 }"
          @click="onTabChange(1)"
        >
          密码登录
        </view>
      </view>

      <!-- 手机号 -->
      <view class="field">
        <view class="field-label">手机号</view>
        <view class="field-box">
          <text class="prefix">+86</text>
          <input
            class="inp"
            v-model="phone"
            type="number"
            maxlength="11"
            placeholder="请输入手机号"
          />
        </view>
      </view>

      <!-- 验证码模式 -->
      <view v-if="currentTab === 0">
        <view class="field">
          <view class="field-label">验证码</view>
          <view class="field-box">
            <input
              class="inp"
              v-model="code"
              type="number"
              maxlength="4"
              placeholder="请输入验证码"
            />
            <text class="sms" :class="{ off: cd > 0 }" @click="sendCode">
              {{ cd > 0 ? cd + "s" : "获取验证码" }}
            </text>
          </view>
        </view>
        <view class="btn" :class="{ loading }" @click="doCodeLogin">
          {{ loading ? "登录中…" : "立即登录" }}
        </view>
        <text class="tip">未注册手机号验证通过后自动创建账号</text>
      </view>

      <!-- 密码模式 -->
      <view v-if="currentTab === 1">
        <view class="field">
          <view class="field-label">登录密码</view>
          <view class="field-box">
            <input
              class="inp"
              v-model="password"
              type="password"
              placeholder="请输入密码"
            />
          </view>
        </view>
        <view class="btn" :class="{ loading }" @click="doPassLogin">
          {{ loading ? "登录中…" : "立即登录" }}
        </view>
        <text class="tip">首次使用请通过验证码登录创建账号</text>
      </view>
    </view>

    <!-- 底部 -->
    <text class="footer">登录即表示同意《用户协议》及《隐私政策》</text>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useUserStore } from "@/stores/user";
import { authApi } from "@/api/modules/auth";

const userStore = useUserStore();

const currentTab = ref(0);
const phone = ref("");
const code = ref("");
const password = ref("");
const loading = ref(false);
const cd = ref(0);

function onTabChange(idx: number) {
  if (loading.value) return;
  currentTab.value = idx;
}

function startCd() {
  let t = 60;
  cd.value = t;
  const iv = setInterval(() => {
    t--;
    cd.value = t;
    if (t <= 0) clearInterval(iv);
  }, 1000);
}

async function sendCode() {
  if (cd.value > 0) return;
  if (!phone.value || phone.value.length < 11) {
    uni.showToast({ title: "请输入正确的手机号", icon: "none" });
    return;
  }
  try {
    await authApi.sendCode(phone.value);
    startCd();
    uni.showToast({ title: "验证码已发送", icon: "none" });
  } catch {
    uni.showToast({ title: "发送失败，请重试", icon: "none" });
  }
}

async function doCodeLogin() {
  if (!phone.value || !code.value) {
    uni.showToast({ title: "请输入手机号和验证码", icon: "none" });
    return;
  }
  loading.value = true;
  try {
    const res = await authApi.phoneCodeLogin(phone.value, code.value);
    userStore.setToken(res.data.access_token, res.data.refresh_token);
    uni.redirectTo({ url: "/pages/operation/index" });
  } catch {
    uni.showToast({ title: "登录失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

async function doPassLogin() {
  if (!phone.value || !password.value) {
    uni.showToast({ title: "请输入手机号和密码", icon: "none" });
    return;
  }
  loading.value = true;
  try {
    const res = await authApi.phonePassLogin(phone.value, password.value);
    userStore.setToken(res.data.access_token, res.data.refresh_token);
    uni.redirectTo({ url: "/pages/operation/index" });
  } catch {
    uni.showToast({ title: "登录失败", icon: "none" });
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  if (userStore.token) {
    uni.redirectTo({ url: "/pages/operation/index" });
    return;
  }
  try {
    const res = await authApi.getLoginMode();
    if (res.data.mode === "ip") {
      try {
        const r = await authApi.ipLogin();
        userStore.setToken(r.data.access_token, r.data.refresh_token);
        uni.redirectTo({ url: "/pages/operation/index" });
        return;
      } catch {
        uni.showToast({ title: "IP 登录失败，请手动登录", icon: "none" });
      }
    }
  } catch {}
});
</script>

<style lang="scss" scoped>
.login-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f0f4f8;
  padding: 0 56rpx;
  box-sizing: border-box;
  overflow: hidden;
}

.header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100rpx;
  flex-shrink: 0;
}
.logo {
  width: 100rpx;
  height: 100rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #1b5e8a, #0f3a5c);
  color: #fff;
  font-size: 44rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}
.title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1d2129;
  letter-spacing: 6rpx;
  margin-bottom: 8rpx;
}
.desc {
  font-size: 24rpx;
  color: #86909c;
}

.card {
  width: 100%;
  background: #fff;
  border-radius: 24rpx;
  padding: 36rpx;
  margin-top: 40rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
}

/* Tab */
.tabs {
  display: flex;
  background: #f2f3f5;
  border-radius: 16rpx;
  padding: 4rpx;
  margin-bottom: 28rpx;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 26rpx;
  color: #86909c;
  border-radius: 12rpx;
  transition: all 0.2s;
  &.on {
    background: #fff;
    color: #1b5e8a;
    font-weight: 600;
    box-shadow: 0 1rpx 8rpx rgba(0, 0, 0, 0.06);
  }
}

.field {
  margin-bottom: 24rpx;
}
.field-label {
  font-size: 24rpx;
  color: #4e5969;
  font-weight: 500;
  margin-bottom: 8rpx;
}
.field-box {
  display: flex;
  align-items: center;
  background: #f7f8fa;
  border-radius: 16rpx;
  border: 1rpx solid #e5e6eb;
  padding: 0 20rpx;
  &:focus-within {
    border-color: #1b5e8a;
    background: #fff;
  }
}
.prefix {
  font-size: 26rpx;
  color: #86909c;
  padding-right: 18rpx;
  margin-right: 18rpx;
  border-right: 1rpx solid #e5e6eb;
  flex-shrink: 0;
}
.inp {
  flex: 1;
  height: 80rpx;
  font-size: 28rpx;
  color: #1d2129;
}
.sms {
  font-size: 24rpx;
  color: #1b5e8a;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  background: #e8f2fa;
  flex-shrink: 0;
  &.off {
    color: #c9cdd4;
    background: #f2f3f5;
  }
}

.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  background: linear-gradient(135deg, #1b5e8a, #0f3a5c);
  border-radius: 20rpx;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  letter-spacing: 4rpx;
  margin-top: 12rpx;
  &:active {
    opacity: 0.85;
  }
  &.loading {
    opacity: 0.6;
  }
}

.tip {
  display: block;
  text-align: center;
  margin-top: 20rpx;
  font-size: 22rpx;
  color: #c9cdd4;
}

.footer {
  margin-top: auto;
  padding: 32rpx 0;
  font-size: 20rpx;
  color: #c9cdd4;
  flex-shrink: 0;
}
</style>
