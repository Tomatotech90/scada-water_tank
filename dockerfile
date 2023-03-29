# Use the official Ubuntu base image
FROM ubuntu:20.04

# Set environment variables to avoid tzdata interaction
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Update package lists and install essential packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    ca-certificates \
    curl \
    nano \
    wget \
    unzip \
    git \
    nginx \
    php-fpm \
    php-mbstring \
    php-zip \
    php-gd \
    php-json \
    php-curl \
    php-xml \
    tcpdump \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip3 install pymodbus

# Download and install phpMyAdmin
RUN wget https://files.phpmyadmin.net/phpMyAdmin/5.1.3/phpMyAdmin-5.1.3-all-languages.zip && \
    unzip phpMyAdmin-5.1.3-all-languages.zip && \
    mv phpMyAdmin-5.1.3-all-languages /var/www/phpmyadmin && \
    rm phpMyAdmin-5.1.3-all-languages.zip

# Remove the default Nginx configuration
RUN rm /etc/nginx/sites-enabled/default

# Create a new Nginx configuration file
RUN echo "server { \
  listen 80; \
  root /app; \
  index index.php index.html; \
  server_name _; \
  location / { \
    try_files \$uri \$uri/ =404; \
  } \
  location ~ \.php$ { \
    include snippets/fastcgi-php.conf; \
    fastcgi_pass unix:/var/run/php/php7.4-fpm.sock; \
  } \
} \
server { \
  listen 69; \
  root /var/www/phpmyadmin; \
  index index.php index.html; \
  server_name _; \
  location / { \
    try_files \$uri \$uri/ =404; \
  } \
  location ~ \.php$ { \
    include snippets/fastcgi-php.conf; \
    fastcgi_pass unix:/var/run/php/php7.4-fpm.sock; \
  } \
}" > /etc/nginx/sites-available/app

# Enable the new Nginx configuration
RUN ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled/

# Set the working directory
WORKDIR /app

# Copy the login.php file from your local project directory into the container
COPY ./login.php /app/login.php

# Copy the dashboard.html file from your local project directory into the container
COPY ./dashboard.html /app/dashboard.html

# Copy the app.py file from your local project directory into the container
COPY ./app.py /app/app.py

# Copy the modbus_server.py file from your local project directory into the container
COPY ./modbus_server.py /app/modbus_server.py

# Create a script to start all services
RUN echo "#!/bin/bash\n\
service php7.4-fpm start\n\
nginx -g 'daemon off;' &\n\
tcpdump -i any -w /app/tcpdump.pcap &\n\
python3 /app/modbus_server.py &\n\
python3 /app/app.py" > /start_services.sh

# Make the script executable
RUN chmod +x /start_services.sh

# Expose ports 80, 69, 502, and 5000
EXPOSE 80 69 502 5000
# Start Nginx, PHP-FPM, and tcpdump on container start
CMD ["/start_services.sh"]
