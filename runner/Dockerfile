# Operator builds this image; execution accepts only its resolved sha256 image ID.
FROM python:3.12.14-slim
RUN pip install --no-cache-dir pytest==9.2.0
COPY harness.py /opt/codepilot/harness.py
RUN mkdir /source && chmod 755 /source
USER 65534:65534
ENTRYPOINT ["python", "-I", "/opt/codepilot/harness.py"]
