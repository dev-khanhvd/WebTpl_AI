# Trang chủ

## Giới thiệu

Trang chủ hay còn gọi là “Homepage” là trang đầu tiên khi người dùng truy cập vào website của bạn. Đây là trang web mặc
định khi bạn truy cập vào địa chỉ website thì chỉ chứa tên miền đó.

Mục đích của trang chủ trên website là giúp điều hướng người dùng đến các trang khác bằng cách nhấp vào các liên kết hay
các danh mục trên trang chủ hoặc gõ vào thanh tìm kiếm trên trang. Từ đó, bạn sẽ được chuyển hướng đến các trang đích.

Trang chủ của 1 website cơ bản thì sẽ bao gồm các nội dung sau:

### Thẻ meta trang chủ

Thẻ Meta là các đoạn văn bản mô tả nội dung của trang, các thẻ này không xuất hiện trên chính trang mà chỉ xuất hiện
trong phần mã nguồn của trang. Về cơ bản chúng giúp cho các công cụ tìm kiếm hiểu rõ hơn về nội dung của một trang web,
do vậy rất tốt cho SEO.

Dưới đây là cách thức lấy thẻ meta trang chủ của website:

```
{% raw %}
{% block meta %}
    {{ headTitle('Trang chủ').setSeparator(' - ').setAutoEscape(false)|raw }}
    <meta name="keywords" content="Trang chủ">
    <meta name="description" content="Trang chủ">
    <link rel="canonical" href="{{ getCurrentUrl(true) }}" />
    <meta property="og:url" content="{{ getCurrentUrl(true) }}">
    <meta property="og:image" content="{{ getBusinessLogo() }}">
    <meta property="og:type" content="website">
    <meta property="og:title" content="Trang chủ">
{% endblock %}
{% endraw %}
```

### Banner trang chủ

Banner website có thể hiểu là những ô vuông trên đó có slogan, logo, ký hiệu và các thông điệp được đặt trên những vị
trí bắt mắt của một website, giúp thu hút lượng người truy cập qua đó vào website để nâng cao doanh số bán hàng.

Dưới đây là cách thức lấy banner trang chủ của website:

* Cách làm:
  * B1. Lấy danh sách banner bằng getBannerByPositionCode()
  * B2. Kiểm tra có dữ liệu không (if banner_home is not empty)
  * B3. Lặp qua danh sách banner và hiển thị từng banner
  
```
{% raw %}
{% set banner_home = getBannerByPositionCode('BANNER_HOME') %}
{% if(banner_home is not empty) %}
     {% for c in banner_home %}
        {{ c.viewLink }}
        {{ c.imageSrc }}
        {{ c.target }}
        {{ c.name }}
        {{ c.intro }}
        {{ c.description }}
    {% endfor %}
{% endif %}
{% endraw %}
```

### Banner limit trên trang chủ

Banner dạng này thì chỉ dùng cho 1 số chỗ để tối đa là bao nhiêu banner trên 1 block. 
Dưới đây là cách thức lấy banner có giới hạn số lượng của website:_

* Cách làm:
  * B1. Gọi hàm getCurrentBannerByCode với tham số 'BANNER_HOME' và giới hạn theo người dùng đặt ra (limit)
  * B2. Kiểm tra có dữ liệu không (if banner_home is not empty)
  * B3. Vòng lặp qua các phần tử trong banner_home.
  * B4. Fill code với các giá trị tương ứng
  
```
{% raw %}
{% set banner_home = getCurrentBannerByCode('BANNER_HOME', {'limit':2}) %}
{% if(banner_home is not empty) %}
     {% for c in banner_home %}
        {{ c.viewLink }}
        {{ c.imageSrc }}
        {{ c.target }}
        {{ c.name }}
        {{ c.intro }}
        {{ c.description }}
    {% endfor %}
{% endif %}
{% endraw %}
```

Trong đó <mark style="color:red;">`BANNER_HOME`</mark> là mã vị trí của banner (có thể thay đổi tên tùy theo vị trí cũng
như chức năng của từng banner) sẽ được tạo trong trang quản trị website.

<figure><img src="../.gitbook/assets/image (42).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (23).png" alt=""><figcaption><p>Banner trang chủ</p></figcaption></figure>


### Sản phẩm trang chủ 

Người dùng có thể lựa chọn các sản phẩm muốn hiện ở trang chủ theo dạng tick để hiển thị ra sản phẩm

Có 3 dạng tick để hiển thị trên trang chủ: tick trang chủ, tick mới hoặc tick hot
Dưới đây là cách thức lấy sản phẩm được tick của website:

* Cách làm:
  * B1. Lấy tối đa sản phẩm tick theo param limit từ searchProducts().
  * B2. Nếu có param showHot,showHome, showNew thì thêm param này vào searchProducts().
  * B3. Kiểm tra có dữ liệu không (if homeProduct is not empty)
  * B4. Vòng lặp hiển thị sản phẩm: ảnh, tên, giá, đánh giá, nút hành động
  * B5. Nếu có giảm giá, hiển thị phần trăm giảm giá
  * B6. Nút hành động: thêm vào giỏ, yêu thích, xem nhanh (Thêm thuộc tính data-id="{{ np.id }}")
  * B7. Hiển thị giá theo điều kiện (liên hệ, giảm giá, giá gốc)

```
{% raw %}
{% set homeProduct = searchProducts({'limit':8,'showHome':1}) %}
{% if homeProduct is not empty %}
      {% for n in homeProduct %}
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

Những sản phẩm được tick trên trang chủ sẽ hiển thị tại đây

<figure><img src="../.gitbook/assets/image (49).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (27).png" alt=""><figcaption><p>Sản phẩm được tick trang chủ</p></figcaption></figure>

### Chương trình promotion
Là nơi để thể hiện chương trình khuyến mãi và có đếm ngược theo ID của chương trình khuyến mãi đang chạy
Dưới đây là cách thức lấy chương trình khuyến mãi và sản phẩm theo chương trình khuyến mãi đó:

* Cách làm:
  * B1. Lấy giá trị promotionId từ getKeyContentValue('PROMOTION_ID')
  * B2. Kiểm tra nếu tồn tại promotionId (if promotionId is not null)
  * B3. Lấy danh sách promotion theo promotionId từ hàm getPromotions()
  * B4. Kiểm tra nếu danh sách promotion (if promotion is not empty)
  * B5. Gán phần tử đầu tiên của promotion vào biến promotionObj
  * B6. Hiển thị thông tin chương trình khuyến mãi: {{ promotionObj.name }},{{ promotionObj.viewLink }},{{ promotionObj.bannerUri }},{{ promotionObj.startDate }},{{ promotionObj.endDate }}
  * B7. Cung cấp nút "Xem tất cả" để link promotionObj.viewLink
  * B8. Lấy tối đa sản phẩm trong chương trình khuyến mãi theo param limit từ getPromotionProduct().
  * B9. Kiểm tra có dữ liệu không (if promotionProduct is not empty)
  * B10. Duyệt từng sản phẩm trong danh sách: ảnh, tên, giá, đánh giá, nút hành động
  * B11. Nếu có giảm giá, hiển thị phần trăm giảm giá
  * B12. Nút hành động: thêm vào giỏ, yêu thích, xem nhanh (Thêm thuộc tính data-id="{{ p.id }}")
  * B13. Hiển thị giá theo điều kiện (liên hệ, giảm giá, giá gốc) 
```
{% raw %}
{% set promotionId = getKeyContentValue('PROMOTION_ID') | e('html') %}
{% if promotionId is not null %}
    {% set promotion = getPromotions({'id':promotionId,'limit':1}) %}
    {% if(promotion is not empty) %}
        {% set promotionObj = promotion|first %}
        {{ promotionObj.name }}
        {{ promotionObj.viewLink }}
        {{ promotionObj.bannerUri }}
        {{ promotionObj.startDate }}
        {{ promotionObj.endDate }}
        {% set promotionProduct = getPromotionProduct({'id':promotionObj.id,'limit':12}) %}
        {% if(promotionProduct is not empty) %}
           {% for p in promotionProduct %}
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
        % endif %}
    {% endif %}
{% endif %}
{% endraw %}
```

### Tạo nút yêu thích cho sản phẩm

```
{% raw %}
<div class="_addWishList" data-id="{{ productId }}">
    <i class="fa-thin fa-heart"></i>
</div>
{% endraw %}
```

<figure><img src="../.gitbook/assets/image (28).png" alt=""><figcaption><p>Nút yêu thích và thuộc tính màu sắc của sản phẩm</p></figcaption></figure>

### Danh mục sản phẩm trang chủ

Ngay trên trang chủ, người dùng có thể nhìn thấy và truy cập nhanh vào các danh mục sản phẩm nổi bật.
Mục tiêu: Giúp người dùng dễ dàng chọn đúng nhóm sản phẩm họ quan tâm chỉ với một cú nhấp chuột.

Dưới đây là cách thức lấy danh mục sản phẩm của website:
* Cách làm:
  * B1. Lấy danh mục từ hàm getCategories().
  * B2. Kiểm tra có dữ liệu không (if category is not empty)
  * B3. Vòng lặp hiển thị danh mục: link,tên,ảnh đại diện,icon
  * B4. Nếu có danh mục con, tiếp tục lặp
  * B5. Hiển thị thông tin danh mục con: link,tên,ảnh đại diện,icon

```
{% raw %}
{% set category = getCategories() %}
{% if category is not empty %}
    {% for c in category %}
        {{ c.viewLink }}
        {{ c.name }}
        {{ c.imageUri }}
        {{ c.iconUri }}
        {% if c.childs %}
          {% for c1 in c.childs %}
            {{ c1.viewLink }}
            {{ c1.name }}
            {{ c1.imageUri }}
            {{ c1.iconUri }}
          {% endfor %}
        {% endif%}
    {% endfor %}
{% endif%}
{% endraw %}
```

<figure><img src="../.gitbook/assets/image (24).png" alt=""><figcaption><p>Ảnh đại diện danh mục sản phẩm</p></figcaption></figure>

### Danh mục tự tạo

Người dùng có thể tự tạo và sắp xếp các danh mục cho menu website theo ý muốn, thay vì phải sử dụng các danh mục mặc định.
Điều này giúp bạn dễ dàng tổ chức nội dung theo cách riêng, phù hợp với nhu cầu và cấu trúc website của mình.

Dưới đây là cách thức lấy danh mục tự tạo của website:

* Cách làm:
  * B1. Lấy danh mục từ hàm getMenus({'type':'header'}).
  * B2. Kiểm tra có dữ liệu không (if menu is not empty)
  * B3. Vòng lặp hiển thị danh mục: link,tên,ảnh đại diện,icon
  * B4. Nếu m.type nằm trong arrTypeCate, gọi hàm getCategoryTypeMenu(m.type) để lấy danh mục tương ứng kiểu và gán vào categoryCustom:
    * B4.1. Nếu categoryCustom không rỗng if(categoryCustom is not empty)
    * B4.2. Duyệt qua từng danh mục c trong categoryCustom: link,tên,ảnh đại diện,icon
    * B4.3. Nếu c có childs, duyệt tiếp và hiển thị viewLink + name của từng c1.
  * B5. Nếu m.type KHÔNG nằm trong arrTypeCate
    * B5.1. Hiển thị: link,tên,ảnh đại diện,icon
    * B5.2. Nếu m có childs, duyệt và hiển thị viewLink + name của từng c1.
  
```
{% raw %}
{% set menu = getMenus({'type':'header'}) %}
{% if(menu is not empty) %}
    {% for m in menu %}
        {% set arrTypeCate = m.typeCates %}
        {% if m.type in arrTypeCate %}
            {% set categoryCustom = getCategoryTypeMenu(m.type) %}
            {% if(categoryCustom is not empty) %}
                {% for c in categoryCustom %}
                    {{ c.viewLink }}
                    {{ c.name }}
                    {% if(c.iconUri) %}
                        {{ c.iconUri }}
                    {% endif %}
                    {% if(c.childs) %}
                        {% for c1 in c.childs %}
                            {{ c1.viewLink }}
                            {{ c1.name }}
                        {% endfor %}
                    {% endif %}
                {% endfor %}
            {% endif %}
        {% else %}
            {{ m.viewLink }}
            {{ m.name }}
            {% if(m.iconUri) %}
                {{ m.iconUri }}
            {% endif %}
            {% if(m.childs) %}
                {% for c1 in m.childs %}
                    {{  c1.viewLink }}
                    {{  c1.name }}
                {% endfor %}
            {% endif %}
        {% endif %}
    {% endfor %}
{% endif %}
{% endraw %}
```
### Thương hiệu
Hiển thị danh sách các thương hiệu mà doanh nghiệp đang phân phối hoặc kinh doanh.
Mỗi thương hiệu sẽ được trình bày với tên, logo và liên kết đến trang chi tiết.

Dưới đây là cách thức lấy thương hiệu:
* Cách làm:
  * B1. Lấy tối đa thương hiệu theo param limit từ loadListBrands().
  * B2. Kiểm tra có dữ liệu không (if l_brand is not empty)
  * B3. Vòng lặp hiển thị thương hiệu: ảnh, tên, link
  * B4. Kiểm tra nếu thương hiệu có ảnh thì mới hiển thị (if b.imageUri is not empty)
```
{% raw %}
 {% set l_brand = loadListBrands({'limit':10}) %}
    {% if l_brand not empty) %}
        {% for b in l_brand %}
          {% if b.imageUri is not empty %}
           {{ b.name | raw }}
           {{ b.viewLink }}
           {{ b.imageUri }}   
          {% endif %}
        {% endfor %}
    {% endif %}
{% endraw %}
```
### Bộ sưu tập album ảnh

Khu vực này cho phép người dùng truy cập nhanh đến các bộ sưu tập ảnh yêu thích.
Mỗi album có thể chứa nhiều ảnh và được trình bày với thông tin chi tiết.

Dưới đây là cách thức lấy ra danh sách bộ sưu tập của website:
 
* Cách làm:
  * B1. Lấy tối đa album theo param limit từ searchAlbum().
  * B2. Kiểm tra có dữ liệu không (if album is not empty)
  * B3. Vòng lặp hiển thị album: ảnh, tên, link, mô tả
```
{% raw %}
{% set albumHome = searchAlbum({'limit': 5}) %}
    {% if(albumHome is not null or albumHome is not empty) %}
        {% for a in albumHome %}
           {{ a.name }}
           {{ a.description |raw }}   
           {{ a.viewLink }}
           {{ a.thumbnailUri }}   
        {% endfor %}
    {% endif %}
{% endraw %}
```
### Tag sản phẩm trong bộ sưu tập

Sẽ lấy ra danh sách các sản phẩm được tag vào từng ảnh trong album
Dưới đây là cách thức lấy tag sản phẩm của mỗi album trên website:

Chú ý: a.id => là id của albumHome được khai báo ở trên
```
{% raw %}

{% set albumItems = getAlbumItems(a.id,{'limit': 4}) %}
   {% if(albumItems is not null or albumItems is not empty) %}
        {% for b in albumItems %}
           {{ a.viewLink }}
           {{ b.imageUri }}
           {{ b.description | striptags }}
        {% endfor %}
    {% endif %}
{% endraw %}
```

<figure><img src="../.gitbook/assets/image (29).png" alt=""><figcaption><p>Bộ sưu tập</p></figcaption></figure>

### Danh sách bài viết tin tức

Lấy ra danh sách các bài viết tin tức để hiển thị trên website
Dưới đây là cách thức lấy bài viết tin tức trên website:
* Cách làm:
  * B1. Lấy tối đa bài viết tin tức theo param limit từ getLastestNews().
  * B2. Kiểm tra có dữ liệu không (if lastestNews is not empty)
  * B3. Vòng lặp hiển thị tin tức bao gồm: ảnh, tên, link, title, giới thiệu, ngày tạo
```
{% raw %}
{% set lastestNews= getLastestNews({'limit':5}) %}
{% if(lastestNews is not empty) %}
    {% for i in lastestNews %}
        {{ i.viewLink }}
        {{ i.pictureUri }}
        {{ i.title  | striptags }}
        {{ i.intro | striptags  }}
        {{ i.createdDateTime|date("d-m-Y") }}
    {% endfor %}
{% endif %}
{% endraw %}
```

<figure><img src="../.gitbook/assets/image (30).png" alt=""><figcaption><p>Tin tức</p></figcaption></figure>

### Danh sách mã voucher

Lấy ra danh sách các mã coupon theo các chương trình coupon đã cài đặt trong hệ thống. Tối đa lấy đuợc 4 chương trình

* Cách làm:
  * B1. Lấy tối đa chương trình voucher theo param limit từ getListCoupon().
  * B2. Kiểm tra có dữ liệu không (if couponLst is not empty)
  * B3. Lặp qua từng voucher, hiển thị thông tin cơ bản của voucher
  * B4. Kiểm tra voucher đó có danh sách coupon không
  * B5. Lặp qua từng mã coupon trong voucher, hiển thị thông tin của coupon đó
```
{% raw %}
{% set voucher = getListCoupon({'couponLimit':4}) %}
{% if voucher is not empty  %}
   {% for v in voucher %}
      {{ v.id }}
      {{ v.value|number_format(0) }}
     {% if(v.couponCode is not empty) %}
        {% for v_child in v.couponCode %}
            {{ v_child.value }}
            {{ v_child.description }}
            {{ v.startDate }}
            {{ v.endDate }}
            {{ v_child.code }}
        {% endfor %}
     {% endif %}
  {% endfor %}
{% endif %}
{% endraw %}
```
