import axios from "axios";
import { API_BASE_URL } from "../Config";
import Cookies from 'js-cookie';

const apiClient = axios.create({
    withCredentials: true,
    baseURL: API_BASE_URL
})


export function SubmitSignup(username, password) {

}

export function SubmitLogin(username, password) {
  return apiClient.post('/api/users/login/', { username, password })
}

export function FetchReportData() {
  return apiClient.get('/api/entries/report_data/');
}

export function fetchEntries() {
  return apiClient.get('/api/entries/list/');
}

export function fetchAccounts() {
  return apiClient.get('/api/accounts/list/');
}

export function postNewEntry(date, acc_dr, acc_cr, total, comment) {
    return apiClient.post(
      '/api/entries/create/', { date, acc_dr, acc_cr, total, comment },
      {headers: { 'X-CSRFToken': Cookies.get('csrftoken') }}
    )
}
