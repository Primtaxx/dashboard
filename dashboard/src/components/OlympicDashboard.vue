<template>
  <div class="container">
    <div class="row my-3">
      <div class="col">
        <select v-model="currentRegion" @change="changeRegion" class="form-select">
          <option v-for="region in regions" :key="region.noc">{{ region.noc }} {{ region.notes }} {{ region.region }}</option>
        </select>
      </div>
    </div>
    <div class="row my-3">
      <div class="col">
        <select v-model="currentEvent" @change="changeEvent" class="form-select">
          <option v-for="event in events" :key="event.event">{{ event.event }}</option>
        </select>
      </div>
    </div>
    <div class="row my-3">
      <div class="col">
        <DataTable class="table table-hover table-striped" width="100%" :data="medalsData">
          <thead>
            <tr>
              <th v-for="column in columns" :key="column">{{ column }}</th>
            </tr>
          </thead>
          <tfoot></tfoot>
        </DataTable>
      </div>
    </div>
    <div class="row my-3">
      <div class="col-md-6">
        <VuePlotly :data="plotData2" :layout="{barmode: 'group'}"></VuePlotly>
      </div>
      <div class="col-md-6">
        <VuePlotly :data="plotData3" :layout="{barmode: 'group'}"></VuePlotly>
      </div>
    </div>
    <div class="row my-3">
      <div class="col-md-6">
        <VuePlotly :data="plotData4" :layout="{barmode: 'group'}"></VuePlotly>
      </div>
      <div class="col-md-6">
        <VuePlotly :data="plotData5" :layout="{barmode: 'group'}"></VuePlotly>
      </div>
    </div>
    <div class="row my-3">
      <div class="col">
        <HelloWorld :data="plotData6" />
      </div>
    </div>
    <div class="row my-3">
      <div class="col-md-6">
        <CustomScatterPlot :data="plotData6"></CustomScatterPlot>
      </div>
    </div>
  </div>
</template>

<script>
import CustomScatterPlot from '@/components/CustomScatterPlot.vue';
import DataTable from 'datatables.net-vue3';
import DataTablesLib from 'datatables.net-bs5';
import { VuePlotly } from 'vue3-plotly';
import axios from 'axios';

const apiUrl = 'http://127.0.0.1:5000/';

export default {
  name: 'App',
  components: {
    CustomScatterPlot,
    DataTable,
    VuePlotly,
  },
  data() {
    return {
      medalsData: [],
      plotData2: [],
      plotData3: [],
      plotData4: [],
      plotData5: [],
      plotData6: [],
      columns: ['medal', 'amount'],
      regions: {},
      currentRegion: {},
      events: {},
      currentEvent: {},
      selectedRegion: '',
    };
  },
  setup() {
    DataTable.use(DataTablesLib);
  },
  async mounted() {
    this.regions = await this.fetchRegions();
    console.log('Regions:', this.regions);
    this.plotData2 = await this.fetchMedals2('AUT');
    this.medalsData = await this.fetchMedals('AUT');
    this.plotData3 = await this.fetchCountBySex2('AUT');
    this.plotData4 = await this.fetchMFByNOC('AUT');
    this.plotData5 = await this.fetchAgeByHeight('AUT');
    this.plotData6 = await this.fetchAgeByHeight('AUT');
    this.events = await this.fetchEvents();
  },
  methods: {
    async fetchMedals(query) {
      const response = await axios.get(apiUrl + 'medals/' + query);
      return response.data;
    },
    async fetchMedals2(query) {
      const response = await axios.get(apiUrl + 'medals2/' + query);
      return response.data;
    },
    async fetchRegions() {
      const response = await axios.get(apiUrl + 'regions');
      return response.data;
    },
    async fetchCountBySex2(query) {
      const response = await axios.get(apiUrl + 'count_by_sex2/' + query);
      return response.data;
    },
    async fetchMFByNOC(query) {
      const response = await axios.get(apiUrl + 'MF_by_noc/' + query);
      return response.data;
    },
    async fetchAgeByHeight(query) {
      const response = await axios.get(apiUrl + 'age_by_height/' + query);
      return response.data;
    },
    async fetchEvents() {
      const response = await axios.get(apiUrl + 'events');
      return response.data;
    },

    async fetchMedalsByEvent(region, event) {
      const response = await axios.get(apiUrl + 'medals/' + region + '/' + event);
      return response.data;
    },
    async fetchMedals2ByEvent(region, event) {
      const response = await axios.get(apiUrl + 'medals2/' + region + '/' + event);
      return response.data;
    },
    async changeRegion() {
      let tempRegion = this.currentRegion.split(' ')[0];
      this.plotData2 = await this.fetchMedals2(tempRegion);
      this.plotData3 = await this.fetchCountBySex2(tempRegion);
      this.plotData4 = await this.fetchMFByNOC(tempRegion);
      this.plotData5 = await this.fetchAgeByHeight(tempRegion);
      this.plotData6 = await this.fetchAgeByHeight(tempRegion);
      this.medalsData = await this.fetchMedals(tempRegion);
    },



    async changeEvent() {
      const selectedRegion = this.currentRegion.noc;
      this.plotData2 = await this.fetchMedals2ByEvent(selectedRegion, this.currentEvent);
      this.medalsData = await this.fetchMedalsByEvent(selectedRegion, this.currentEvent);
    },


  },
};
</script>