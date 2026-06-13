<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">创建数字人形象</h2>
    <el-card style="max-width: 600px">
      <el-form :model="form" label-position="top">
        <el-form-item label="形象名称">
          <el-input v-model="form.name" placeholder="例如：我的AI主播" />
        </el-form-item>
        <el-form-item label="正面照片URL">
          <el-input v-model="form.front_url" placeholder="输入图片URL" />
        </el-form-item>
        <el-form-item label="侧面照片URL（可选）">
          <el-input v-model="form.side_url" placeholder="输入图片URL" />
        </el-form-item>
        <el-alert
          title="创建形象后，系统将生成授权二维码，需要真人扫码授权后方可使用。MVP版本自动完成授权。"
          type="info"
          :closable="false"
          style="margin-bottom: 16px"
        />
        <el-button type="primary" :loading="loading" @click="handleCreate">创建形象</el-button>
      </el-form>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { createAvatar } from "../api/avatars";
import AppLayout from "../components/AppLayout.vue";

const router = useRouter();
const loading = ref(false);
const form = ref({ name: "", front_url: "", side_url: "" });

async function handleCreate() {
  if (!form.value.name) {
    ElMessage.warning("请输入形象名称");
    return;
  }
  loading.value = true;
  try {
    const photoUrls: Record<string, string> = { front: form.value.front_url };
    if (form.value.side_url) photoUrls.side = form.value.side_url;
    await createAvatar(form.value.name, photoUrls);
    ElMessage.success("数字人形象创建成功");
    router.push("/avatars");
  } catch {
  } finally {
    loading.value = false;
  }
}
</script>
