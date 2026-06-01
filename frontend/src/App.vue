<template>
  <div id="app" :class="{ 'dark-mode': isDark }">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSettingsStore } from './stores/settings'

const settingsStore = useSettingsStore()
const isDark = computed(() => settingsStore.isDark)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  transition: background 0.3s, color 0.3s;
}

#app {
  background: transparent;
}

.dark-mode {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #e0e0e0;
}

.dark-mode .el-table {
  background-color: rgba(45, 45, 45, 0.9);
  color: #e0e0e0;
}

.dark-mode .el-card {
  background-color: rgba(45, 45, 45, 0.9);
  color: #e0e0e0;
}

.dark-mode .el-table__header-wrapper th {
  background-color: rgba(102, 126, 234, 0.2);
  color: #e0e0e0;
}
</style>