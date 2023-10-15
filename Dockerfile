FROM python:3-alpine
ARG BIN_VERSION=<unknown>

RUN mkdir /app
COPY ./*.py ./requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
ENTRYPOINT ["python", "/app/feedbin_stars.py"]

LABEL license="MIT"
LABEL maintainer="Chris Dzombak <https://www.dzombak.com>"
LABEL org.opencontainers.image.authors="Chris Dzombak <https://www.dzombak.com>"
LABEL org.opencontainers.image.url="https://github.com/cdzombak/feedbin-stars-to-email"
LABEL org.opencontainers.image.documentation="https://github.com/cdzombak/feedbin-stars-to-email/blob/main/README.md"
LABEL org.opencontainers.image.source="https://github.com/cdzombak/feedbin-stars-to-email.git"
LABEL org.opencontainers.image.version="${BIN_VERSION}"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="feedbin-stars-to-email"
LABEL org.opencontainers.image.description="Email starred items from your Feedbin account to a chosen email address"
