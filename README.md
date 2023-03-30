# Project Name

This project demonstrates how to run a Flask web application and a Modbus server inside a Docker container.

## Getting Started

### Prerequisites

- Docker

### Building the Docker Image

1. Clone this repository.
2. Navigate to the root directory of the project.
3. Build the Docker image with the following command:

docker build -t my-app-image .

bash


### Running the Docker Container

1. Run the Docker container with the following command:

docker run -d -i -t --privileged -p 80:80 -p 69:69 -p 502:502 -p 5000 --name my-app-container my-app-image

markdown

- The `-d` flag runs the container in the background.
- The `-i` flag keeps stdin open even if not attached.
- The `-t` flag allocates a pseudo-TTY.
- The `--privileged` flag gives extended privileges to this container.
- The `-p` flags map the container's ports to the host machine's ports.
- The `--name` flag gives a name to the container.

2. Access the web application by navigating to `http://localhost` in your web browser.

### Stopping the Docker Container

1. Stop the Docker container with the following command:

docker stop my-app-container

bash


2. Remove the Docker container with the following command:

docker rm my-app-container

markdown


## Authors

- ketchup- 
## Acknowledgments

- [Flask documentation](https://flask.palletsprojects.com/en/2.1.x/)
- [pymodbus documentation](https://pymodbus.readthedocs.io/en/latest/)
