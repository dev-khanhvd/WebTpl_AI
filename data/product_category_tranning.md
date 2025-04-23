# Danh mục sản phẩm

## Các nội dung cơ bản của trang danh mục sản phẩm <a href="#cac-noi-dung-co-ban-cua-header" id="cac-noi-dung-co-ban-cua-header"></a>

Trang danh mục sản phẩm về cơ bản nội dung sẽ giống như trang danh sách sản phẩm. Tuy nhiên, trang danh sách sản phẩm sẽ chỉ liệt kê sản phẩm cũng như bộ lọc của danh mục sản phẩm đó chứ không phải tất cả sản phẩm như trang danh sách sản phẩm. Trang danh mục sản phẩm của 1 website cơ bản thì sẽ bao gồm các nội dung sau:

### Các thẻ meta của danh mục sản phẩm

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

### Cây danh mục sản phẩm

Cây danh mục sẽ lấy danh mục con của sản phẩm đó. Nếu không có thì sẽ mặc định hiển thị danh mục cấp 1

* Cách làm:
  * B1. Lấy danh sách danh mục con
  * B2. Kiểm tra nếu có danh mục con (if child is not empty )
  * B3. Lặp qua danh mục con để hiển thị tên + link
  * B4. Nếu không có danh mục con, gọi hàm getCategories() để lấy danh sách danh mục cấp 1
  * B5. Kiểm tra nếu có danh mục (if category is not empty)
  * B6. Hiển thị danh sách danh mục từ hàm getCategories(): tên, link
  
```
{% raw %}
    {% set child = category.childs %}
    {% if child is not empty %}
        {% for c in child %}
            {{ c.viewLink }}
            {{ c.name }}
        {% endfor %}
    {% else %}
        {% set category = getCategories() %}  
        {% if category is not empty %}
        {% for c in category %}
            {{ c.viewLink }}
            {{ c.name }}
        {% endfor %}
    {% endif%}  
    {% endif %}
{% endraw %}
```

### Bộ lọc giá

Lọc khoảng giá cho danh sách sản phẩm 

* Cách làm:
  * B1. Lấy tham số giá từ getParam('price')
  * B2. Lặp qua các dải giá (price_ranges)
  * B3. Định dạng giá trị min và max
  * B4. Tạo một chuỗi biểu diễn dải giá dưới dạng min_price:max_price 
  * B5. Gán tên cột để dùng Kiểm tra nếu dải giá đã được chọn (if range_string in price_param)
  * B6. Cập nhật bộ lọc và trạng thái checkbox
  * B7. Ngược lại, thêm bộ lọc và bỏ qua checkbox
  * B8. Hiển thị checkbox và label
```
{% raw %}
{% set price_ranges = [
    ["0", "200000"],
    ["200000", "350000"],
    ["350000", "500000"],
    ["500000", "800000"],
    ["800000", "1000000"],
    ["1000000", "0"],
] %}

{% set price_param = getParam('price') %}
 {% for range in price_ranges %}
    {% set min_price = range[0]|number_format(0, '.', '') %}
    {% set max_price = range[1]|number_format(0, '.', '') %}
    {% set range_string = min_price ~ ':' ~ max_price %}
    {% if(range_string in price_param) %}
        {% set filter = removeFilter('price', range_string) %}
        {% set checked =  'checked' %}
    {% else %}
        {% set filter = addFilter('price', range_string) %}
        {% set checked =  '' %}
    {% endif %}
    <div>
        <input type="checkbox" value="{{ filter }}" {{ checked }}>
        <label>
              {% if(min_price == 0 and max_price == 200000) %}
                    Dưới {{ max_price/1000|number_format(0, '.', '') ~ 'k' }}
              {% elseif (min_price == 1000000 and max_price == 0) %}
                   Trên 1 triệu
              {% else %}
                  Từ {{ min_price/1000|number_format(0, '.', '') ~ 'k' }} - {{ max_price/1000|number_format(0, '.', '') ~ 'k' }}
              {% endif %}
        </label>
    </div>
{% endfor %}
{% endraw %}
```
### Bộ lọc thương hiệu danh mục sản phẩm

Lấy ra danh sách các thương hiệu theo danh mục sản phẩm

* Cách làm:
  * B1. Lấy danh sách thương hiệu theo danh mục từ hàm loadListBrands
  * B2. Lấy thông tin lọc từ URL (getParam('brand'))
  * B3. Nếu có tham số brand, chuyển thành mảng
  * B4. Kiểm tra nếu có danh sách thương hiệu (if l_brand)
  * B5. Lặp qua từng thương hiệu
  * B6. Kiểm tra xem thương hiệu hiện tại có được chọn (đang lọc) hay không
  * B6. Hiển thị input theo điều kiện: Chưa lọc và đã lọc
```
{% raw %}
 {% set l_brand = loadListBrands({'categoryId':category.id}) %}
 {% set prBrand = getParam('brand') %}
 {% if prBrand %}
  {% set prBrand = prBrand|split(',') %}
 {% endif %}
 {% if l_brand %}
  {% for b in l_brand %}
   {% if prBrand is defined and b.id in prBrand %}
    <input checked type="checkbox" value="{{ removeFilter('brand', b.id) }}">
    {{ b.name|raw }}
   {% else %}
   <input type="checkbox" value="{{ category.viewLink ~ '?brand=' ~ b.id }}">
    {{ b.name|raw }}
   {% endif %}
  {% endfor %}
 {% endif %}
{% endraw %}
```
### Bộ lọc thuộc tính

Hiển thị bộ lọc thuộc tính theo danh mục sản phẩm hoặc theo danh sách sản phẩm 

* Cách làm:
  * B1. Lấy danh sách tất cả thuộc tính theo danh mục từ getAllAttributes().
  * B2. Kiểm tra nếu tồn tại danh sách thuộc tính
  * B3. Vòng lặp duyệt qua từng thuộc tính
  * B4. Kiểm tra nếu thuộc tính có danh sách giá trị (values)
  * B5. Gán column để dùng cho bộ lọc: {% set column = attr.column %}
  * B6. Hiển thị tên thuộc tính, thêm ở thẻ bao quanh tên thuộc tính thì thêm attribute trong thẻ đó là: data-column = column, data-id = attr.id
  * B7. Lặp qua từng giá trị trong thuộc tính
  * B8. Kiểm tra xem giá trị đang được lọc hay không
  * B9. Hiển thị input theo điều kiện: Chưa lọc và đã lọc 
  
```
{% raw %}
{% set allAttr = getAllAttributes({'categoryId':category.id}) %}
{% if(allAttr) %}
    {% for attr in allAttr %}
        {% if(attr.values != null) %}
            {% set column = attr.column %}
            {{ attr.name | raw }}
            {{ attr.id | raw }}
            {% for cl in attr.values %}
               {% if cl.id in attrColumnValues[column] %}
                    <input checked type="checkbox" value="{{ removeFilter(column, cl.id) }}">
                    {{ cl.name|raw }}
               {% else %}
                    <input type="checkbox" value="{{ addFilter(column, cl.id, 2) }}">
                    {{ cl.name|raw }}
               % endif %}
           {% endfor %}
        {% endif %}
    {% endfor %}
{% endif %}
{% endraw %}
```

### Sắp xếp sản phẩm

```
{% raw %}
<ul>
    <li class="{{ getParam('show') == 'discount' ? 'selected' : '' }}">
        <a href="{{ addFilter('show', 'discount', 2) }}">Khuyến mãi</a>
    </li>
    <li class="{{ getParam('show') == 'priceAsc' ? 'selected' : '' }}">
        <a href="{{ addFilter('show', 'priceAsc', 2) }}">Giá:Tăng dần</a>
    </li>
    <li class="{{ getParam('show') == 'priceDesc' ? 'selected' : '' }}">
        <a href="{{ addFilter('show', 'priceDesc', 2) }}">Giá: Giảm dầm</a>
    </li>
    <li class="{{ getParam('show') == 'nameAsc' ? 'selected' : '' }}">
        <a href="{{ addFilter('show', 'nameAsc', 2) }}">Tên: A - Z</a>
    </li>
    <li class="{{ getParam('show') == 'nameDesc' ? 'selected' : '' }}">
        <a href="{{ addFilter('show', 'nameDesc', 2) }}">Tên: Z - A</a>
    </li>z
    <li class="{{ getParam('show') == 'old' ? 'selected' : '' }}">
        <a href="{{ addFilter('show', 'old', 2) }}">Cũ nhất</a>
    </li>
    <li class="{{ getParam('show') == 'new' ? 'selected' : '' }}">
        <a href="{{ addFilter('show', 'new', 2) }}">Mới nhất</a>
    </li>
</ul>
{% endraw %}
```

### Danh sách sản phẩm theo phân trang trong danh mục

Danh sách sản phẩm bao gồm tất cả các sản phẩm có thể bán trên website.

* Cách làm:
  * B1. Kiểm tra xem paginator.currentModels có dữ liệu không
  * B3. Vòng lặp hiển thị sản phẩm: ảnh, tên, giá, đánh giá, nút hành động
  * B4. Nếu có giảm giá, hiển thị phần trăm giảm giá
  * B5. Nút hành động: thêm vào giỏ, yêu thích, xem nhanh (Thêm thuộc tính data-id="{{ p.id }}")
  * B6. Hiển thị giá theo điều kiện (liên hệ, giảm giá, giá gốc)

```
{% raw %}
{% if paginator.currentModels %}
    {% for p in paginator.currentModels %}
       {{ p.id }}
       {{ p.thumbnailUri }}
       {{ p.viewLink }}
       {{ p.name }}
       {% if(p.calcDiscountPercent > 0) %}
            {{ p.calcDiscountPercent }}%
       {% endif %}   
       {% if(p.contactPrice or (p.price == 0)) %}   
           Liên hệ
       {% elseif p.priceAfterDiscount > 0 %}
          {{ p.priceAfterDiscount | number_format(0) }}₫
          {{ p.price | number_format(0) }}₫
       {% elseif (p.oldPrice > 0) %}
          {{ p.price | number_format(0) }}₫
          {{ p.oldPrice | number_format(0) }}₫
       {% else %}
          {{ p.price | number_format(0) }}₫
        {% endif %}
    {% endfor %}
{% endif %}
{% endraw %}
```

### Phân trang

Hiển thị phân trang trong danh sách sản phẩm

```
{% raw %}
{{ render_paginator(paginator) }}
{% endraw %}
```

<figure><img src="../../.gitbook/assets/image (52).png" alt=""><figcaption></figcaption></figure>
