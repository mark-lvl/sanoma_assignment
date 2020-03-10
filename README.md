Setup Instruction
---

If you have the docker already install in your test machine, simply run the following command in the route of the project to build the docker image and running the container.

`$ docker-compose up`

In order to run the script, attach to your running container (by assuming you already followed previous step), by running

`docker run -it sanoma_script /bin/bash`

navigate to app directory:

`cd app`

and finally run the python script by proving the task argument as shown in below:

for running first task and calling the api:
`python assignment.py -t task_1`

for running second task and seeing the average arrival time:
`python assignment.py -t task_2`

**Notes**

* If docker has been used for installing the application, there is no need to install dependencies manually since they all been installed within the container.
