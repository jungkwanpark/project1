# 📊 LLM 및 RAG 기반 미국 주식 분석 서비스

## 🖥️ 서버 환경 세팅 (Ubuntu 22.04 기준 예시)

```bash
### Package 업데이트 및 Python 설치 ###
sudo apt update && sudo apt install python3 && sudo apt install python3-pip
python3 --version

### Git 설치 ###
sudo apt install git
git --version

### Git clone 실행 ###
git clone https://github.com/jungkwanpark/project1.git

### 디렉토리 이동 ###
cd project1
ls -la

### 의존성 설치 ###
pip3 install -r requirements.txt

### 환경변수 파일 (.env) 생성 (아래 예시 참조) ###
Example : 
--------------------------------------------------------------
PORT=5000
OPENAI_API_TYPE="azure"
OPENAI_API_MODEL="gpt-4.1"
OPENAI_TEMPERATURE=0.5
AZURE_OPENAI_VERSION="2025-01-01-preview"
AZURE_OPENAI_ENDPOINT="https://your-azure-openai-endpoint"
AZURE_OPENAI_KEY="your-azure-openai-api-key"
AZURE_DEPLOYMENT_ID="gpt-4.1"
AZURE_SEARCH_SERVICE_ENDPOINT="https://your-azure-ai-search-endpoint"
AZURE_SEARCH_INDEX_NAME="your-azure-ai-search-index"
AZURE_SEARCH_API_KEY="your-azure-ai-search-api-key"
--------------------------------------------------------------

### app.py 파일 실행 ###
python3 app.py

```

## 🖥️ 원격 클라이언트에서 서버 접속

```bash
http://your-server-domain:5000
```
