FROM node:20-alpine AS build
WORKDIR /usr/www/frontend
COPY package.json ./
RUN npm i
COPY . .
RUN npm run build
CMD [ "npm", "run", "preview" ]

FROM node:20-alpine AS production
WORKDIR /usr/www/frontend
COPY --from=build /usr/www/frontend/package.json ./
RUN npm i 
COPY --from=build /usr/www/frontend/dist ./dist