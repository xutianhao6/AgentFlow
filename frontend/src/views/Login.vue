<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { UserOutlined, ArrowRightOutlined } from '@ant-design/icons-vue'

const router = useRouter()
const user = useUserStore()
const username = ref('default')

function login() {
  user.login(username.value || 'default')
  router.push('/workflows')
}
</script>

<template>
  <div class="login">
    <!-- 左侧品牌区 -->
    <div class="login__brand">
      <div class="login__logo">
        <svg viewBox="0 0 24 24" width="28" height="28" fill="none" aria-hidden="true">
          <path
            d="M12 2 3 7v10l9 5 9-5V7l-9-5Z"
            stroke="#fff"
            stroke-width="1.6"
            stroke-linejoin="round"
          />
          <path d="m12 7-4 5h3l-1 5 5-7h-3l1-3Z" fill="#fff" />
        </svg>
        <span>AgentFlow</span>
      </div>
      <h1 class="login__headline">可视化编排<br />你的 AI 工作流</h1>
      <p class="login__sub">
        在画布上拖拽节点、连线、配置 IO，即可编排一条 AI 工作流。内置 LLM、知识检索、工具、代码、条件分支等节点库。
      </p>
      <div class="login__chips">
        <span>LangGraph 风格编译</span>
        <span>知识库 RAG</span>
        <span>插件即节点</span>
      </div>
    </div>

    <!-- 右侧登录卡 -->
    <div class="login__panel">
      <div class="login__card">
        <h2 class="login__title">登录</h2>
        <p class="login__hint">演示环境，输入任意用户名即可进入</p>
        <label class="login__label" for="username">用户名</label>
        <a-input
          id="username"
          v-model:value="username"
          placeholder="用户名"
          size="large"
          @press-enter="login"
        >
          <template #prefix><UserOutlined style="color: var(--af-text-tertiary)" /></template>
        </a-input>
        <a-button type="primary" size="large" block class="login__btn" @click="login">
          进入平台
          <ArrowRightOutlined />
        </a-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login {
  height: 100vh;
  display: flex;
}

/* 左侧品牌 */
.login__brand {
  flex: 1.1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 64px;
  color: #fff;
  background: linear-gradient(150deg, #4f46e5 0%, #6366f1 45%, #a855f7 100%);
}
.login__logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 22px;
  font-weight: 700;
}
.login__headline {
  margin: 40px 0 16px;
  font-size: 40px;
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.login__sub {
  max-width: 460px;
  font-size: 15px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.85);
}
.login__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}
.login__chips span {
  padding: 6px 14px;
  font-size: 13px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
}

/* 右侧登录 */
.login__panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--af-surface);
}
.login__card {
  width: 360px;
  max-width: 86vw;
}
.login__title {
  margin: 0;
  font-size: 26px;
  font-weight: 600;
}
.login__hint {
  margin: 6px 0 28px;
  font-size: 13px;
  color: var(--af-text-secondary);
}
.login__label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
  color: var(--af-text-secondary);
}
.login__btn {
  margin-top: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

@media (max-width: 860px) {
  .login__brand {
    display: none;
  }
}
</style>
