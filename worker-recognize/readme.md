# worker-recognize

## Build
````shell script
cd worker-recognize
mkdir vosk-model
````

1) Download model file from https://alphacephei.com/vosk/models
3) Extract model from archive to ````vosk-model```` directory
4) Build docker image
````shell script
docker build -t worker-recognize .
````
## Run
````shell script
cd ..
docker-compose up
````