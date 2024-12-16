import http from 'k6/http';
import { check, sleep } from 'k6';

// Options
export const options = {
    stages: [
        { duration: '10s', target: 10 },  // Ramp-up to 10 VUs in 30 seconds
        { duration: '20', target: 50 },   // Stay at 50 VUs for 1 minute
        { duration: '30s', target: 100 }, // Ramp-up to 100 VUs in 30 seconds
        { duration: '20', target: 100 },  // Stay at 100 VUs for 1 minute
        { duration: '10', target: 50 },  // Ramp-down to 50 VUs in 30 seconds
        { duration: '10s', target: 0 },   // Ramp-down to 0 VUs in 30 seconds
    ],
};

// Function to test the GET /banque/:id route
export function testGetBanque() {
    let idClient = 1;
    let res = http.get(`http://servicebanque:8081/banque/${idClient}`);
    check(res, {
        'GET /banque/:id status was 200': (r) => r.status === 200,
        'GET /banque/:id status was 404': (r) => r.status === 404,
    });
}

// Function to test POST /banque/debit
export function testPostDebit() {
    let idClient = Math.floor(Math.random() * 80) + 1;
    let valeurDebit = Math.floor(Math.random() * 1000) + 1;
    let payload = JSON.stringify({
        idClient: idClient,
        valeurDebit: valeurDebit,
    });
    let params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    let res = http.post('http://servicebanque:8081/banque/debit', payload, params);
    check(res, {
        'POST /banque/debit status was 200': (r) => r.status === 200,
        'POST /banque/debit status was 400': (r) => r.status === 400,
        'POST /banque/debit status was 404': (r) => r.status === 404,
    });
}

// Function to test POST /banque/depot
export function testPostDepot() {
    let idClient = Math.floor(Math.random() * 80) + 1;
    let valeurDepot = Math.floor(Math.random() * 1000) + 1;
    let payload = JSON.stringify({
        idClient: idClient,
        valeurDepot: valeurDepot,
    });
    let params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    let res = http.post('http://servicebanque:8081/banque/depot', payload, params);
    check(res, {
        'POST /banque/depot status was 200': (r) => r.status === 200,
        'POST /banque/depot status was 404': (r) => r.status === 404,
    });
}

// Function to test POST /banque/credit
export function testPostCredit() {
    let idClient = Math.floor(Math.random() * 80) + 1;
    let valeurCredit = Math.floor(Math.random() * 100) + 1;
    let payload = JSON.stringify({
        idClient: idClient,
        valeurCredit: valeurCredit,
    });
    let params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    let res = http.post('http://servicebanque:8081/banque/credit', payload, params);
    check(res, {
        'POST /banque/credit status was 200': (r) => r.status === 200,
        'POST /banque/credit status was 404': (r) => r.status === 404,
    });
}

// Function to test POST /banque/remboursement
export function testPostRemboursement() {
    let idClient = Math.floor(Math.random() * 80) + 1;
    let valeurRemboursement = Math.floor(Math.random() * 100) + 1;
    let payload = JSON.stringify({
        idClient: idClient,
        valeurRemboursement: valeurRemboursement,
    });
    let params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    let res = http.post('http://servicebanque:8081/banque/remboursement', payload, params);
    check(res, {
        'POST /banque/remboursement status was 200': (r) => r.status === 200,
        'POST /banque/remboursement status was 400': (r) => r.status === 400,
    });
}

export function testGetError() {
    if(Math.floor(Math.random() * 100) === 1){
        let errorResponse = http.get(`http://servicebanque:8081/error`);
        check(errorResponse, {
            'status is 500': (r) => r.status === 500,
        });
    }
}

// Default function to run all tests
export default function () {
    testGetBanque();
    testPostDepot()
    testPostDebit();
    testPostCredit();
    testPostDepot()
    testPostRemboursement();
    testGetError();
    sleep(1); // Sleep for 1 second between requests
}
