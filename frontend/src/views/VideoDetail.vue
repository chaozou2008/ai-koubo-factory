<template>
  <AppLayout>
    <h2 style="margin-bottom: 24px">视频详情</h2>
    <el-card v-loading="loading" style="max-width: 700px">
      <el-descriptions :column="2" border v-if="video">
        <el-descriptions-item label="状态">
          <el-tag :type="statusType(video.status)">{{ statusText(video.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="消耗算粒">{{ video.cost_credits }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ new Date(video.created_at).toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">
          {{ video.completed_at ? new Date(video.completed_at).toLocaleString() : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="文案" :span="2">{{ video.script_text }}</el-descriptions-item>
        <el-descriptions-item v-if="video.error_message" label="错误信息" :span="2">
          <el-text type="danger">{{ video.error_message }}</el-text>
        </el-descriptions-item>
      </el-descriptions>
      <div style="margin-top: 24px" v-if="video">
        <el-button v-if="video.video_url" type="success" size="large" @click="downloadVideo">
          下载视频
        </el-button>
        <el-button @click="refresh" :loading="loading">刷新状态</el-button>
      </div>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { getVideo } from "../api/videos";
import AppLayout from "../components/AppLayout.vue";

const route = useRoute();
const video = ref<any>(null);
const loading = ref(false);

function downloadVideo() {
  if (video.value?.video_url) window.open(video.value.video_url);
}

function statusType(s: string) {
  const map: Record<string, string> = { done: "success", failed: "danger", processing: "warning", queued: "info" };
  return map[s] || "info";
}
function statusText(s: string) {
  const map: Record<string, string> = { done: "已完成", failed: "失败", processing: "生成中", queued: "排队中" };
  return map[s] || s;
}

async function refresh() {
  loading.value = true;
  try { video.value = (await getVideo(route.params.id as string)).data; }
  finally { loading.value = false; }
}

onMounted(refresh);
</script>
