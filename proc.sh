CONTAINER_NAME=study_container
APP_NAME=study

#developing environment
#pipreqs . --encoding=utf-8 --force

docker --host tcp://$SERVERURL:2375 stop $CONTAINER_NAME
docker --host tcp://$SERVERURL:2375 rm $CONTAINER_NAME
docker --host tcp://$SERVERURL:2375 image rm $APP_NAME
docker --host tcp://$SERVERURL:2375 buildx build --tag $APP_NAME .
docker --host tcp://$SERVERURL:2375 run --detach --publish 8044:8044 --restart always --env TZ=$MYTIMEZONE --name $CONTAINER_NAME $APP_NAME 