# Chi tiết sản phẩm

## Các nội dung cơ bản của trang chi tiết sản phẩm <a href="#cac-noi-dung-co-ban-cua-header" id="cac-noi-dung-co-ban-cua-header"></a>

Trang chi tiết sản phẩm là trang chứa các thông tin chi tiết của sản phẩm như hình ảnh, thông tin về mô tả sản phẩm, chi tiết sản phẩm, các thuộc tính sản phẩm... và các thao tác mua bán sản phẩm. Trang sẽ giúp cho khách hàng có được cái nhìn cụ thể, rõ ràng nhất trước khi quyết định mua sản phẩm. Trang chi tiết sản phẩm sản phẩm của 1 website cơ bản thì sẽ bao gồm các nội dung sau:

### Các thẻ meta

```
{% raw %}
{% extends layout_layout %}
{% block meta %}
   {{ headTitle(product.name).setSeparator(' - ').setAutoEscape(false)|raw }}
    <meta name="keywords" content="{{ product.metaKeywords ?: product.name }}">
    <meta name="description" content="{{ product.metaDescription ?: product.name }}">
    <meta property="og:title" content="{{ product.metaTitle ?: product.name }}">
    <meta property="og:url" content="{{ product.canonicalLink }}">
    <meta property="og:image" content="{{ product.imageUri }}">
    <meta property="og:type" content="website">
    <link rel="canonical" href="{{ product.canonicalLink }}" />
{% endblock %}
{% endraw %}
```

### Ảnh sản phẩm

Danh sách ảnh sản phẩm sẽ lấy ra tất cả ảnh của sản phẩm, bảo gồm ảnh cha và ảnh con.
* Cách làm:
  * B1. Nếu product.images tồn tại (danh sách ảnh), thì:
  * B1.1. Duyệt qua danh sách ảnh (product.images)
  * B1.2. Với mỗi ảnh: Hiển thị đường dẫn ảnh, tên sản phẩm
  * B2. Nếu không có product.images
  * B2.1. Hiển thị ảnh của sản phẩm, tên sản phẩm
```
{% raw %}
{% if product.images %}
    {% for i in product.images %}
        {{ i.thumbnailUri }}
        {{ product.name }}
    {% endfor %}
{% else %}
  {{ product.imageUri }}
  {{ product.name }}
{% endif %}
{% endraw %}
```

### Tên sản phẩm

Tên sản phẩm sẽ được lấy ra như sau như sau:

```
{% raw %}
{{ product.name }}
{% endraw %}
```

### Giá sản phẩm

Giá sản phẩm thường sẽ bao gồm giá mới, giá cũ và số phần trăm giảm giá (nếu có) của sản phẩm và sẽ được gọi ra như sau:

* Cách làm:
  * B1. Kiểm tra và hiển thị giá
  * B1.1. Nếu sản phẩm yêu cầu liên hệ để biết giá hoặc giá = 0 → hiển thị: Liên hệ.
  * B1.2. Nếu có giá sau giảm (priceAfterDiscount > 0) → hiển thị:Giá sau giảm,Giá gốc
  * B1.3. Nếu không có priceAfterDiscount nhưng có oldPrice → hiển thị:Giá hiện tại (price), Giá cũ (oldPrice)
  * B2. Hiển thị phần trăm giảm nếu có
  
```
{% raw %}
    {% if(product.contactPrice or (product.price == 0)) %}
        Liên hệ
    {% elseif (product.priceAfterDiscount > 0) %}
        {{ product.priceAfterDiscount|number_format(0) }}đ
        {{product.price|number_format(0) }}đ
    {% elseif (product.oldprice > 0) %}
         {{ product.price|number_format(0) }}đ
         {{ product.oldPrice|number_format(0) }}đ
    {% else %}
        {{ product.price|number_format(0) }}đ
    {% endif %}
    {% if product.calcDiscountPercent > 0 %}
       -{{ product.calcDiscountPercent}}%
    {% endif %}
{% endraw %}
```

### Thuộc tính sản phẩm

Thuộc tính của sản phẩm sẽ gồm 2 thuộc tính chính là màu và size, sẽ được gọi ra như sau:

* Cách làm:
  * B1. Lấy các thuộc tính từ sản phẩm (color, size...)
  * B1.1. Biến flag dùng để xác định xem có thuộc tính nào được hiển thị không
  * B2. Hiển thị chọn Màu sắc (color)
  * B2.1. Kiểm tra thuộc tính màu (if color is not null or color is not empty)
  * B2.2. Lấy danh sách các giá trị màu và đếm số lượng.
  * B2.3. Nếu danh sách màu có giá trị thì xử lý hiển thị
  * B2.4. Đếm  flag và tạo giao diện chọn màu
  * B3. Tạo vòng lặp hiển thị từng màu
  * B3.1. Tạo mảng chứa giá trị màu đang lặp qua
  * B3.2. Gọi hàm getAttrValueImage để lấy ảnh tương ứng và danh sách id sản phẩm tương ứng với màu đó
  * B3.3. Hiển thị lựa chọn màu với ảnh và tên
  * B4. Hiển thị chọn Kích cỡ (size)
  * B4.1. Kiểm tra thuộc tính size (if size is not null or size is not empty)
  * B4.2. Lấy danh sách các giá trị size và đếm số lượng.
  * B5. Tạo vòng lặp hiển thị từng size
  * B6. Nếu không có thuộc tính màu và size thì hiển thị dropdown chọn sản phẩm con
  * B7. Nếu không có thuộc tính nào được hiển thị và có sản phẩm con thì tạo dropdown.
  * B8. Tạo Vòng lặp sản phẩm con
  * B8.1. Mỗi option chứa ID sản phẩm con, giá, và ảnh tương ứng

```
{% raw %}
    {% set variableAttributes = product.variableAttributes %}
    {% set color = variableAttributes['color'] %}
    {% set size = variableAttributes['size'] %}
    {% set flag=0 %}
    {% if color is not null or color is not empty %}
        {% set valuesColor = color.childValues %}
        {% set numbC =  (valuesColor | length) %}
        {% if(valuesColor is not null and numbC>0) %}
            {% set flag = flag + 1 %}
            <div class="req _colorSelect" column="{{ color.column }}">
              <span>Màu sắc</span>
              {% for attrValue in valuesColor %}
                 {% set arrColor = [] %}
                 {% set arrColor = arrColor|merge({ (color.column): attrValue.id }) %}
                 {% set img = getAttrValueImage(arrColor,false, {'return':'image','product':product}) %}
                 {% set pIdsAttrStr = getAttrValueImage(arrColor,true,{'product':product}) | json_encode() %}
                 {% set pIdsAttrStr = pIdsAttrStr | replace({'[': '', ']': ''}) %}
                 <a class="_pSelect {{ (numbC == 1) ?'active':'' }}" data-psId="{{ pIdsAttrStr }}" data-id="{{ attrValue.id }}" data-src="{{ img }}">
                       {{ attrValue.name }}
                  </a>
              {% endfor %}
            </div>
        {% endif %}
    {% endif %}
    {% if size is not empty %}
        {% set valuesSize = size.childValues %}
        {% set numbS = (valuesSize | length) %}
         {% if(valuesSize is not null and numbS>0) %}
             {% set flag = flag + 1 %}
             <span>Kích cỡ</span>
             <div class="req _sizeSelect" data-column="{{ size.column }}">
                {% for attrValueC in valuesSize %}
                      <a data-id="{{ attrValueC.id }}" class="{{ ((numbS == 1) ? 'active' : '') }}">
                           {{ attrValueC.name }}
                      </a>
                {% endfor %}
            </div>    
         {% endif %}
    {% endif %}
    {% if((flag==0) and (product.childs)) %}
      {% set flagchilds= product.childs|length %}
         <select class="childProducts">
             <option value="1">Chọn sản phẩm</option>
             {% set name_parent = product.name %}
             {% for cp in product.childs %}
                <option value="{{ cp.id }}, {{ cp.price }}"
                       href="{{ cp.imageUri }}"
                         data-src="{{ cp.imageUri }}">
                    { cp.name|replace({ name_parent :''}) }}
                </option>
             {% endfor %}
         </select>
    {% endif %}
{% endraw %}
```

### Số lượng sản phẩm

Số lượng sản phẩm sẽ được tùy chỉnh theo ý muốn của khách hàng và sẽ thường gồm nút tăng, giảm, ô để nhập số lượng. Số lượng sản phẩm sẽ được gọi ra như sau:

```
{% raw %}
<div class="_quantityCart">
    <a class="_subtract" data-id="{{ product.id }}">
         <i class="fal fa-minus"></i>
    </a>
    <input class="_numberProduct" max="{{ product.available }}" min="1"
               type="number" value="1" psId="{{ product.id }}">
    <a class="_plus" data-id="{{ product.id }}">
          <i class="fal fa-plus"></i>
     </a>
</div>
{% endraw %}
```

### Nút thêm sản phẩm vào giỏ hàng và nút mua ngay

Nút thêm sản phẩm vào giỏ hàng và nút mua ngay sẽ được gọi ra như sau:

```
{% raw %}
    {% if(ivt <= 0) %}
        <a class="_addToCart" data-psid="{{ product.id }}">
               <i class="far fa-shopping-cart"></i>
            {{ translate('Sản phẩm tạm hết hàng') }}
        </a>
        <a class="_buyNow" data-psid="{{ product.id }}">
             {{ translate('Sản phẩm tạm hết hàng') }}
        </a>
    {% else%}
        {% if (flag > 0) %}
         <a class="_addToCart" title="{{ translate('Vui lòng chọn màu sắc hoặc kích cỡ') }}!" data-ck="0" data-psid="{{ product.id }}" data-selId="{{ product.id }}" >
               <i class="far fa-shopping-cart"></i>
               {{ translate('Thêm vào giỏ hàng') }}
         </a>
         <a class="_buyNow" title="{{ translate('Vui lòng chọn màu sắc hoặc kích cỡ') }}!" data-ck="0" data-psid="{{ product.id }}" data-selId="{{ product.id }}" >
             {{ translate('Mua ngay') }}
         </a>
        {% else %}
         <a class="_addToCart" data-ck="1" data-psid="{{ product.id }}" data-selId="{{ product.id }}" >
             <i class="far fa-shopping-cart"></i>
            {{ translate('Thêm vào giỏ hàng') }}
         </a>
         <a class="_buyNow" data-ck="1" data-psid="{{ product.id }}" data-selId="{{ product.id }}" >
              {{ translate('Mua ngay') }}
         </a>
     {% endif %}
    {% endif %}
{% endraw %}
```

### Mô tả sản phẩm

Mô tả sản phẩm là phần mô tả ngắn của sản phẩm sẽ được thêm trong trang quản trị của khách hàng.

<figure><img src="../../.gitbook/assets/image (45).png" alt=""><figcaption></figcaption></figure>

Mô tả sản phẩm được gọi ra như sau:

```
{% raw %}
    {{ product.description | raw }}
{% endraw %}
```

### Chi tiết bài viết sản phẩm

Chi tiết sản phẩm là phần bài viết chi tiết của sản phẩm sẽ được thêm trong trang quản trị của khách hàng.

<figure><img src="../../.gitbook/assets/image (43).png" alt=""><figcaption></figcaption></figure>

Chi tiết sản phẩm được gọi ra như sau:

```
{% raw %}
    {{ product.content| raw }}
{% endraw %}
```

### Sản phẩm liên quan

Lấy ra những sản phẩm upSale của sản phẩm hiện tại. Người dùng có thể tự thêm sản các sản phẩm đó vào sản phẩm hiện tại
* Cách làm:
  * B1. Lấy tối đa sản phẩm upSale param limit, ID sản phẩm param productId ở hàm getRelatedProducts().
  * B2. Kiểm tra có dữ liệu không (if getRelatedProducts is not empty)
  * B3. Vòng lặp hiển thị sản phẩm: ảnh, tên, giá, đánh giá, nút hành động
  * B4. Nếu có giảm giá, hiển thị phần trăm giảm giá
  * B5. Nút hành động: thêm vào giỏ, yêu thích, xem nhanh (Thêm thuộc tính data-id="{{ pu.id }}")
  * B6. Hiển thị giá theo điều kiện (liên hệ, giảm giá, giá gốc)
  
```
{% raw %}
    {% set productUpSale = getRelatedProducts({'productId': product.id, 'limit':8}) %}
    {% if(productUpSale is not empty) %}
        {% for pu in productUpSale %}
             {{ pu.thumbnailUri }}
             {{ pu.viewLink }}
             {{ pu.name}}
             
             {% if(pu.calcDiscountPercent > 0) %}
                    {{ pu.calcDiscountPercent }}%
             {% endif %}   
             {% if(pu.contactPrice or (pu.price == 0)) %}   
                   Liên hệ
             {% elseif pu.priceAfterDiscount > 0 %}
                  {{ pu.priceAfterDiscount | number_format(0) }}₫
                  {{ pu.price | number_format(0) }}₫
             {% elseif (pu.oldPrice > 0) %}
                    {{ pu.price | number_format(0) }}₫
                    {{ pu.oldPrice | number_format(0) }}₫
             {% else %}
                     {{ pu.price | number_format(0) }}₫
             {% endif %}
        {% endfor %}
    {% endif %}
{% endraw %}
```

### Sản phẩm tương tự

Lấy ra những sản phẩm thuộc cùng 1 danh mục

* Cách làm:
  * B1. Lấy tối đa sản phẩm thuộc cùng 1 danh mục param limit, ID danh mục theo param categoryId, loại trừ sản phẩm hiện tại theo param excludedIds ở hàm searchProducts().
  * B2. Kiểm tra có dữ liệu không (if searchProducts is not empty)
  * B3. Vòng lặp hiển thị sản phẩm: ảnh, tên, giá, đánh giá, nút hành động
  * B4. Nếu có giảm giá, hiển thị phần trăm giảm giá
  * B5. Nút hành động: thêm vào giỏ, yêu thích, xem nhanh (Thêm thuộc tính data-id="{{ n.id }}")
  * B6. Hiển thị giá theo điều kiện (liên hệ, giảm giá, giá gốc)

```
{% raw %}
    {% set productRelated = searchProducts({'limit':5, 'categoryId':product.categoryId,'excludedIds': product.id}) %}
    {% if(productRelated is not empty) %}
        {% for n in productRelated %}
             {{ n.thumbnailUri }}
             {{ n.viewLink }}
             {{ n.name}}
             
             {% if(n.calcDiscountPercent > 0) %}
                    {{ n.calcDiscountPercent }}%
             {% endif %}   
             {% if(n.contactPrice or (n.price == 0)) %}   
                   Liên hệ
             {% elseif n.priceAfterDiscount > 0 %}
                  {{ n.priceAfterDiscount | number_format(0) }}₫
                  {{ n.price | number_format(0) }}₫
             {% elseif (n.oldPrice > 0) %}
                    {{ n.price | number_format(0) }}₫
                    {{ n.oldPrice | number_format(0) }}₫
             {% else %}
                     {{ n.price | number_format(0) }}₫
             {% endif %}
        {% endfor %}
    {% endif %}
{% endraw %}
```

### Sản phẩm đã xem

Lấy ra những sản phẩm người dùng đã xem

* Cách làm:
  * B1. Lấy tối đa sản phẩm đã xem param limit từ getHistory().
  * B2. Kiểm tra có dữ liệu không (if lastProduct is not empty)
  * B3. Vòng lặp hiển thị sản phẩm: ảnh, tên, giá, đánh giá, nút hành động
  * B4. Nếu có giảm giá, hiển thị phần trăm giảm giá
  * B5. Nút hành động: thêm vào giỏ, yêu thích, xem nhanh (Thêm thuộc tính data-id="{{ ls.id }}")
  * B6. Hiển thị giá theo điều kiện (liên hệ, giảm giá, giá gốc)

```
{% raw %}
    {% set lastProduct = getHistory({'limit':5}) %}
    {% if lastProduct is not empty %}
        {% for ls in lastProduct %}
             {{ ls.thumbnailUri }}
             {{ ls.viewLink }}
             {{ ls.name}}
             
             {% if(ls.calcDiscountPercent > 0) %}
                    {{ ls.calcDiscountPercent }}%
             {% endif %}   
             {% if(ls.contactPrice or (ls.price == 0)) %}   
                   Liên hệ
             {% elseif n.priceAfterDiscount > 0 %}
                  {{ ls.priceAfterDiscount | number_format(0) }}₫
                  {{ ls.price | number_format(0) }}₫
             {% elseif (n.oldPrice > 0) %}
                  {{ ls.price | number_format(0) }}₫
                  {{ ls.oldPrice | number_format(0) }}₫
             {% else %}
                  {{ ls.price | number_format(0) }}₫
             {% endif %}
        {% endfor %}
    {% endif %}
{% endraw %}
```

### Lấy tổng hợp đánh giá của sản phẩm

Lấy tổng hợp đánh giá của sản phẩm (Đã làm tròn lên): Số lượt đánh giá, trung bình đánh giá

* Cách làm:
  * B1. Lấy số lượt đánh giá theo ID sản phẩm ở hàm countRating()
  * B2. Lấy trung bình đánh giá theo ID sản phẩm ở hàm getSummaryRating()
  * B3. Gán biến totalAvgRate để làm tròn trung bình đánh giá
  * B4. Nếu có đánh giá (totalAvgRate > 0)
  * B4.1. Hiển thị sao vàng (đã đánh giá), vòng lặp từ 1 đến totalAvgRate để hiển thị biểu tượng sao vàng (<i class="fas fa-star"></i>)
  * B4.2. Hiển thị sao trắng (chưa đánh giá) nếu nhỏ hơn 5 sao, vòng lặp thêm sao trắng để đủ 5 sao.
  * B5. Trường hợp chưa có đánh giá
  * B5.1. Nếu chưa có đánh giá (totalAvgRate <= 0), hiển thị 5 sao trắng.
  * B6. Hiển thị số lượt đánh giá

```
{% raw %}
    {% set totalRate = countRating({'itemId': product.id , 'type': 1}) %}
    {% set avgRate = getSummaryRating({'itemId':product.id}).rate %}
    
    {% set totalAvgRate = avgRate.rate ? avgRate.rate|round : 0 %}
    {% if totalAvgRate > 0 %}
       {% for i in range(1, totalAvgRate) %}
          <i class="fas fa-star"></i>
       {% endfor %}
    {% if totalAvgRate < 5 %}
       {% for i in range(1, 5 - totalAvgRate) %}
          <i class="far fa-star"></i>
       {% endfor %}
    {% endif %}
    {% else %}
       {% for i in range(1, 5) %}
          <i class="far fa-star"></i>
       {% endfor %}
    {% endif %}
    {{ totalRate }}
{% endraw %}
```

### Form đánh giá 

Lấy ra 1 form để người dùng có thể đánh giá mặc định có sẵn
```
{% raw %}
{{ render_embedRating({'productId': product.id}) }}
{% endraw %}
```

### Lấy ra các comment đánh giá

Lấy ra danh sách các đánh giá để hiển thị: Comment, số sao, ảnh ...
```
{% raw %}
    render_embedRatingComment({'productId': product.id,'limit': 3 }
{% endraw %}
```

<figure><img src="../../.gitbook/assets/image (54).png" alt=""><figcaption></figcaption></figure>
