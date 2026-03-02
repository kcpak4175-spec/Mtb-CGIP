FROM python:3.10-slim

# OS 레벨 패키지 설치
# libxrender1, libxext6, libfontconfig1: RDKit에 필요
# gcc, g++: 일부 파이썬 패키지 C++ 빌드에 필요
RUN apt-get update && apt-get install -y \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 워크디렉토리 설정
WORKDIR /app

# 파이썬 경로 설정
ENV PYTHONPATH=/app/Mtb_Inhibitor_Web/backend:$PYTHONPATH

# (해당되는 경우) 캐시 최적화를 위해 requirement.txt부터 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 전체 복사
COPY . .

# FastAPI 서버 포트 노출
EXPOSE 8000

# uvicorn으로 서버 실행
CMD ["uvicorn", "Mtb_Inhibitor_Web.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
