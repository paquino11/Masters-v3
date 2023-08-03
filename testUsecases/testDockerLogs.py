import docker
from flask import Flask, render_template_string, Markup

app = Flask(__name__)

@app.route('/')
def container_logs():
    # Connect to the Docker daemon using the docker-py library
    client = docker.from_env()

    container_name = "fabric-gateway"  # Replace with the name of your container
    container = client.containers.get(container_name)

    # Fetch the logs of the container (limit to last 1000 lines in this example)
    logs = container.logs(tail=1000, stream=False, timestamps=True)

    # Format logs for better readability and indentation
    formatted_logs = logs.decode().replace('\n', '\n<br>')
    formatted_logs = Markup('<pre>{}</pre>'.format(formatted_logs))

    return render_template_string('{{ logs }}', logs=formatted_logs)


if __name__ == '__main__':
    app.debug = True  # Enable debug mode
    app.run()
