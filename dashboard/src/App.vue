<template>
  <div id="app">
    <OlympicDashboard />
  </div>
</template>

<script>
import OlympicDashboard from "./components/OlympicDashboard.vue";

export default {
  name: "App",
  components: {
    OlympicDashboard,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
