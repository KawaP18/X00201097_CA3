import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 3,
  duration: '10s',
};

export default function () {
  const response = http.get('https://example.com');

  check(response, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
