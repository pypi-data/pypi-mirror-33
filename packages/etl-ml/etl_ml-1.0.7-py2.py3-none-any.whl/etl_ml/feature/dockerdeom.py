import  docker


client = docker.from_env()

#print(client.version())

client.containers.run("ubuntu:latest", "echo hello world")