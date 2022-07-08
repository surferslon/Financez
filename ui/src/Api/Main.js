import axios from "axios";
import { API_BASE_URL } from "../Config";


export function FetchReportData() {
    return axios.get(`${API_BASE_URL}/api/report_data`)
}