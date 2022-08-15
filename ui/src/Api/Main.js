import axios from "axios";
import { API_BASE_URL } from "../Config";

const apiClient = axios.create({
    withCredentials: true,
    baseURL: API_BASE_URL
})


export function SubmitSignup(username, password) {

}

export function SubmitLogin(username, password) {
    return apiClient.post('/api/users/login/', { username, password }, {withCredentials:true} )
}


export function FetchReportData() {
    return apiClient.get('/api/entries/report_data/');
}

export function fetchEntries() {
    return apiClient.get('/api/entries/list/');
}
