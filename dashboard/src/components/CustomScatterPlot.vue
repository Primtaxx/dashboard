<template>
    <div>
      <VuePlotly :data="scatterData" :layout="layout"></VuePlotly>
    </div>
  </template>
  
<script>
  import { VuePlotly } from 'vue3-plotly';
  
  export default {
    name: 'CustomScatterPlot',
    components: {
      VuePlotly,
    },
    props: {
      data: {
        type: Array,
        required: true,
      },    
    },
    computed: {
      scatterData() {
        return [this.data];
      },
      layout() {
        return {
          xaxis: {
            title: 'Age',
          },
          yaxis: {
            title: 'Height',
          },
        };
      },
    },
  };
  </script>
  