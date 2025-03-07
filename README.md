# Sử dụng LangChain framework
https://python.langchain.com/docs/how_to/installation/

# Cách cài đặt  
    - Cài đặt python: https://www.python.org/downloads/ (version mới nhất: 3.13.2)  
    - Cài đặt pip: https://pip.pypa.io/en/stable/installation/

 ## Khi cài đặt, mặc định python sẽ cài đặt pip (pip 23.2.1)  
    - Trong TH không tự động cài đặt thì dùng:  
        python -m pip install \--upgrade pip   (Mặc định lấy version pip mới nhất để cài đặt)

    - Khởi tạo langchain framework, dùng PyCharm  
        pip install langchain  
        pip install openai (Muốn tích hợp luôn OpenAI thì dùng lệnh này ) 
        pip install langchain-community

 ## Cài đăt streamlit (https://pypi.org/project/streamlit/)  
    - Streamlit là một framework Python giúp tạo ứng dụng web nhanh chóng, chủ yếu dành cho machine learning và data science mà không cần dùng HTML, CSS hay JavaScript. Demo này tạm thời sử dụng call API của Deepseek - R1
    - Cài đặt env (Dùng để lưu cấu hình chung)  
        pip install python-dotenv  
        python -c \"import os; from dotenv import load_dotenv; 
        load_dotenv();
        print(os.getenv('OPENAI_API_KEY'))" (Kiểm tra xem key có hoạt động không)

## Embeddings & Vector Database  
    - Embeddings: Embeddings là một cách để chuyển đổi văn bản, hình ảnh thành một vector số (mảng số thực)  
    - Vector Database: DB được tối ưu hóa để lưu trữ và tìm kiếm embeddings dựa trên sự tương đồng

## Cài đặt Chroma DB 
    - pip install chromadb  
    - Windows không hỗ trợ trực tiếp ChromaDB, cần sử dụng WSL (Windows Subsystem for Linux) hoặc MinGW. Nếu chưa có WSL, hãy bật nó bằng lệnh sau trong PowerShell (chạy với quyền Admin):  
        wsl --install.

    - Cài đặt xong, mở WSL bắt đầu cài lại ChromaDB (chroma-hnswlib)  
        sudo apt update  
        sudo apt install -y build-essential cmake python3-dev
    - Nếu báo lỗi:  
        - sudo not found:  
            whoami (check xem có quyền root hay không)  
            - Nếu trả về root, không cần sudo  
                apt update  
                apt install sudo -y  
            - Nếu trả về một user khác, thì sudo thực sự bị thiếu => Cài đặt lại sudo  
        - apt not found:  
            - Kiểm tra lại hệ điều hành  
                uname -a - cat /etc/os-release  
            - Dùng Alpine Linux  
                apk update 
                apk add sudo  
            - Dùng CentOS/RHEL  
                yum update -y  
                yum install sudo -y


    - Sau khi hoàn thành, tiếp tục cài đặt ChromaDB
    - Sau khi cài mà vẫn báo lỗi: Could not build wheels for hnswlib, which is required to install pyproject.toml-based projects  
        - Cách fix issue: 
            https://github.com/chroma-core/chroma/issues/189#issuecomment-1454418844

    - Chạy lại 2 câu lệnh như ở dưới là done:  
        pip install \--no-cache-dir hnswlib  
        pip install \--q chromadb

## Cài đặt PyWebCoppy  
    pip install pywebcopy  
    pip install lxml_html_clean (Thư viện của PyWebCoppy)

## Cài đặt BeautifulSoup: 
    -  Thư viện Python dùng để lấy dữ liệu ra khỏi các file HTML và XML  
        pip install requests beautifulsoup4


## Hiện tại đang xử lý AI chạy trên local bằng con DeepSeek R1 Distill
https://huggingface.co/deepseek-ai/DeepSeek-R1

## Đang dùng GPT4ALL để xử lý training cho con AI này. Docs đọc ở đây
https://github.com/nomic-ai/gpt4all
https://docs.gpt4all.io/
