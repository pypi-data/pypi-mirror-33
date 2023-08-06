Quickstart
^^^^^^^^^
Install serviceultra-cmd from PyPI:
::

    pip install serviceultra-ctl

Usage
^^^^^^^^^^
1.login
login serviceultra by:
::

    suctl login -u[--username] xxx -p[--password] xxx -d[--domain] huayun.com/bigdata.com -a[--address] 10.10.10.10:8080 -s[--security] http/https -l[--language] en/ch


or
::

    suctl login

If none is specified, linux system will check /etc/dataultractl/os-verify and windows check C:/dataultractl/os-verify
The file will be like:
::

    [verify]
    username=xxx
    password=xxx
    domain=xxx
    address=xxx
    security=xxx
    language=xxx

#.logout
logout dataultra by:
::

    suctl logout

#.ls
list cluster/machine/application/serice/task/microservice/instance info by:
::

    suctl ls cluster [--clusterid xxx] [-f]
    suctl ls machine [--machineid xxx] [-f]
    suctl ls application [--appid xxx] [-f]
    suctl ls service --appid xxx [-f]
    suctl ls task --appid xxx [-f]
    suctl ls microservice --serviceid xxx [-f]
    suctl ls instance --serviceid xxx [--instanceid xxxx -t/-l] [-f]

#.statistics
statistics cluster/machine/application/microservice info by:
::

    suctl statistics cluster [--clusterid xxx] [-f]
    suctl statistics machine [-f]
    suctl statistics application [--appid xxx] [-f]
    suctl statistics microservice --serviceid xxx [-f]

#.deploy
deploy service/machine/task by:
::

    suctl deploy service --serviceid xxx --appid xxx
    suctl deploy machine --machineid xxx --clusterid xxx
    suctl deploy task --taskid xxx --appid xxx

#.undeploy
undeploy service/machine/instance/task by:
::

    suctl undeploy service --serviceid xxx --appid xxx
    suctl undeploy machine --machineid xxx --clusterid xxx
    suctl undeploy instance --serviceid xxx --microserviceid xxx --instanceid xxx
    suctl undeploy task --taskid xxx --appid xxx

#.start
start task by:
::

    suctl start task --taskid xxx --appid xxx

#.stop
stop task by:
::

    suctl stop task --taskid xxx --appid xxx

#.delete
delete cluster/machine/application/service/task/microservice/instance by:
::

    suctl delete cluster --clusterid xxx
    suctl delete machine --machineid xxx
    suctl delete application --appid xxx
    suctl delete service --serviceid xxx --appid xxx
    suctl delete task --taskid xxx --appid xxx
    suctl delete microservice --microserviceid xxx --serviceid xxx
    suctl delete instance --serviceid xxx --microserviceid xxx --instanceid xxx

#.remove
remove machine from cluster, by:
::

    suctl remove machine --machineid xxx --clusterid xxx

#.add
add machine to cluster, by:
::

    suctl add machine --machineid xxx ---clusterid xxx




