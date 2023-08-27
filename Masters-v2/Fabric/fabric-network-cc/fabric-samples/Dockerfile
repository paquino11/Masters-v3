# Use a base Node.js image
FROM node:18

# Set the working directory in the container
WORKDIR /app

COPY . .

RUN cd asset-transfer-basic/application-gateway-typescript/ && npm install


EXPOSE 3025

#ENTRYPOINT ["tail", "-f", "/dev/null"]

CMD ["sh", "-c", "cd asset-transfer-basic/application-gateway-typescript/ && npm start"]
