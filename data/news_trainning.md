# Danh mục tin tức

## Các nội dung cơ bản của trang danh mục tin tức

Trang danh mục tin tức về cơ bản nội dung sẽ giống như trang danh sách sản phẩm. Tuy nhiên, trang danh sách tin tức sẽ chỉ liệt kê tin tức của danh mục đó chứ không liệt kê tất cả tin tức như trang danh sách sản phẩm. Trang danh mục tin tức của 1 website cơ bản thì sẽ bao gồm các nội dung sau:

### Các thẻ meta

```
{% raw %}
{% extends layout_layout %} 
{% block meta %}
{{ headTitle(category.name).setSeparator(' - ').setAutoEscape(false)|raw }}
<meta name="keywords" content="{{ category.metaKeywords ?: category.name }}">
<meta name="description" content="{{ category.metaDescription ?: category.name }}">
<meta property="og:title" content="{{ category.metaTitle ?: category.name }}">
<meta property="og:url" content="{{ category.canonicalLink }}">
<meta property="og:image" content="{{ category.imageUri }}">
<meta property="og:type" content="website">
<link rel="canonical" href="{{ category.canonicalLink }}" />
{% endblock %}
{% endraw %}
```

### Danh sách bài viết tin tức

Danh sách bài viết tin tức là tập hợp các bài viết được trình bày theo dạng lưới hoặc danh sách, nhằm cung cấp thông tin thời sự, sự kiện hoặc cập nhật mới nhất đến người đọc.Giúp người dùng nhanh chóng nắm bắt các tin tức mới, tăng khả năng duyệt nhiều nội dung liên quan, nâng cao tính cập nhật và chuyên nghiệp cho website.

Dưới đây là cách thức lấy bài viết tin tức trên website:

* Cách làm:
  * B1. Kiểm tra xem danh sách bài viết (paginator.currentModels) có dữ liệu hay không
  * B2. Lặp qua từng bài viết trong danh sách 
  * B4. Fill code với các giá trị tương ứng
  * B5. Kết thúc điều kiện if ban đầu – đảm bảo chỉ render nếu có bài viết
  * B6. Gọi hàm để hiển thị thành phần phân trang (các nút chuyển trang, số trang...).
  
```
{% raw %}
{% if(paginator.currentModels is not empty) %}
    {% for art in paginator.currentModels %}
         {{ art.viewLink }}
         {{ art.pictureUri }}
         {{ art.title | raw }}
         {% set time = art.createdDateTime|split(' ') %}
         {% set date = time[0]|split('-') %}
         {{ date[2] }}/{{ date[1] }}/{{ date[0] }}
         {{ art.intro(true) | raw }}
    {% endfor %}
    {{ render_paginator(paginator) }}
{% endif %}
{% endraw %}
```

### Tag bài viết

Tag bài viết là các từ khóa ngắn gọn dùng để nhóm các bài viết có nội dung liên quan lại với nhau. Việc gắn tag giúp người đọc dễ dàng tìm kiếm và khám phá thêm các bài viết cùng chủ đề, đồng thời hỗ trợ cải thiện khả năng điều hướng và tối ưu SEO cho website.

Dưới đây là cách thức lấy Tag bài viết:

* Cách làm:
  * B1. Lấy tối đa tag thuộc cùng 1 bài viết theo param itemId, theo type ở hàm getTags().
  * B2. Kiểm tra có dữ liệu không (if getTags is not empty)
  * B3. Vòng lặp hiển thị tag: link, tên tag

```
{% raw %}
{% set tags = getTags({'itemId':news.id,'type':'article'}) %}
{% if (tags is not empty) %}
    {% for t in tags %}
        {{ t.viewLink }}
        {{ t.name }}
     {% endfor %}
{% endif %}
{% endraw %}
```

### Bài viết cùng danh mục

"Bài viết cùng danh mục" là phần hiển thị danh sách các bài viết khác có cùng chủ đề hoặc chuyên mục với bài viết hiện tại, nhằm gợi ý thêm nội dung liên quan cho người đọc.

Dưới đây là cách thức lấy bài viết liên quan:
* Cách làm:
  * B1. Lấy tối đa bài viết thuộc cùng 1 danh mục param limit, loại trừ sản phẩm hiện tại theo param excludedIds ở hàm searchNewsByCategory().
  * B2. Kiểm tra có dữ liệu không (if relatedNews is not empty)
  * B3. Vòng lặp hiển thị bài viết: thời gian, ngày tạo, link, ảnh, mô tả
  * B3.1. Hiển thị ngày đăng bài dưới định dạng DD/MM/YYYY

```
{% raw %}
{% set relatedNews = searchNewsByCategory(category.id,{'limit':4,'excludedIds': news.id}) %}
{% if relatedNews is not empty %}
    {% for n in relatedNews %}
            {% set time = news.createdDateTime|split(' ') %}
            {% set date = time[0]|split('-') %}
            {{ n.viewLink}}
            {{ n.title | raw }}
            {{ n.imageUri }}
            {{ date[2] }}/{{ date[1] }}/{{ date[0] }}
            {{ art.intro(true) | raw }}
    {% endfor %}
{% endif %}
{% endraw %}
```