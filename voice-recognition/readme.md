# Voice recognition microservice for youtube 

## Build
````shell script
cd voice-recognition
mkdir vosk-model
````

1) Download model file from https://alphacephei.com/vosk/models
3) Extract model from archive to ````vosk-model```` directory
4) Build docker image
````shell script
docker build -t voice-recognition .
````
## Run
````shell script
cd ..
docker-compose up
````

## Endpoint
Schedule recognition
````shell script
http://localhost:8080/voice-recognition/schedule/<vidid>
````
Get result
````shell script
http://localhost:8080/voice-recognition/text/<vidid>
````