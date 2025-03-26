import platform
import subprocess
from llama_cpp import Llama

from agents.home_page import HomePage

class BaseAgent:
    def __init__(self, base_dir):
        self.base_dir = base_dir
    def menu_agent(self):
        print("\n=== Menu xử lý fill logic website ===")
        options = [
            'Trang chủ',
            'Danh mục sản phẩm',
            'Chi tiết sản phẩm',
            'Giỏ hàng',
            'Thanh toán',
            'Thanh toán thành công',
        ]
        while True:
            self.clear_screen()
            print("\n=== Menu xử lý fill logic website ===")
            for i, option in enumerate(options):
                print(f"{i + 1}. {option}")

            menu_choice = input("Nhập số thứ tự trên menu để thao tác (hoặc 'exit' để thoát): ").strip()

            if menu_choice.lower() == "exit" or not menu_choice:
                print("👋 Thoát module xử lý logic!")
                break

            if not menu_choice.isdigit():
                print("Lỗi: Vui lòng nhập một số hợp lệ!")
                continue

            menu_choice = int(menu_choice)

            if menu_choice == 1:
                home_page = HomePage(self.base_dir)
                home_page.get_home_page_content()
                break
            elif menu_choice == 2:
                continue
            elif menu_choice == 3:
                continue
            elif menu_choice == 4:
                continue
            elif menu_choice == 5:
                continue
            elif menu_choice == 6:
                continue
            else:
                break

    # def ai_processing(self, user_question):
    #     model_path = "C:/Users/phogu/AppData/Local/nomic.ai/GPT4All/deepseek-coder-6.7b-base.Q4_0.gguf"
    #     llm = Llama(
    #         model_path=model_path,
    #         n_ctx=4096,  # Context size
    #         n_gpu_layers=32  # Adjust based on your GPU capability
    #     )
    #
    #     input_text = "#write a quick sort algorithm"
    #     output = llm(input_text, max_tokens=500)
    #
    #     # Print the generated text
    #     print(output['choices'][0]['text'])

    def clear_screen(self):
        """Clear the terminal screen based on the operating system."""
        if platform.system() == "Windows":
            subprocess.call('cls', shell=True)
        else:  # For Linux and MacOS
            subprocess.call('clear', shell=True)