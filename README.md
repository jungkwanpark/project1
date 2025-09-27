LLM 및 RAG 기반 미국 주식 분석 서비스 

서버 환경 세팅 (Ubuntu 22.04)

### Apt update -> Install python3 packages ###
sudo apt update && sudo apt install python3 && sudo apt install python3-pip
python3 --version

### Install git ###
sudo apt install git
git --version

### Git clone ###
git clone https://github.com/jungkwanpark/project1.git

### Change directory ###
cd project1
ls -la

### Install dependencies ###
pip3 install -r requirements.txt

### Create environment (.env) file as below example ###
Example : 
--------------------------------------------------------------
PORT=5000
OPENAI_API_TYPE="azure"
OPENAI_API_MODEL="gpt-4.1"
OPENAI_TEMPERATURE=0.5
AZURE_OPENAI_VERSION="2025-01-01-preview"
AZURE_OPENAI_ENDPOINT="https://your-azure-openai-endpoint"
AZURE_OPENAI_KEY="your-azure-ai-openai-api-key"
AZURE_DEPLOYMENT_ID="gpt-4.1"
AZURE_SEARCH_SERVICE_ENDPOINT="https://your-azure-ai-search-endpoint"
AZURE_SEARCH_INDEX_NAME="your-azure-ai-search-index"
AZURE_SEARCH_API_KEY="your-azure-ai-search-api-key"
--------------------------------------------------------------

### Implement app.py ###
python3 app.py


### From your local browser, access to your server as below ###
http://your-server-domain:5000



