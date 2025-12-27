# Stage 1: Build stage
FROM python:3.14-slim AS builder

WORKDIR /code

COPY ./requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final stage
FROM python:3.14-slim

WORKDIR /code

# Copy only the installed packages from the builder stage
COPY --from=builder /root/.local /root/.local
COPY ./app /code/app

# Update PATH to include the user-installed binaries
ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]