import { createApp } from 'vue';
import DataTables from 'datatables.net-vue3';
import 'datatables.net-dt/css/jquery.dataTables.css';
import axios from 'axios';

import App from './App.vue';
import OlympicDashboard from './components/OlympicDashboard.vue';

const app = createApp(App);

app.component('olympic-dashboard', OlympicDashboard);

app.use(DataTables);
app.provide('axios', axios);

app.mount('#app');
