<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">创建数字人形象</h2>
    <el-card style="max-width: 600px">
      <el-form :model="form" label-position="top">
        <el-form-item label="形象名称">
          <el-input v-model="form.name" placeholder="例如：我的AI主播" />
        </el-form-item>
        <el-form-item label="上传正面照片">
          <el-upload
            :auto-upload="false"
            :limit="1"
            :on-change="(file: any) => handleFileSelect(file, 'front')"
            :file-list="frontFiles"
            list-type="picture"
            accept="image/*"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon> 选择照片
            </el-button>
            <template #tip>
              <div style="color:#999;font-size:12px">上传您的正面清晰照片，用于生成数字人形象</div>
            </template>
          </el-upload>
          <el-progress v-if="uploading === 'front'" :percentage="uploadProgress" />
        </el-form-item>
        <el-alert
          title="创建形象后，系统将自动完成授权。MVP版本已自动对接火山引擎素材库。"
          type="info"
          :closable="false"
          style="margin-bottom: 16px"
        />
        <el-button type="primary" :loading="loading" @click="handleCreate" :disabled="!form.front_url">
          创建形象
        </el-button>
      </el-form>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { createAvatar, uploadPhoto } from "../api/avatars";
import AppLayout from "../components/AppLayout.vue";

const router = useRouter();
const loading = ref(false);
const uploading = ref("");
const uploadProgress = ref(0);
const frontFiles = ref<any[]>([]);
const form = ref({ name: "", front_url: "" });

async function handleFileSelect(file: any, type: string) {
  uploading.value = type;
  uploadProgress.value = 50;
  try {
    const url = await uploadPhoto(file.raw);
    if (type === "front") {
      form.value.front_url = url;
    }
    uploadProgress.value = 100;
    ElMessage.success("照片上传成功！");
  } catch {
    ElMessage.error("上传失败，请重试");
  } finally {
    uploading.value = "";
    uploadProgress.value = 0;
  }
}

async function handleCreate() {
  if (!form.value.name) {
    ElMessage.warning("请输入形象名称");
    return;
  }
  if (!form.value.front_url) {
    ElMessage.warning("请上传照片");
    return;
  }
  loading.value = true;
  try {
    await createAvatar(form.value.name, { front: form.value.front_url });
    ElMessage.success("数字人形象创建成功！");
    router.push("/avatars");
  } catch {
  } finally {
    loading.value = false;
  }
}
</script>