FROM broken-base-local
RUN depthflow load-model
CMD /bin/bash /App/Docker/Scripts/main.sh depthflow
