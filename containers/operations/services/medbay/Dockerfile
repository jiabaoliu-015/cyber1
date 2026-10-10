FROM gcc:14-bookworm AS build
WORKDIR /src
COPY route_selector.c .
RUN gcc -std=c11 -Wall -Wextra -Werror -O2 -fno-ident -o artifact3_binary route_selector.c

FROM python:3.12-slim-bookworm
WORKDIR /srv/medbay
COPY --from=build /src/artifact3_binary ./artifact3_binary
COPY app.py app.js index.html ./
RUN chmod 0555 artifact3_binary && chown -R 10001:10001 /srv/medbay
USER 10001:10001
EXPOSE 8080
ENV MEDBAY_BIND=0.0.0.0 MEDBAY_PORT=8080
CMD ["python", "-u", "app.py"]
