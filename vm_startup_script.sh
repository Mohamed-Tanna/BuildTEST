#!bin/bash
vm_name=$(curl "http://metadata.google.internal/computeMetadata/v1/instance/name" -H "Metadata-Flavor: Google")
commit_SHA=$(gcloud compute instances describe $vm_name --format='value(metadata.items.commit-SHA)' --zone=us-west1-a)
# update package index
apt-get update 
echo y
# install Docker
apt-get install docker.io -y
echo y
apt-get install docker-compose -y
echo y
cd root
# Create the docker-compose.yaml file
echo "version: '3'" > docker-compose.yaml

# Add a service to the file
echo "services:" >> docker-compose.yaml
echo "  app:" >> docker-compose.yaml
echo "    restart: always" >> docker-compose.yaml
echo "    command: ./startup.sh" >> docker-compose.yaml
echo "    container_name: backend" >> docker-compose.yaml
echo "    image: \${IMAGE_1}" >> docker-compose.yaml
echo "    volumes:">>docker-compose.yaml
echo "      - static_volume:/code/static" >> docker-compose.yaml
echo "    expose:" >> docker-compose.yaml
echo "      - '8000'">> docker-compose.yaml
echo "    environment:" >> docker-compose.yaml
echo "      - PROJ_ID=freightslayer-staging" >> docker-compose.yaml
echo "      - ENV=STAGING" >> docker-compose.yaml
echo "      - EMAIL_HOST_USER=notifications@freightslayer.com" >> docker-compose.yaml
echo "      - FMCSA_WEBKEY=WEBKEY" >> docker-compose.yaml
echo "      - SECRET_KEY=D_SECRET_KEY" >> docker-compose.yaml
echo "      - EMAIL_HOST_PASS=EMAIL_HOST_PASSWORD" >> docker-compose.yaml
echo "      - DB_CONNECTION_NAME=CONNECTION_NAME" >> docker-compose.yaml
echo "      - DB_NAME=DATABASE_NAME" >> docker-compose.yaml
echo "      - DB_USER=DATABASE_USER" >> docker-compose.yaml
echo "      - DB_PASS=DB_PASS" >> docker-compose.yaml
echo "      - DB_IP=DATABASE_IP" >> docker-compose.yaml
echo "      - RED_IP=RED_IP" >> docker-compose.yaml
echo "  nginx:" >> docker-compose.yaml
echo "    restart: always" >> docker-compose.yaml
echo "    volumes:">>docker-compose.yaml
echo "      - static_volume:/code/static">>docker-compose.yaml
echo "    image: \${IMAGE_2}" >> docker-compose.yaml
echo "    container_name: nginx" >> docker-compose.yaml
echo "    ports:" >> docker-compose.yaml
echo "      - '80:80'" >> docker-compose.yaml
echo "    depends_on:" >>docker-compose.yaml
echo "      - app" >> docker-compose.yaml
echo "volumes:">> docker-compose.yaml
echo "  static_volume:" >> docker-compose.yaml
gcloud auth configure-docker \
    us-west1-docker.pkg.dev
echo y

IMAGE_1=us-west1-docker.pkg.dev/freightslayer-staging/backend/backend:$commit_SHA 
IMAGE_2=us-west1-docker.pkg.dev/freightslayer-staging/nginx/backend-nginx:$commit_SHA
export IMAGE_1
export IMAGE_2
docker-compose up -d