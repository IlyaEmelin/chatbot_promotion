FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm i
COPY . .

ARG VITE_API_URL
ARG REACT_APP_DEBUG

ENV VITE_API_URL=$VITE_API_URL
ENV REACT_APP_DEBUG=$REACT_APP_DEBUG

RUN npm run build
CMD [ "npm", "run", "build" ]

FROM node:20-alpine AS production
WORKDIR /app
COPY --from=build /app/package.json ./
RUN npm i 
COPY --from=build /app/dist ./dist