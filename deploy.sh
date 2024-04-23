echo "Input server's url"
read SERVERURL
CONTAINER_NAME=simple_note_container
APP_NAME=simple_note

docker --host tcp://$SERVERURL:2375 stop $CONTAINER_NAME
docker --host tcp://$SERVERURL:2375 rm $CONTAINER_NAME
docker --host tcp://$SERVERURL:2375 image rm $APP_NAME
docker --host tcp://$SERVERURL:2375 buildx build --tag $APP_NAME .
docker --host tcp://$SERVERURL:2375 run --detach --publish 8044:8044 --restart always --name $CONTAINER_NAME $APP_NAME 