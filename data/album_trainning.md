# Danh mục bộ sưu tập

## Giới thiệu

Bộ sưu tập là tập hợp ảnh các sản phẩm có cùng chủ đề, giúp Shop quản lý sản phẩm theo nhóm dễ dàng và hiệu quả, đồng thời giúp người mua có thể nhanh chóng tìm món hàng theo nhu cầu, theo ngành hàng.

Bộ sưu tập của 1 website cơ bản thì sẽ bao gồm các nội dung sau:

### Thẻ meta bộ sưu tập

Thẻ Meta là các đoạn văn bản mô tả nội dung của trang, các thẻ này không xuất hiện trên chính trang mà chỉ xuất hiện trong phần mã nguồn của trang. Về cơ bản chúng giúp cho các công cụ tìm kiếm hiểu rõ hơn về nội dung của một trang web, do vậy rất tốt cho SEO.

Dưới đây là cách thức lấy thẻ meta bộ sưu tập của website:

```
{{ headTitle(category.name).setSeparator(' - ').setAutoEscape(false)|raw }}
    <meta name="keywords" content="{{ category.metaKeywords ?: category.name }}">
    <meta name="description" content="{{ category.metaDescription ?: category.name }}">
    <meta property="og:title" content="{{ category.name }}">
    <meta property="og:url" content="{{ category.canonicalLink }}">
    <meta property="og:image" content="{{ category.imgUri }}">
    <meta property="og:type" content="website">
    <link rel="canonical" href="{{ category.canonicalLink }}" />
           
```

### Danh sách bộ sưu tập

Danh sách album ảnh là nơi tổng hợp các bộ sưu tập hình ảnh được phân loại theo chủ đề như sự kiện, sản phẩm, hoạt động doanh nghiệp, hoặc phản hồi từ khách hàng. Mỗi album giúp người xem dễ dàng theo dõi nội dung hình ảnh theo từng nhóm, tăng tính trực quan và sinh động cho website. Tính năng này đặc biệt hữu ích để giới thiệu thương hiệu, tạo dấu ấn thị giác và tăng mức độ tương tác với người dùng.

Dưới đây là cách thức lấy danh sách bộ sưu tập của website:

* Cách làm:
  * B1. Kiểm tra danh sách album có dữ liệu (if albums.currentModels is not empty)
  * B2. Duyệt qua từng album
  * B3. Lấy nội dung phụ nếu có (extraContent)
  * B3.1. Nếu album có nội dung bổ sung (extraContent), thì gọi hàm a.extraContent(true) để lấy.
  * B3.2. Lưu phần nội dung mô tả chi tiết vào biến content
  * B4. Hiển thị thông tin của album: ảnh, link, tên, Nội dung mô tả (nếu có)

```
{% raw %}
{% if(albums.currentModels is not empty) %}
    {% for a in albums.currentModels %} 
        {% if(a.extraContent) %}
            {% set extraContent = a.extraContent(true) %}
            {% set content = extraContent['content'] %}
        {% endif %}
        {{a.name}}
        {{a.getImageSrc}}
        {{a.name}}
        {{a.viewLink}}
        {{content}}
    {% endfor %}
{% endif %}
{% endraw %}
```

### Ảnh trong bộ sưu tập

Ảnh trong bộ sưu tập là các hình ảnh được phân nhóm theo từng album cụ thể nhằm minh họa cho một chủ đề, sự kiện hoặc sản phẩm nhất định. Mỗi album chứa nhiều ảnh liên quan giúp người dùng dễ dàng xem chi tiết, cảm nhận được nội dung và ý nghĩa của bộ sưu tập. Việc trình bày ảnh theo album không chỉ giúp website trực quan và hấp dẫn hơn, mà còn nâng cao trải nghiệm người dùng khi khám phá nội dung bằng hình ảnh sinh động.
Dưới đây là cách thức lấy ảnh trong bộ sưu tập của website:

* Cách làm:
  * B1. Lấy danh sách ảnh từ hàm fetchAllItemAlbum
  * B2. Kiểm tra nếu album có ảnh (if items is not empty)
  * B3. Duyệt qua từng ảnh trong album
  * B8. Hiển thị mô tả ảnh
```
{% raw %}
{% set items = fetchAllItemAlbum(album.id) %}
   {% if items is not empty %}
     {% for a in items %}
        {{ a.thumbnailUri }}
        {{ a.id }}
        {{ a.name }}
       {% endfor %}
    {% endif %}     
{% endraw %}
```

### Sản phẩm được tag trong ảnh

Sản phẩm được tag trong ảnh là tính năng cho phép liên kết trực tiếp các hình ảnh trong bộ sưu tập với thông tin sản phẩm cụ thể. Thông qua các tag này, mỗi ảnh không chỉ mang giá trị minh họa trực quan mà còn đóng vai trò như một điểm tương tác thương mại, hỗ trợ người dùng truy cập nhanh vào chi tiết sản phẩm tương ứng.
Dưới đây là cách thức lấy sản phẩm được tag trong ảnh:

* Cách làm:
  * B1. Lấy danh sách sản phẩm được gắn trong ảnh (getAlbumTag)
  * B2. Kiểm tra có dữ liệu không (if itemsTags is not empty)
  * B3. Vòng lặp hiển thị sản phẩm: ảnh, tên, giá, link
  * B4. Hiển thị giá theo điều kiện (liên hệ, giảm giá, giá gốc)
  * B5. Hiển thị mô tả ảnh
```
{% raw %}
    {% set itemsTags = getAlbumTag(a.id) %}
    {% if itemsTags is not empty %}
        {% for it in itemsTags %}
            {% if it.product is not empty %}
                    {% set p = it.product %}
                    {{ p.viewlink }}
                    {{ p.name }}
                    {% if(p.contactPrice or (p.price == 0)) %}   
                        Liên hệ
                    {% elseif (p.priceAfterDiscount > 0) %}
                        {{ p.price|number_format(0) }} ₫
                        {{ p.priceAfterDiscount|number_format(0) }} ₫
                    {% elseif (p.oldprice > 0) %}
                        {{ p.oldprice|number_format(0) }} ₫
                        {{ p.priceAfterDiscount|number_format(0) }} ₫
                    {% else %}
                        {{ p.price|number_format(0) }} ₫
                    {% endif %} 
                 {{ a.description | raw }}
                 {% endif %}
                {% endfor %}
             {% endif %} 
{% endraw %}
```

### Phân trang bộ sưu tập

```
{{ render_paginator(paginator) }}
           
```

<figure><img src="../../.gitbook/assets/image (8).png" alt=""><figcaption></figcaption></figure>
