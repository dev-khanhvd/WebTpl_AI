import tiktoken
import openai
import textwrap
from config import MODEL_NAME, OPENAI_API_KEY


class TokenOptimizer:
    def __init__(self, model_name= MODEL_NAME):
        self.model_name = model_name
        openai.api_key = OPENAI_API_KEY

        self.encoding = tiktoken.encoding_for_model(model_name)

    def count_tokens(self, text):
        """
        Đếm số lượng token trong văn bản
        """
        return len(self.encoding.encode(text))

    def truncate_text(self, text, max_tokens):
        """
        Cắt văn bản để giảm số lượng token
        """
        tokens = self.encoding.encode(text)
        return self.encoding.decode(tokens[:max_tokens])

    def chunk_text(self, text, max_tokens_per_chunk):
        """
        Chia văn bản thành các đoạn nhỏ
        """
        tokens = self.encoding.encode(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens_per_chunk):
            chunk = self.encoding.decode(tokens[i:i + max_tokens_per_chunk])
            chunks.append(chunk)

        return chunks

    def optimize_prompt(self, prompt):
        """
        Tối ưu hóa prompt để giảm token
        """
        # Loại bỏ khoảng trắng thừa
        prompt = ' '.join(prompt.split())

        # Viết lại prompt ngắn gọn
        return textwrap.fill(prompt, width=100)

    def get_completion(self, prompt, max_tokens=150):
        """
        Gọi API với prompt tối ưu
        """
        # Kiểm tra và cắt token nếu cần
        if self.count_tokens(prompt) > 4000:
            prompt = self.truncate_text(prompt, 4000)

        return prompt
        # try:
        #     response = openai.ChatCompletion.create(
        #         model=self.model_name,
        #         messages=[
        #             {"role": "system", "content": "Bạn là trợ lý AI hữu ích."},
        #             {"role": "user", "content": prompt}
        #         ],
        #         max_tokens=max_tokens
        #     )
        #     return response.choices[0].message['content']
        # except Exception as e:
        #     print(f"Lỗi khi gọi API: {e}")
        #     return None


# Ví dụ sử dụng
def main():
    # Khởi tạo optimizer
    optimizer = TokenOptimizer()

    # Ví dụ văn bản dài
    long_text = """
    Đây là một ví dụ về văn bản dài mà chúng ta muốn xử lý 
    và tối ưu hóa số lượng token khi gửi đến OpenAI API. 
    Chúng ta sẽ sử dụng các kỹ thuật như chia nhỏ văn bản, 
    đếm token, và cắt giảm nếu cần thiết.
    """

    # Đếm token
    print("Số lượng token:", optimizer.count_tokens(long_text))

    # Chia văn bản thành chunks
    chunks = optimizer.chunk_text(long_text, max_tokens_per_chunk=50)
    print("Các chunk:", chunks)

    # Tối ưu prompt
    optimized_prompt = optimizer.optimize_prompt(long_text)
    print("Prompt tối ưu:", optimized_prompt)

    # Gọi API với prompt tối ưu
    response = optimizer.get_completion(optimized_prompt)
    print("Phản hồi:", response)


if __name__ == "__main__":
    main()