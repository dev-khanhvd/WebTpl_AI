def run():
    print("\n Bắt đầu xử lý logic trong agent_main...")

if __name__ == "__main__":
    print("\nMenu xử lý fill logic website:")
    options = [
        'Trang chủ',
        'Danh mục sản phẩm',
        'Chi tiết sản phẩm',
        'Giỏ hàng',
        'Thanh toán',
        'Thanh toán thành công',
    ]
    actions = {
        1: lambda: print("Xử lý logic trang chủ"),
        2: lambda: print("Xử lý danh mục sản phẩm"),
        3: lambda: print("Xử lý chi tiết sản phẩm"),
        4: lambda: print("Xử lý giỏ hàng"),
        5: lambda: print("Xử lý thanh toán"),
        6: lambda: print("Xử lý thanh toán thành công"),
    }
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        menu_choice = input("Nhập số thứ tự trên menu để thao tác (hoặc 'exit' để thoát): ").strip()

        if menu_choice.lower() == "exit" or not menu_choice:
            print("👋 Thoát module xử lý logic!")
            break

        if not menu_choice.isdigit() or (choice := int(menu_choice)) not in actions:
            print("Lỗi: Vui lòng nhập một số hợp lệ!")
            continue

        actions[choice]()