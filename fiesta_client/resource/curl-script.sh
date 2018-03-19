
# export PROJECT_PATH 
cd $PROJECT_PATH
curl -X POST  -H "iPlanetDirectoryPro: $(cat fiesta-token.json)" -H 'Accept: application/json' -H 'Content-Type: text/plain' --data "$(cat fiesta-client/resource/example.sparql)" https://playground.fiesta-iot.eu/iot-registry/api/queries/execute/global

