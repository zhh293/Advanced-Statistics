<template>
  <router-view />
</template>

<script setup>
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background-color: #f0f2f5;
  color: #333;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: #1a3c6e;
  margin-bottom: 20px;
}

.card-shadow {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
</style>
