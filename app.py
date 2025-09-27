import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>주식 분석</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Noto Sans KR', sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #f8f9fa;
            color: #343a40;
            line-height: 1.6;
        }
        .container {
            background-color: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        h1 {
            color: #1a73e8;
            font-weight: 700;
            margin-bottom: 30px;
            font-size: 2.2em;
        }
        h2 {
            color: #202124;
            font-weight: 500;
            margin-top: 30px;
            font-size: 1.5em;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
        }
        h3 {
            color: #202124;
            font-weight: 500;
            margin-top: 25px;
            font-size: 1.2em;
        }
        .input-group {
            margin-bottom: 30px;
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            padding: 12px 16px;
            width: 250px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.2s;
            font-family: 'Noto Sans KR', sans-serif;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #1a73e8;
        }
        button {
            padding: 12px 24px;
            background-color: #1a73e8;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: background-color 0.2s;
            font-family: 'Noto Sans KR', sans-serif;
        }
        button:hover {
            background-color: #1557b0;
        }
        .loading {
            display: none;
            margin-top: 20px;
            color: #5f6368;
            font-weight: 500;
        }
        #result {
            margin-top: 30px;
            white-space: pre-wrap;
            line-height: 1.8;
        }
        .analysis-section {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .chart-container {
            margin-top: 30px;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        pre {
            font-family: 'Noto Sans KR', sans-serif;
            white-space: pre-wrap;
            word-wrap: break-word;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 0.95em;
            line-height: 1.7;
        }
        .search-container {
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }
        .search-results {
            margin-top: 20px;
            padding: 15px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>미국 주식 종목 분석 서비스</h1>
        <div class="input-group">
            <input type="text" id="ticker" placeholder="종목 코드 입력 (예: AAPL)">
            <button onclick="analyzeStock()">분석하기</button>
        </div>
        <div class="loading" id="loading">분석 중입니다. 잠시만 기다려주세요...</div>
        <div id="result"></div>
    </div>

    <script>
        function analyzeStock() {
            const ticker = document.getElementById('ticker').value;
            if (!ticker) {
                alert('종목 코드를 입력해주세요');
                return;
            }

            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').innerHTML = '';

            fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ticker: ticker })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                if (data.error) {
                    document.getElementById('result').innerHTML = `<div class="analysis-section">오류: ${data.error}</div>`;
                } else {
                    let resultHtml = `<h2>${data.ticker} 종목 분석 결과</h2>`;
                    resultHtml += `<div class="analysis-section"><pre>${data.analysis}</pre></div>`;
                    
                    // Display charts if available
                    if (data.data.charts) {
                        if (data.data.charts.income_statement) {
                            resultHtml += `<div class="chart-container"><h3>손익계산서 추이</h3><div id="income_chart"></div></div>`;
                            const incomeChart = JSON.parse(data.data.charts.income_statement);
                            Plotly.newPlot('income_chart', incomeChart.data, incomeChart.layout);
                        }
                        if (data.data.charts.cash_flow) {
                            resultHtml += `<div class="chart-container"><h3>현금흐름 추이</h3><div id="cashflow_chart"></div></div>`;
                            const cashFlowChart = JSON.parse(data.data.charts.cash_flow);
                            Plotly.newPlot('cashflow_chart', cashFlowChart.data, cashFlowChart.layout);
                        }
                        if (data.data.charts.balance_sheet) {
                            resultHtml += `<div class="chart-container"><h3>재무상태표 추이</h3><div id="balance_chart"></div></div>`;
                            const balanceChart = JSON.parse(data.data.charts.balance_sheet);
                            Plotly.newPlot('balance_chart', balanceChart.data, balanceChart.layout);
                        }
                    }
                    
                    document.getElementById('result').innerHTML = resultHtml;
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').innerHTML = `<div class="analysis-section">오류: ${error.message}</div>`;
            });
        }
    </script>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</body>
</html>
"""

# Initialize Azure OpenAI
azure_openai = AzureChatOpenAI(
    openai_api_type="azure",
    openai_api_version=os.getenv("AZURE_OPENAI_VERSION"),
    openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
    deployment_name=os.getenv("AZURE_DEPLOYMENT_ID"),
    temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.5))
)

def setup_selenium():
    try:
        # Try Firefox first
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from webdriver_manager.firefox import GeckoDriverManager
        
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=firefox_options)
    except Exception as e:
        print(f"Failed to initialize Firefox: {str(e)}")
        
        # If Firefox fails, try Chrome
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            from webdriver_manager.chrome import ChromeDriverManager
            from webdriver_manager.core.utils import ChromeType
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            return webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Failed to initialize Chrome: {str(e)}")
            raise Exception("Failed to initialize any web driver")

def get_finviz_data(ticker):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'lxml')
        
        pe_element = soup.find('td', string='P/E')
        if pe_element:
            pe_ratio = pe_element.find_next_sibling('td').text
            return {"P/E": pe_ratio}
        return {"P/E": "N/A"}
    except Exception as e:
        print(f"Error fetching Finviz data: {str(e)}")
        return {"P/E": "N/A"}

def get_naver_finance_data(ticker):
    base_url = f"https://m.stock.naver.com/worldstock/stock/{ticker}.O/finance"
    
    # Initialize Selenium with retry mechanism
    max_retries = 3
    retry_count = 0
    driver = None
    
    while retry_count < max_retries:
        try:
            driver = setup_selenium()
            break
        except Exception as e:
            retry_count += 1
            print(f"Attempt {retry_count} failed: {str(e)}")
            if retry_count == max_retries:
                return {
                    "income_statement": {"error": "Failed to initialize web driver"},
                    "cash_flow": {"error": "Failed to initialize web driver"},
                    "balance_sheet": {"error": "Failed to initialize web driver"}
                }
            time.sleep(2)
    
    try:
        # Initialize empty data structures
        income_data = {
            "revenue": [],
            "operating_income": [],
            "net_income": [],
            "years": []
        }
        
        cash_flow_data = {
            "operating_cash_flow": [],
            "years": []
        }
        
        balance_sheet_data = {
            "total_assets": [],
            "total_liabilities": [],
            "total_equity": [],
            "years": [],
            "debt_to_equity": None
        }

        # Get Income Statement Data
        try:
            driver.get(f"{base_url}/income/annual")
            time.sleep(10)  # Increased wait time
            
            # Wait for any table element to appear
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            
            # Try different class names for the table rows
            row_classes = ["VTableRow_row__DYUj1", "row", "table-row"]
            rows = []
            for class_name in row_classes:
                try:
                    rows = driver.find_elements(By.CLASS_NAME, class_name)
                    if rows:
                        break
                except:
                    continue
            
            if rows:
                # Extract years from table headers
                header_elements = driver.find_elements(By.CSS_SELECTOR, "th, td.header")
                income_data["years"] = [el.text.strip() for el in header_elements[1:] if el.text.strip()]
                
                # Extract financial data
                for row in rows:
                    try:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if not cells:
                            continue
                        
                        label = cells[0].text.strip()
                        values = [cell.text.strip() for cell in cells[1:]]
                        
                        if "매출액" in label or "Revenue" in label:
                            income_data["revenue"] = values
                        elif "영업이익" in label or "Operating Income" in label:
                            income_data["operating_income"] = values
                        elif "당기순이익" in label or "Net Income" in label:
                            income_data["net_income"] = values
                    except:
                        continue
        except Exception as e:
            print(f"Error fetching income statement: {str(e)}")

        # Similar updates for cash flow and balance sheet data...
        # [Previous implementation continues here]

        return {
            "income_statement": income_data,
            "cash_flow": cash_flow_data,
            "balance_sheet": balance_sheet_data
        }
    
    except Exception as e:
        print(f"Error in get_naver_finance_data: {str(e)}")
        return {
            "income_statement": {"error": str(e)},
            "cash_flow": {"error": str(e)},
            "balance_sheet": {"error": str(e)}
        }
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def analyze_stock_data(ticker, all_data):
    # First, search for relevant documents
    try:
        search_results = search_azure_ai(ticker)
    except Exception as e:
        print(f"문서 검색 중 오류 발생: {str(e)}")
        search_results = "관련 리포트를 찾을 수 없습니다."

    system_prompt = """당신은 전문적인 주식 분석 AI로, 주어진 데이터를 바탕으로 종합적인 투자 분석을 제공합니다.
    
    다음 항목들에 대해 상세한 분석을 제공해주세요:
    
    1. 밸류에이션 분석
    - P/E(주가수익비율) 분석
    - 현재 주가의 적정성 평가
    - 동종 업계 평균과의 비교 (가능한 경우)
    
    2. 재무건전성 분석
    - 손익계산서: 매출, 영업이익, 순이익 추세 분석
    - 현금흐름표: 영업활동 현금흐름 추세 분석
    - 대차대조표: 부채비율, 자본구조 분석
    
    3. 종합 투자의견
    - 강점과 기회요인
    - 약점과 위험요인
    - 투자 추천 등급 (매수/중립/매도)
    - 단기 및 중장기 전망
    
    4. 증권사 리포트 분석 자료 요약
    - 제공된 증권사 리포트 내용을 바탕으로 주요 분석 의견 요약
    - 투자의견과 목표가격 동향
    - 주요 이슈 및 전망
    
    분석은 객관적 사실에 기반하여 구체적인 수치를 포함해야 하며, 
    위험요인과 기회요인을 균형있게 다루어야 합니다.
    
    응답 형식:
    1. 요약
    2. 상세 분석 (각 항목별)
    3. 투자 포인트 (긍정/부정)
    4. 최종 투자의견
    5. 증권사 리포트 분석 자료 요약
        
    마지막에 반드시 아래와 같이 데이터 출처 링크를 명확히 표기하세요:
    @https://finviz.com/quote.ashx?t={ticker}
    @https://m.stock.naver.com/worldstock/stock/{ticker}.O/finance
    """


    data_str = json.dumps(all_data, indent=2)
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"{ticker} 종목에 대해 제공된 데이터를 기반으로 분석해주세요.\n\n데이터:\n{data_str}\n\n증권사 리포트 내용:\n{search_results}")
    ]
    
    response = azure_openai.generate([messages])
    return response.generations[0][0].text

def create_financial_charts(naver_data):
    charts = {}
    
    try:
        # Income Statement Chart
        income_data = naver_data.get("income_statement", {})
        if isinstance(income_data, dict) and "years" in income_data and income_data["years"]:
            try:
                fig = go.Figure()
                
                # Convert string values to numbers safely
                years = income_data["years"]
                revenue = [float(str(x).replace(',', '')) if x and str(x).strip() != '' else 0 for x in income_data.get("revenue", [])]
                operating_income = [float(str(x).replace(',', '')) if x and str(x).strip() != '' else 0 for x in income_data.get("operating_income", [])]
                net_income = [float(str(x).replace(',', '')) if x and str(x).strip() != '' else 0 for x in income_data.get("net_income", [])]
                
                # Add traces only if we have data
                if len(years) == len(revenue) and revenue:
                    fig.add_trace(go.Bar(x=years, y=revenue, name="Revenue"))
                if len(years) == len(operating_income) and operating_income:
                    fig.add_trace(go.Bar(x=years, y=operating_income, name="Operating Income"))
                if len(years) == len(net_income) and net_income:
                    fig.add_trace(go.Bar(x=years, y=net_income, name="Net Income"))
                
                # Update layout
                fig.update_layout(
                    title="Income Statement Trends",
                    barmode='group',
                    xaxis_title="Year",
                    yaxis_title="Amount",
                    template="plotly_white"
                )
                
                charts["income_statement"] = fig.to_json()
            except Exception as e:
                print(f"Error creating income statement chart: {str(e)}")
        
        # Similar updates for cash flow and balance sheet charts...
        # [Previous implementation continues here]
    
    except Exception as e:
        print(f"Error in create_financial_charts: {str(e)}")
    
    return charts

def search_azure_ai(query):
    search_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    
    print(f"Searching for: {query}")
    print(f"Search endpoint: {search_endpoint}")
    print(f"Index name: {index_name}")
    print(f"API key exists: {'Yes' if api_key else 'No'}")
    
    if not all([search_endpoint, index_name, api_key]):
        print("Missing required Azure Search configuration")
        return "Azure Search 설정이 완료되지 않았습니다."
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    url = f"{search_endpoint}/indexes/{index_name}/docs/search?api-version=2024-07-01"
    
    payload = {
        "search": query,
        "count": True,
        "queryType": "full",
        "searchMode": "all",
        "top": 5  # Limit to top 5 most relevant results
    }
    
    try:
        print(f"Making request to: {url}")
        response = requests.post(url, headers=headers, json=payload)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return f"검색 API 호출 실패: {response.status_code}"
        
        results = response.json()
        print(f"Number of results: {len(results.get('value', []))}")
        
        if not results.get('value'):
            return "검색된 리포트가 없습니다."
        
        # Join the content with clear separators
        content_list = []
        for doc in results.get('value', []):
            content = doc.get('content', '').strip()
            if content:
                content_list.append(f"--- 리포트 내용 ---\n{content}\n")
        
        return "\n".join(content_list) if content_list else "검색된 리포트가 없습니다."
        
    except Exception as e:
        print(f"Error in search_azure_ai: {str(e)}")
        return f"검색 중 오류 발생: {str(e)}"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze_stock():
    data = request.get_json()
    ticker = data.get('ticker')
    
    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400
    
    try:
        # Gather data from all sources
        finviz_data = get_finviz_data(ticker)
        naver_data = get_naver_finance_data(ticker)
        
        # Create charts only if we have valid data
        charts = {}
        if isinstance(naver_data, dict) and not any("error" in v for v in naver_data.values()):
            charts = create_financial_charts(naver_data)
        
        all_data = {
            "finviz": finviz_data,
            "naver_finance": naver_data,
            "charts": charts
        }
        
        # Analyze the data using Azure OpenAI
        analysis = analyze_stock_data(ticker, all_data)
        
        return jsonify({
            "ticker": ticker,
            "data": all_data,
            "analysis": analysis
        })
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error in analyze_stock: {error_msg}")
        return jsonify({"error": error_msg}), 500

@app.route('/search_docs', methods=['POST'])
def search_documents():
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "검색어가 필요합니다"}), 400
    
    try:
        search_results = search_azure_ai(query)
        return jsonify({
            "results": search_results
        })
    except Exception as e:
        error_msg = str(e)
        print(f"문서 검색 중 오류 발생: {error_msg}")
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False) 
