import http from 'k6/http';
import { sleep, check } from 'k6';

// Configuration options
/*
export let options = {
    stages: [
        { duration: '10s', target: 10 },  // Ramp-up to 10 VUs in 30 seconds
        { duration: '20', target: 50 },   // Stay at 50 VUs for 1 minute
        { duration: '30s', target: 100 }, // Ramp-up to 100 VUs in 30 seconds
        { duration: '20', target: 100 },  // Stay at 100 VUs for 1 minute
        { duration: '10', target: 50 },  // Ramp-down to 50 VUs in 30 seconds
        { duration: '10s', target: 0 },   // Ramp-down to 0 VUs in 30 seconds
    ],
};
 */
export let options = {
    scenarios: {
        constant_load: {
            executor: 'constant-vus', // Exécute un nombre constant de VUs
            vus: 5,                 // 50 utilisateurs constants
            duration: '10m',         // Pendant 10 minutes
        },
    },
};

// Base URL for your service
const BASE_URL = 'http://serviceclient:8080'; // Change this to the actual base URL of your service

// Function to test the /client/:id endpoint
export default function () {
    // Randomly choose an ID between 1 and 100
    let clientId = Math.floor(Math.random() * 80) + 1;

    // Test /client/:id
    let clientResponse = http.get(`${BASE_URL}/client/${clientId}`);

    check(clientResponse, {
        'status is 200 or 404': (r) => r.status === 200 || r.status === 404,
        'client found or not': (r) => r.json('error') === undefined || r.json('error') === 'Client not found',
    });

    // Test /client/:id/releve
    let releveResponse = http.get(`${BASE_URL}/client/${clientId}/releve`);

    check(releveResponse, {
        'status is 200 or 404': (r) => r.status === 200 || r.status === 404,
        'client or releve found or not': (r) => r.json('error') === undefined || r.json('error') === 'Client not found',
    });

    if(Math.floor(Math.random() * 100) === 1){
        let errorResponse = http.get(`${BASE_URL}/error`);
        check(errorResponse, {
            'status is 500': (r) => r.status === 500,
        });
    }

    // Pause for a short time before the next iteration
    sleep(1);
}
