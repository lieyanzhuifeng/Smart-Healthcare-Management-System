<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('[v0] 智慧医疗管理系统已启动')
})
</script>

<style>
#app {
  width: 100%;
  height: 100vh;
}
</style>
