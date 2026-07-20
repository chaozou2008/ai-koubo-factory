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
        <el-descriptions-item label="内容" :span="2">
          {{ video.script_text || video.prompt || '-' }}
        </el-descriptions-item>
        <el-descriptions-item v-if="video.error_message" label="错误信息" :span="2">
          <el-text type="danger">{{ video.error_message }}</el-text>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 分镜进度（长视频） -->
      <div v-if="video?.long_video && segmentProgress" style="margin-top: 20px">
        <h4>📋 分镜生成进度</h4>
        <div v-for="seg in segmentProgress.segments" :key="seg.index"
             style="display:flex; align-items:center; gap:12px; padding: 10px 0; border-bottom: 1px solid #eee;">
          <span style="font-weight: bold; min-width: 64px;">分镜 {{ seg.index + 1 }}</span>
          <el-tag :type="seg.status === 'done' ? 'success' : seg.status === 'generating' ? 'warning' : seg.status === 'failed' ? 'danger' : 'info'" size="small">
            {{ seg.status === 'done' ? '已完成' : seg.status === 'generating' ? '生成中...' : seg.status === 'failed' ? '失败' : '排队中' }}
          </el-tag>
          <span v-if="seg.prompt" style="color: #999; font-size: 12px; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            {{ seg.prompt }}
          </span>
        </div>
      </div>

      <div v-if="video?.status === 'done' && video?.video_url" style="margin-top: 24px">
        <video :src="video.video_url" controls style="width:100%;max-width:360px;border-radius:8px;background:#000">
          您的浏览器不支持视频播放
        </video>
      </div>
      <div style="margin-top: 16px" v-if="video">
        <el-button v-if="video.video_url" type="success" @click="downloadVideo">下载视频</el-button>
        <el-button v-if="video.video_url" @click="copyLink">复制链接</el-button>
        <el-button @click="refresh" :loading="loading">刷新状态</el-button>
      </div>

      <!-- 分发到各平台 -->
      <div v-if="video?.status==='done'&&video?.video_url" style="margin-top:32px">
        <h3 style="margin-bottom:16px">📤 分发到各平台</h3>
        <el-row :gutter="12">
          <el-col :span="6" v-for="p in platforms" :key="p.name">
            <el-card shadow="hover" class="platform-card" :class="{busy: publishing}" @click="p.action()">
              <div style="text-align:center;font-size:28px">{{ p.icon }}</div>
              <div style="text-align:center;font-weight:bold;margin-top:8px">{{ p.name }}</div>
              <div style="text-align:center;font-size:12px;color:#999;margin-top:4px">
                <span v-if="publishing===p.name">⏳ 上传中...</span>
                <span v-else>{{ p.tip }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { getVideo } from "../api/videos";
import { publishVideo } from "../api/publish";
import AppLayout from "../components/AppLayout.vue";

const route = useRoute();
const video = ref<any>(null);
const loading = ref(false);
const publishing = ref("");

function downloadVideo() {
  if (video.value?.video_url) window.open(video.value.video_url);
}

function copyLink() {
  if (video.value?.video_url) {
    navigator.clipboard.writeText(video.value.video_url);
    ElMessage.success('链接已复制！');
  }
}

async function handlePublish(platform: string, name: string) {
  if (!video.value?.id) return;
  publishing.value = platform;
  try {
    const resp = await publishVideo(video.value.id, platform, '', video.value.prompt || video.value.script_text || '');
    if (resp.data.ok) {
      ElMessage.success(`${name}: ${resp.data.msg}`);
    } else {
      ElMessage.warning(`${name}: ${resp.data.msg}`);
    }
  } catch {
    ElMessage.error(`${name}: 上传失败`);
  } finally {
    publishing.value = "";
  }
}

const platforms = ref([
  { name: '抖音', icon: '🎵', tip: '自动打开浏览器上传', action: () => handlePublish('douyin', '抖音') },
  { name: '快手', icon: '📺', tip: '自动打开浏览器上传', action: () => handlePublish('kuaishou', '快手') },
  { name: '视频号', icon: '💬', tip: '自动打开浏览器上传', action: () => handlePublish('shipinhao', '视频号') },
  { name: '小红书', icon: '📕', tip: '自动打开浏览器上传', action: () => handlePublish('xiaohongshu', '小红书') },
]);

function statusType(s: string) {
  const map: Record<string, string> = { done: "success", failed: "danger", processing: "warning", video_generating: "warning", queued: "info" };
  return map[s] || "info";
}
function statusText(s: string) {
  const map: Record<string, string> = { done: "已完成", failed: "失败", processing: "生成中", video_generating: "生成中", queued: "排队中" };
  return map[s] || s;
}

// 分镜进度
const segmentProgress = computed(() => {
  if (!video.value?.segment_status) return null;
  try { return JSON.parse(video.value.segment_status); }
  catch { return null; }
});

async function refresh() {
  loading.value = true;
  try { video.value = (await getVideo(route.params.id as string)).data; }
  finally { loading.value = false; }
}

// 自动轮询：进行中每5秒刷新
let pollTimer: ReturnType<typeof setInterval> | null = null;
onMounted(() => {
  refresh();
  pollTimer = setInterval(() => {
    const s = video.value?.status;
    if (s === 'processing' || s === 'video_generating' || s === 'queued') {
      refresh();
    } else if (s === 'done' || s === 'failed') {
      if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
    }
  }, 5000);
});

onUnmounted(() => {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
});
</script>

<style scoped>
.platform-card { cursor: pointer; transition: all 0.2s; }
.platform-card:hover { transform: translateY(-2px); border-color: #409EFF; }
</style>
