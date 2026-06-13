<template>
  <div class="auth-container">
    <el-card class="auth-card" shadow="always">
      <h1 style="text-align: center; margin-bottom: 24px">注册账号</h1>
      <el-form :model="form" label-position="top">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="公司名称（选填）">
          <el-input v-model="form.company_name" placeholder="您的公司或店铺名称" />
        </el-form-item>
        <el-button type="primary" :loading="loading" block @click="handleRegister">注册</el-button>
      </el-form>
      <p style="text-align: center; margin-top: 16px">
        已有账号？<el-link type="primary" @click="$router.push('/login')">立即登录</el-link>
      </p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { register } from "../api/auth";
import { useUserStore } from "../stores/user";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const form = ref({ phone: "", password: "", company_name: "" });

async function handleRegister() {
  loading.value = true;
  try {
    const resp = await register(form.value.phone, form.value.password, form.value.company_name || undefined);
    localStorage.setItem("token", resp.data.access_token);
    await userStore.fetchMe();
    ElMessage.success("注册成功，已赠送100算粒");
    router.push("/");
  } catch {
    // interceptor handles error message
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
.auth-card { width: 400px; }
</style>
