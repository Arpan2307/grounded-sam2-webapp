FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Set environment variable
ENV NODE_ENV=production
ENV REACT_APP_API_BASE_URL=http://localhost:5000

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
