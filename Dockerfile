FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY etl_scripts/ ./etl_scripts/
COPY database/ ./database/
COPY utils/ ./utils/
COPY pricing_engine/ ./pricing_engine/
RUN pip install --no-cache-dir -e .
CMD ["python"]