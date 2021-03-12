---
title: Running PhiloLogic in Docker
---

You can run PhiloLogic with the prebuilt Docker image available on DockerHub. 


- Download Docker image from DockerHub:
```bash
docker pull artfl/philologic
```
- Create a directory on your host system to store the PhiloLogic databases. E.g.:
```bash
mkdir ~/philologic
```
- When you start the container, you will need to mount your local philologic directory in the docker image. Run the following command to start a container:
```bash
docker run -td -p 80:80 -v /PATH/TO/PHILOLOGIC_DIR:/var/www/html/philologic/ artfl/philologic
```
- You will need to enter the container shell to load PhiloLogic databases:
```bash
docker exec -it CONTAINER_NAME /bin/bash
```


### NOTES ###
- The Docker image is designed to listen to connections on port 80. Adjust according to your needs 
- If you need to run this under https, you will need to configure the Apache webserver for that purpose.
