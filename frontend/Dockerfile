FROM node:20-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the application
COPY . .

# Set environment to allow Vite to run in Docker
ENV VITE_HOST=0.0.0.0
EXPOSE 5173

CMD ["npm", "run", "dev"]
