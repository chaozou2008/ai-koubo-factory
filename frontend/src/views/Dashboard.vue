<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">工作台</h2>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card shadow="hover" @click="$router.push('/avatars/create')" class="quick-card">
          <el-icon :size="48" color="#409EFF"><UserFilled /></el-icon>
          <h3>创建数字人</h3>
          <p>上传照片，打造您的专属AI形象</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" @click="$router.push('/videos/create')" class="quick-card">
          <el-icon :size="48" color="#67C23A"><VideoCamera /></el-icon>
          <h3>生成视频</h3>
          <p>选模板、写文案、一键生成口播视频</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" @click="$router.push('/plans')" class="quick-card">
          <el-icon :size="48" color="#E6A23C"><Goods /></el-icon>
          <h3>升级套餐</h3>
          <p>更多算粒、更多形象、更多模板</p>
        </el-card>
      </el-col>
    </el-row>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from "../components/AppLayout.vue";
</script>

<style scoped>
.quick-card { text-align: center; cursor: pointer; padding: 24px; transition: transform 0.2s; }
.quick-card:hover { transform: translateY(-4px); }
.quick-card h3 { margin: 12px 0 8px; }
.quick-card p { color: #999; font-size: 13px; }
</style>
