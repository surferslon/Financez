FROM node:14.9.0 AS build-step

WORKDIR /build
ENV PATH /build/node_modules/.bin:$PATH
COPY package.json package-lock.json ./
RUN npm install

COPY . ./
RUN npm run build

FROM nginx:1.18-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-step /build/build /usr/share/nginx/html
