# Operator builds this image; execution accepts only its resolved sha256 image ID.
FROM python:3.12.14-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f
COPY requirements.txt /opt/codepilot/requirements.txt
RUN pip install --no-cache-dir -r /opt/codepilot/requirements.txt
COPY harness.py /opt/codepilot/harness.py
RUN mkdir /source && chmod 755 /source
USER 65534:65534
ENTRYPOINT ["python", "-I", "/opt/codepilot/harness.py"]
