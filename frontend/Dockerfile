FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm i
COPY . .
RUN npm run build
CMD [ "npm", "run", "build" ]

FROM node:20-alpine AS production
WORKDIR /app
COPY --from=build /app/package.json ./
RUN npm i 
COPY --from=build /app/dist ./dist