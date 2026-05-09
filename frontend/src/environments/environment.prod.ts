export const environment = {
  production: true,
  // When serving frontend and backend from the same host, leave apiUrl empty
  // so all API calls go to the same origin (e.g. http://YOUR_SERVER_IP:8000)
  // Change this to your actual server IP or domain before building for production:
  // e.g. apiUrl: 'http://192.168.1.100:8000'  (LAN)
  // e.g. apiUrl: 'https://mi-dominio.com/api'  (Internet)
  apiUrl: 'http://localhost:8000'
};
