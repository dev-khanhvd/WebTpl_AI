# Sử dụng LangChain framework
https://python.langchain.com/docs/how_to/installation/

# Cách cài đặt  
    - Cài đặt python: https://www.python.org/downloads/ (version mới nhất: 3.13.2)  
    - Cài đặt pip: https://pip.pypa.io/en/stable/installation/

 ## Khi cài đặt, mặc định python sẽ cài đặt pip (pip 23.2.1)  
    - Trong TH không tự động cài đặt thì dùng:  
        python -m pip install --upgrade pip   (Mặc định lấy version pip mới nhất để cài đặt)

    - Khởi tạo langchain framework, dùng PyCharm  
        pip install langchain  
        pip install openai (Muốn tích hợp luôn OpenAI thì dùng lệnh này ) 
        pip install langchain-community

 ## Cài đăt streamlit (https://pypi.org/project/streamlit/)  
    - Streamlit là một framework Python giúp tạo ứng dụng web nhanh chóng, chủ yếu dành cho machine learning và data science mà không cần dùng HTML, CSS hay JavaScript.

 ## Cài đặt env (Dùng để lưu cấu hình chung)  
        pip install python-dotenv  
        python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))" (Kiểm tra xem key có hoạt động không)

## Embeddings & Vector Database  
    - Embeddings: Embeddings là một cách để chuyển đổi văn bản, hình ảnh thành một vector số (mảng số thực)  
    - Vector Database: DB được tối ưu hóa để lưu trữ và tìm kiếm embeddings dựa trên sự tương đồng
## Elastic DB
    - https://www.docker.com/
    - https://www.elastic.co/guide/en/elasticsearch/reference/current/zip-windows.html

## Cài đặt Scrapy: https://scrapy.org/
    pip install scrapy

## Cài đặt BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        pip install requests beautifulsoup4

## Tạo server API, dùng fastAPI để xử lý: https://fastapi.tiangolo.com/, https://fastapi.tiangolo.com/vi/tutorial/
    pip install fastapi uvicorn

## Xử lý embeddings + LLaMa để trainning cho AI
    // llama-cpp-python → Chạy mô hình LLaMA trên CPU/GPU
    // sentence-transformers → Tạo embeddings từ văn bản
    pip install llama-cpp-python sentence-transformers
    
    - Đang dùng all-mpnet-base-v2 để xử lý embedding 768 chiều