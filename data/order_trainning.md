# Thanh toán

## Các nội dung cơ bản của trang thanh toán

Trang thanh toán là trang cung cấp dịch vụ thanh toán cho đơn hàng đã được người dùng chọn vào giỏ hàng trước đó. Thanh toán là bước xác nhận cuối cùng để người dùng có thể thành công đặt được sản phẩm mình đã chọn mua.

### Các thẻ meta

```
{% raw %}
{% extends layout_empty %}
{% block meta %}
    {{ headTitle('Thanh toán').setSeparator(' - ').setAutoEscape(false)|raw }}
    <meta name="keywords" content="Thanh toán">
    <meta name="description" content="Thanh toán">
    <link rel="canonical" href="{{ getCurrentUrl(true) }}" />
    <meta property="og:url" content="{{ getCurrentUrl(true) }}">
    <meta property="og:image" content="https://dummyimage.com/300x200/000/fff">
    <meta property="og:type" content="website">
    <meta property="og:title" content="Thanh toán">
{% endblock %}
{% endraw %}
```

### Danh sách sản phẩm trang thanh toán

Trang thanh toán sẽ hiển thị một danh sách chi tiết các sản phẩm mà người dùng dự định mua. Mỗi sản phẩm sẽ bao gồm các thông tin sau: Hình ảnh của sản phẩm giúp người mua dễ dàng nhận diện, Mô tả ngắn gọn về sản phẩm để hiểu rõ hơn về đặc điểm và tính năng, Số lượng sản phẩm mà người dùng đã chọn, và Giá của từng sản phẩm. Thông tin này giúp người mua kiểm tra lại đơn hàng của mình trước khi tiến hành thanh toán.
Dưới đây là cách thức lấy sản phẩm:

* Cách làm:
  * B1. Lấy danh sách sản phẩm từ serviceCart().productList.
  * B2. Kiểm tra xem giỏ hàng có sản phẩm hay không (if products is not empty)
  * B3. Vòng lặp qua từng sản phẩm trong giỏ hàng
  * B4. Xử lý đơn vị sản phẩm (Nếu có)
  * B5. Tính toán tổng giá trị sản phẩm
  * B6. Hiển thị thông tin sẵn có của sản phẩm: : ảnh, tên - đơn vị sản phẩm, giá, số lượng, xóa
  * B7. Tính toán giá sau giảm giá hoặc giá gốc
  * B8. Nút hành động: Xóa sản phẩm trong giỏ (Thêm thuộc tính data-id="{{ p.id }}")

```
{% raw %}
{% set products = serviceCart().productList %}
{% if products is not empty %}
    {% for p in products %}
         {% set textUnit = '' %}
          {% if p.productUnit %}
              {% set textUnit = '(' ~ p.productUnit.name ~ ')'%}
          {% endif %}
           {% set moneyTotal = p.price * p.quantity %}
           {% if (p.priceAfterDiscount > 0) %}
                 {% set moneyTotal = p.priceAfterDiscount * p.quantity%}
           {% endif %}
           {{ p.viewLink }}
           {{ p.available }}
           {{ p.thumbnailUri }}
           {{ p.quantity }}
           {{ p.name }} {{ textUnit }}
           {% if (p.moneyDiscount) %}
                 {{ (p.priceAfterDiscount * p.quantity)|number_format(0) }}
           {% else %}
                {{ (p.price * p.quantity)|number_format(0) }}
           {% endif %}
            <p class="_removeCart" data-id="{{ p.id }}">Xóa</p>
    {% endfor %}
{% endif %}
{% endraw %}
```
### Lịch sử mua hàng:
Lịch sử mua hàng là danh sách ghi lại tất cả các đơn hàng mà khách hàng đã thực hiện trên website. Thông tin thường bao gồm mã đơn hàng, ngày mua, trạng thái xử lý, phương thức thanh toán và tổng giá trị. Chức năng này giúp người dùng dễ dàng theo dõi đơn hàng, kiểm tra lại các giao dịch trước đó
Dưới đây là cách thức lấy sử mua hàng:
* Cách làm:
  * B1. Lấy danh sách đơn hàng từ paginator.
  * B2. Kiểm tra có đơn hàng hay không (if paginator is not empty)
  * B3. Vòng lặp duyệt qua từng đơn hàng
  * B4. Hiển thị thông tin đơn hàng
  * B5. Lấy và hiển thị danh sách sản phẩm trong đơn hàng
  * B6. Hiển thị thông tin sẵn có của sản phẩm: : ảnh, tên - đơn vị sản phẩm, giá, số lượng, xóa
  * B6.1. Tính thành tiền cho sản phẩm (giá x số lượng)
  * B6.2. Cộng vào tổng giá trị đơn hàng.

```
{% raw %}
   {% if(paginator is not empty) %}
       {% for order in paginator %}
            {% set totalOrderPrice = 0 %}
            {{ order.id }}
            {{ order.createdDate | date("d/m/Y") }}
            {{ order.status }}
            {{ totalOrderPrice | number_format(0) }}
            {% set products = orders[order.id].products %}
            {% if(products is not empty) %}
                 {% for pOrder in products %}
                      {% set p = pOrder.product %}
                      {% set total = (pOrder.quantity * pOrder.price) %}
                      {% set totalOrderPrice = totalOrderPrice + (pOrder.quantity * pOrder.price) %}
                      {{ p.viewLink }}
                      {{ p.thumbnailUri }}
                      {{ p.name }}
                      {{ pOrder.quantity }}
                      {{ total | number_format(0) }}
                 {% endfor %}
            {% endif %}
      {% endfor %}
   {% endif %}
{% endraw %}
```
### Mã giảm giá

Mã giảm giá là một công cụ mà người dùng có thể áp dụng khi thanh toán để giảm giá trị đơn hàng. Khi có chương trình khuyến mãi hoặc ưu đãi, người dùng có thể nhập mã giảm giá vào ô tương ứng trên trang thanh toán. Sau khi áp dụng mã, tổng giá trị đơn hàng sẽ được điều chỉnh giảm theo tỷ lệ phần trăm hoặc số tiền cố định mà mã giảm giá quy định. Mã giảm giá giúp tăng sự hấp dẫn của các chương trình bán hàng, khuyến khích khách hàng mua sắm nhiều hơn.

```
  <span>{{ translate('Mã giảm giá') }}</span>
  <p class="_couponPrice"></p>
  
   <input type="text" class="_txtCoupon" placeholder="Nhập mã ưu đãi">
   <a class="_couponBtn">{{ translate('Áp dụng') }}</a>
{% endraw %}
```

### Số tiền cần thanh toán

Số tiền cần thanh toán cho mỗi đơn hàng bao gồm số tiền tạm tính và phí vận chuyển

```
{% raw %}
<span id="showTotalMoney" value="{{ totalCartMoney }}">
    {{ totalCartMoney |number_format(0) }} đ
</span>
{% endraw %}
```

### Thông tin giao hàng

Thông tin về người mua hàng sẽ được hiển thị chi tiết như: Tên, Số điện thoại, Email, Địa chỉ, Tỉnh thành phố, Quận huyện, Phường xã
Dưới đây là cách thức lấy thông tin giao hàng:
```
{% raw %}
<input aria-label="{{ translate('Họ và tên') }}" type="text" placeholder="{{ translate('Họ và tên') }}" class="validate[required] form-control" name="customerName" value="{{ user?user.fullname:'' }}">
<input aria-label="{{ translate('Điện thoại') }}" class="validate[required,custom[phone]] form-control" name="customerMobile" type="text" placeholder="{{ translate('Điện thoại') }}" value="{{ user ? (user.mobile | replace({'+84': '0'})):'' }}" required>
<input aria-label="Email" class="form-control" type="email" placeholder="Email" value="{{ user?user.email:'' }}" name="customerEmail">
<input aria-label="{{ translate('Địa chỉ') }}" type="text" placeholder="{{ translate('Địa chỉ') }}" class="validate[required] form-control" 
                                               value="{{ user?user.address:'' }}" name="customerAddress">
<select name="customerCityId" id="customcityId">
     <option value="">{{ translate('Chọn Tỉnh/ thành phố') }}</option>
     {% for city in cities %}
        <option value="{{ city.Id }}">
         {{ city.nativeName }}
        </option>
     {% endfor %}
 </select>
 
 <select name="customerDistrictId" id="customdistrictId"
        class="validate[required] form-control">
        <option>{{ translate('Chọn Quận/ Huyện') }}</option>
        {% if user and user.cityLocationId %}
            {% set dts = getDistrict(user.cityLocationId) %}
            {{ toSelectBox(dts, user.districtLocationId) }}
        {% endif %}
  </select>
  <select name="customerWardId" id="customerWardId"
         class="validate[required] form-control">
      <option>{{ translate('Chọn Phường/ Xã') }}</option>
       {% if user and user.districtLocationId %}
           {% set dts = getWard(user.districtLocationId) %}
           {{ toSelectBox(dts, user.districtLocationId) }}
       {% endif %}
    </select>
    <textarea aria-label="description" name="description"  placeholder="{{ translate('Ghi chú đơn hàng') }}" rows="3" ></textarea>
{% endraw %}

```


### Phương thức vận chuyển

Người dùng có thể chọn các phương thức vận chuyển cũng như các hãng vận chuyển như: Liên vùng, Giao nhanh, Giao chậm, Giao hỏa tốc...

```
{% raw %}
<span id="ship_fee" class="_ship_fee">0</span>
<span id="showCarrier"></span>
{% endraw %}
```

### Phương thức thanh toán

Người dùng có thể chọn các phương thức thanh toán mình muốn như: Thanh toán tại nhà, Thanh toán chuyển khoản, cũng như các nền tảng hộ trợ thanh toán online khác như VNPay hoặc MoMo.

```
{% raw %}
{{ getPayments() | raw }}
{% endraw %}
```