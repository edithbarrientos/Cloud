FROM nginx:alpine

# Copiar todos tus archivos estáticos al directorio por defecto de Nginx
COPY index.html app.js style.css /usr/share/nginx/html/
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
