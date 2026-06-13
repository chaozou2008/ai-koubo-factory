<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">生成口播视频</h2>
    <el-card style="max-width: 700px">
      <el-form :model="form" label-position="top">
        <el-form-item label="选择数字人形象">
          <el-select v-model="form.avatar_id" placeholder="请选择" style="width: 100%">
            <el-option v-for="a in avatars" :key="a.id" :label="a.name" :value="a.id"
              :disabled="a.status !== 'active'" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择模板">
          <el-select v-model="form.template_id" placeholder="请选择" style="width: 100%">
            <el-option v-for="t in templates" :key="t.id" :label="`${t.name} (${t.industry})`" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="口播文案">
          <el-input v-model="form.script_text" type="textarea" :rows="6"
            placeholder="输入您的口播文案...&#10;&#10;例如：大家好，我是XX美容的专属顾问，今天给大家推荐一款..." />
        </el-form-item>
        <el-alert title="每条视频消耗 10 算粒" type="warning" :closable="false" style="margin-bottom: 16px" />
        <el-button type="primary" :loading="loading" size="large" @click="handleCreate">
          生成视频 (消耗10算粒)
        </el-button>
      </el-form>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getAvatars } from "../api/avatars";
import { getTemplates } from "../api/templates";
import { createVideo } from "../api/videos";
import { useUserStore } from "../stores/user";
import AppLayout from "../components/AppLayout.vue";

const router = useRouter();
const userStore = useUserStore();
const loading = ref(false);
const avatars = ref<any[]>([]);
const templates = ref<any[]>([]);
const form = ref({ avatar_id: "", template_id: "", script_text: "" });

onMounted(async () => {
  const [aRes, tRes] = await Promise.all([getAvatars(), getTemplates()]);
  avatars.value = aRes.data.items;
  templates.value = tRes.data.items;
});

async function handleCreate() {
  if (!form.value.avatar_id || !form.value.template_id || !form.value.script_text) {
    ElMessage.warning("请填写完整信息");
    return;
  }
  loading.value = true;
  try {
    const resp = await createVideo(form.value.avatar_id, form.value.template_id, form.value.script_text);
    await userStore.fetchBalance();
    ElMessage.success("视频生成任务已提交");
    router.push(`/videos/${resp.data.id}`);
  } catch {
  } finally {
    loading.value = false;
  }
}
</script>
