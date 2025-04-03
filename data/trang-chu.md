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

Trong đó <mark style="color:red;">`BANNER_HOME`</mark> là mã vị trí của banner (có thể thay đổi tên tùy theo vị trí cũng
như chức năng của từng banner) sẽ được tạo trong trang quản trị website.

<figure><img src="../.gitbook/assets/image (42).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (23).png" alt=""><figcaption><p>Banner trang chủ</p></figcaption></figure>

### Danh mục sản phẩm

Để người dùng có thể chuyển hướng đến các danh mục sản phẩm mình thích được nhanh chóng hơn.

Dưới đây là cách thức lấy danh mục sản phẩm của website:

```
{% raw %}
{% set category = getCategories() %}
{% if category is not empty %}
    {% for c in category %}
        {{ c.viewLink }}
        {{ c.name }}
        {{ c.imageUri }}
    {% endfor %}
{% endif%}
{% endraw %}
```

<figure><img src="../.gitbook/assets/image (24).png" alt=""><figcaption><p>Ảnh đại diện danh mục sản phẩm</p></figcaption></figure>

### Sản phẩm mới
```
{% raw %}
{% set newProduct = searchProducts({'limit':8,'showNew':1}) %}
{% if newProduct is not empty %}
      {% for np in newProduct %}
         {{ np.thumbnailUri }}
         {{ np.viewLink }}
         {{ np.name}}
         
         {% if(np.calcDiscountPercent > 0) %}
                {{ h.calcDiscountPercent }}%
         {% endif %}
         {% if(np.contactPrice or (np.price == 0)) %}   
               Liên hệ
         {% elseif np.priceAfterDiscount > 0 %}
              {{ np.priceAfterDiscount | number_format(0) }}₫
              {{ np.price | number_format(0) }}₫
         {% elseif (np.oldPrice > 0) %}
                {{ np.price | number_format(0) }}₫
                {{ np.oldPrice | number_format(0) }}₫
         {% else %}
                 {{ np.price | number_format(0) }}₫
         {% endif %}
      {% endfor %}
    {% endif %}
{% endraw %}
```

Những sản phẩm được tích sản phẩm mới sẽ hiển thị tại đây

<figure><img src="../.gitbook/assets/image (47).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (25).png" alt=""><figcaption><p>Sản phẩm mới</p></figcaption></figure>

### Sản phẩm hot
```
{% raw %}
{% set hotProduct = searchProducts({'limit':8,'showHot':1}) %}
{% if hotProduct is not empty %}
      {% for hp in hotProduct %}
         {{ hp.thumbnailUri }}
         {{ hp.viewLink }}
         {{ hp.name}}
         
         {% if(hp.calcDiscountPercent > 0) %}
                {{ hp.calcDiscountPercent }}%
         {% endif %}   
          {% if(hp.contactPrice or (hp.price == 0)) %}   
               Liên hệ
         {% elseif hp.priceAfterDiscount > 0 %}
              {{ hp.priceAfterDiscount | number_format(0) }}₫
              {{ hp.price | number_format(0) }}₫
         {% elseif (hp.oldPrice > 0) %}
                {{ hp.price | number_format(0) }}₫
                {{ hp.oldPrice | number_format(0) }}₫
         {% else %}
                 {{ hp.price | number_format(0) }}₫
         {% endif %}
      {% endfor %}
    {% endif %}
{% endraw %}
```

Những sản phẩm được tích sản phẩm hot sẽ hiển thị tại đây

<figure><img src="../.gitbook/assets/image (46).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (26).png" alt=""><figcaption><p>Sản phẩm hot</p></figcaption></figure>


### Sản phẩm tick trang chủ 

Người dùng có thể lựa chọn các sản phẩm muốn hiện ở trang chủ theo dạng tick trang chủ để hiển thị ra sản phẩm 

Dưới đây là cách thức lấy sản phẩm được tick trang chủ của website:
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

Những sản phẩm được tích trang chủ sẽ hiển thị tại đây

<figure><img src="../.gitbook/assets/image (49).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (27).png" alt=""><figcaption><p>Sản phẩm được tick trang chủ</p></figcaption></figure>

### Sản phẩm giảm giá

```
{% raw %}
{% set discountProduct = searchProducts({'limit':8,'discount':1}) %}
{% if discountProduct is not empty %}
      {% for ds in discountProduct %}
         {{ ds.thumbnailUri }}
         {{ ds.viewLink }}
         {{ ds.name}}
         
         {% if(ds.calcDiscountPercent > 0) %}
                {{ ds.calcDiscountPercent }}%
         {% endif %}   
         {% if(ds.contactPrice or (ds.price == 0)) %}   
               Liên hệ
         {% elseif ds.priceAfterDiscount > 0 %}
              {{ ds.priceAfterDiscount | number_format(0) }}₫
              {{ ds.price | number_format(0) }}₫
         {% elseif (ds.oldPrice > 0) %}
                {{ ds.price | number_format(0) }}₫
                {{ ds.oldPrice | number_format(0) }}₫
         {% else %}
                 {{ ds.price | number_format(0) }}₫
         {% endif %}
      {% endfor %}
    {% endif %}
{% endraw %}
```

Những sản phẩm được nhập giá mới và giá cũ sẽ hiển thị tại đây

<figure><img src="../.gitbook/assets/image (44).png" alt=""><figcaption></figcaption></figure>


### Chương trình khuyến mãi
Là nơi để thể hiện danh sách sản phẩm theo chương trình khuyến mãi và có đếm ngược theo ID của chương trình khuyến mãi đang chạy
Dưới đây là cách thức lấy chương trình khuyến mãi và sản phẩm theo chương trình khuyến mãi đó:

* Cách làm:
  * B1. Lấy ID của chương trình khuyến mãi
  * B2. Nếu tồn tại, lấy dữ liệu khuyến mãi từ getPromotions()
  * B3. Hiển thị tiêu đề "Flash Deals"
  * B4. Thêm bộ đếm ngược dựa trên promotionObj.endDate
  * B5. Cung cấp nút "Xem tất cả" để link promotionObj.viewLink
  
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
    {% endif %}
{% endif %}
{% endraw %}
```
### Sản phẩm trong chương trình khuyến mãi
Sau khi lấy được chương trình khuyến mãi, thì dưới đây là cách lấy ra sản phẩm trong chương trình khuyến mãi đó

```
{% raw %}
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

### Danh sách bộ sưu tập

Là nơi để chuyển hướng nhanh đến bộ sưu tập sản phẩm mà người dùng yêu thích

Dưới đây là cách thức lấy banner bộ sưu tập của website:
 
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

### Bài viết tin tức

Luôn cập nhật những tin tức mới nhất lên trang web của bạn

Dưới đây là cách thức lấy tin tức của website:

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
