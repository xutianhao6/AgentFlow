<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const user = useUserStore()
const username = ref('default')

function login() {
  user.login(username.value || 'default')
  router.push('/workflows')
}
</script>

<template>
  <div style="height:100vh;display:flex;align-items:center;justify-content:center">
    <a-card style="width:360px" title="AgentFlow 登录">
      <a-input v-model:value="username" placeholder="用户名" style="margin-bottom:12px" />
      <a-button type="primary" block @click="login">进入平台</a-button>
      <div style="color:#999;font-size:12px;margin-top:12px">演示环境，输入任意用户名即可</div>
    </a-card>
  </div>
</template>
