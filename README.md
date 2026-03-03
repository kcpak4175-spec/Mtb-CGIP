# Mtb-Inhibitor Finder AI
**Mtb 저해제 발굴 AI 플랫폼**
write. kcpak

Mtb-Inhibitor Finder AI는 딥러닝 기반의 화합물 스크리닝 플랫폼으로, 결핵균(Mtb)의 필수 대사 과정에 관여하는 13개 클러스터에 대한 화합물의 저해 활성을 예측합니다. 화학 정보학(Cheminformatics)과 AI 기술을 결합하여 신약 개발 초기 단계의 효율성을 극대화합니다.

🔗 [Live Demo 보러가기](https://kcpak4175-spec-mtb-cgip.hf.space)

🚀 기술 스택 (Tech Stack)
- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Vanilla HTML5, JavaScript (ES6+), Tailwind CSS
- **AI/ML Engine**: PyTorch, Chemprop (DMPNN), RDKit (Cheminformatics)
- **Data Visualization**: Plotly.js
- **Environment**: Docker
- **Deployment**: Hugging Face Spaces (16GB RAM Optimized)

✨ 주요 기능 (Key Features)
### 화합물 스크리닝 및 AI 예측 (AI Prediction)
- **대량 스크리닝**: CSV 파일 업로드 기능을 통해 다수의 화합물을 한 번에 분석
- **개별 분석**: SMILES 코드를 직접 입력하여 즉각적인 AI 분석 실행
- **멀티 태스크 예측**: 13개 필수 클러스터(C1~C13)에 대한 저해 확률 산출 (DMPNN 앙상블 모델 적용)

### 시각화 및 데이터 분석 (Visualization)
- **Radar Chart**: 화합물의 클러스터별 저해 프로파일을 직관적인 레이더 차트로 시각화
- **분자 구조 렌더링**: RDKit을 활용한 화합물의 2D 구조화면 자동 생성
- **약물성 지표 계산**: 분자량(MW), LogP, TPSA, HBD, HBA 등 주요 약물성 지표 자동 계산 및 Lipinski's Rule 평가

### 리포트 관리 및 공유
- **결과 요약 리포트**: Hit Count 기반의 전문가 요약 코멘트 자동 생성
- **데이터 내보내기**: 분석 결과를 Excel(XLSX) 및 CSV 형식으로 다운로드 지원
- **실시간 상태 모니터링**: AI 모델 로딩 및 시스템 상태 실시간 업데이트

💻 로컬 개발 환경 설정 (Getting Started)
프로젝트를 로컬 환경에서 실행하려면 다음 단계를 따르세요.

1. 레포지토리 클론
```bash
git clone https://github.com/kcpak4175-spec/Mtb-CGIP.git
cd Mtb-CGIP
```

2. 가상환경 생성 및 패키지 설치
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 학습된 모델 확인
`Results/Trained_model/DMPNN_RN_Ensemble_5/fold_0/` 경로에 모델 파일(`model.pt`)들이 있는지 확인합니다.

4. 백엔드 서버 실행
```bash
python Mtb_Inhibitor_Web/backend/main.py
```
브라우저에서 `http://localhost:7860` 접속하여 플랫폼을 확인합니다. (또는 기본 포트 8000 사용 시 포트 설정 확인)

🌐 배포 가이드 (Deployment)
이 프로젝트는 **Hugging Face Spaces (Docker)** 환경에 최적화되어 있습니다. 메모리 사양이 높은 환경(최소 16GB RAM)을 권장합니다.

1. Hugging Face에서 새 Space를 생성하고 SDK로 **Docker**를 선택합니다.
2. `Dockerfile`의 포트 설정이 `7860`으로 되어 있는지 확인합니다. (Hugging Face 기본 사양)
3. 파일들을 업로드하거나 GitHub 저장소를 연동합니다.
4. 빌드가 완료되면 `https://[your-space-name].hf.space` 주소로 배포됩니다.

> [!IMPORTANT]
> **메모리 관련 주의사항**: 이 프로젝트는 5개의 딥러닝 모델을 동시에 메모리에 로드하므로, 최소 8GB 이상의 RAM이 필요합니다. Hugging Face의 무료 CPU 기본 티어(16GB)에서 가장 안정적으로 구동됩니다.
