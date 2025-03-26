# Trang chủ

## Giới thiệu

Trang chủ hay còn gọi là “Homepage” là trang đầu tiên khi người dùng truy cập vào website của bạn. Đây là trang web mặc định khi bạn truy cập vào địa chỉ website thì chỉ chứa tên miền đó.

Mục đích của trang chủ trên website là giúp điều hướng người dùng đến các trang khác bằng cách nhấp vào các liên kết hay các danh mục trên trang chủ hoặc gõ vào thanh tìm kiếm trên trang. Từ đó, bạn sẽ được chuyển hướng đến các trang đích.

Trang chủ của 1 website cơ bản thì sẽ bao gồm các nội dung sau:

### Thẻ meta trang chủ

Thẻ Meta là các đoạn văn bản mô tả nội dung của trang, các thẻ này không xuất hiện trên chính trang mà chỉ xuất hiện trong phần mã nguồn của trang. Về cơ bản chúng giúp cho các công cụ tìm kiếm hiểu rõ hơn về nội dung của một trang web, do vậy rất tốt cho SEO.

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

Banner website có thể hiểu là những ô vuông trên đó có slogan, logo, ký hiệu và các thông điệp được đặt trên những vị trí bắt mắt của một website, giúp thu hút lượng người truy cập qua đó vào website để nâng cao doanh số bán hàng.

Dưới đây là cách thức lấy banner trang chủ của website:

```
{% raw %}
{% set banner_home = getBannerByPositionCode('BANNER_HOME') %}
{% if(banner_home is not empty) %}
    <div>
     {% for c in banner_home %}
        <a href="{{ c.viewLink }}">
            <img src="{{ c.imagesrc }}" alt="{{ c.name }}">
        </a>
    {% endfor %}
    </div>
{% endif %}
{% endraw %}
```

Trong đó <mark style="color:red;">`BANNER_HOME`</mark> là mã vị trí của banner (có thể thay đổi tên tùy theo vị trí cũng như chức năng của từng banner) sẽ được tạo trong trang quản trị website.

<figure><img src="../.gitbook/assets/image (42).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (23).png" alt=""><figcaption><p>Banner trang chủ</p></figcaption></figure>

### Banner danh mục sản phẩm

Để người dùng có thể chuyển hướng đến các danh mục sản phẩm mình thích được nhanh chóng hơn.

Dưới đây là cách thức lấy banner danh mục sản phẩm của website:

```
{% raw %}
{% set category = getCategories() %}
{% if category is not empty %}
    <div>
        {% for c in category %}
            <div>
                <a href="{{ c.viewLink }}">
                    <img alt="{{ c.name }}" src="{{ c.image }}">
                </a>
                <a href="{{ c.viewLink }}"><p>{{ c.name }}</p></a>
            </div>
        {% endfor %}
    <div>
{% endif%}
{% endraw %}
```

<figure><img src="../.gitbook/assets/image (24).png" alt=""><figcaption><p>Ảnh đại diện danh mục sản phẩm</p></figcaption></figure>

### Sản phẩm mới, hot, trang chủ, giảm giá

Là những sản phẩm mà người bán hàng muốn người dùng tiếp cận một cách nhanh chóng.

Dưới đây là cách thức lấy Sản phẩm hot, mới, trang chủ, giảm giá của website:

* Sản phẩm mới

```
{% raw %}
{% set newProduct = searchProducts({'limit':8,'showNew':1}) %}
{% endraw %}
```

Những sản phẩm được tích sản phẩm mới sẽ hiển thị tại đây

<figure><img src="../.gitbook/assets/image (47).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (25).png" alt=""><figcaption><p>Sản phẩm mới</p></figcaption></figure>

* Sản phẩm hot

```
{% raw %}
{% set hotProduct = searchProducts({'limit':8,'showHot':1}) %}
{% endraw %}
```

Những sản phẩm được tích sản phẩm hot sẽ hiển thị tại đây

<figure><img src="../.gitbook/assets/image (46).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (26).png" alt=""><figcaption><p>Sản phẩm hot</p></figcaption></figure>

* Sản phẩm trang chủ

```
{% raw %}
{% set homeProduct = searchProducts({'limit':8,'showHome':1}) %}
{% endraw %}
```

Những sản phẩm được tích trang chủ sẽ hiển thị tại đây

<figure><img src="../.gitbook/assets/image (49).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../.gitbook/assets/image (27).png" alt=""><figcaption><p>Sản phẩm được tick trang chủ</p></figcaption></figure>

* Sản phẩm giảm giá (Trừ các sản phẩm đang chạy CTKM)

```
{% raw %}
{% set homeProduct = searchProducts({'limit':8,'discount':1}) %}
{% endraw %}
```

Những sản phẩm được nhập giá mới và giá cũ sẽ hiển thị tại đây

<figure><img src="../.gitbook/assets/image (44).png" alt=""><figcaption></figcaption></figure>

Ví dụ một block hoàn chỉnh lấy sản phẩm:

```
{% raw %}
{% set newProduct = searchProducts({'limit':8,'showNew':1}) %}
    {% if newProduct is not empty %}
        <div >
            {% for n in newProduct %}
                {% set priceDiscount = n.priceAfterDiscount %}
                {% set percent = n.calcDiscountPercent %}
                {% set image = n.thumbnailUri %}
                <div>
                    <a href="{{ n.viewLink }}">
                        <picture>
                            <source data-srcset="{{ image }}">
                            <img loading="lazy" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC"
                                 alt="{{ n.name | raw }}"/>
                        </picture>
                    </a>
                    {% if(percent > 0) %}
                        <div>- {{percent }}%</div>
                    {% endif %}
                    <a href="{{ n.viewLink }}">{{ n.name | raw }}</a>
                    <div>
                        {% if p.priceAfterDiscount > 0 %}
                        <p>{{ p.priceAfterDiscount | number_format(0) }}₫
                        <del>{{ p.price | number_format(0) }}₫</del></p>
                        {% elseif (p.oldPrice > 0) %}
                            <p>{{ p.price | number_format(0) }}₫
                            <del>{{ p.oldPrice | number_format(0) }}₫</del></p>
                        {% else %}
                            <span>{{ p.price | number_format(0) }}₫</span>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        </div>
    {% endif %}
{% endraw %}
```

* Tạo nút yêu thích cho sản phẩm

```
<div class="_addWishList" data-id="{{ productId }}">
    <i class="fa-thin fa-heart"></i>
</div>
```

* Lấy thuộc tính của sản phẩm (Sản phẩm ở list sản phẩm chỉ lấy đc thuộc tính màu sắc)

```
{% raw %}
{% set values = n.options.attrValues %}
{% if(values is not empty) %}
    <div>
        {% for v in values %}
        {% set color = v.options.attrContent %}
            <span data-attr="{{ v.thumbnailUri }}">
                <a style="background-color: {{ '#' ~ color }};"
                   data-value="{{ v.name }}"></a>
            </span>
        {% endfor %}
    </div>
{% endif %}
{% endraw %}
```

<figure><img src="../.gitbook/assets/image (28).png" alt=""><figcaption><p>Nút yêu thích và thuộc tính màu sắc của sản phẩm</p></figcaption></figure>

### Banner bộ sưu tập

Là nơi để chuyển hướng nhanh đến bộ sưu tập sản phẩm mà người dùng yêu thích

Dưới đây là cách thức lấy banner bộ sưu tập của website:

```
{% raw %}
{% set albumHome = searchAlbum({'limit': 1}) %}
    {% if(albumHome is not null or albumHome is not empty) %}
        {% for a in albumHome %}
            <section>
                <span>{{ a.name }}</span>
                
                {{ a.description |raw }}
                
                <a href="{{ a.viewLink }}">
                    Link bộ sưu tập
                </a>
                
                <div>
                    <a class="img-link d-block position-relative" href="{{ a.viewLink }}">
                        <img alt="{{ a.name }}" class="lookbook-img" src="{{ a.thumbnailUri }}">
                        <div class="lookbook-img_cover position-absolute">{{ a.name }}</div>
                    </a>
                    {% set albumItems = getAlbumItems(a.id,{'limit': 4}) %}
                    {% if(albumItems is not null or albumItems is not empty) %}
                        {% for b in albumItems %}
                            <a href="{{ a.viewLink }}">
                                <img alt="{{ a.name }}" src="{{ b.imageUri }}">
                                {{ b.description | striptags }}
                            </a>
                        {% endfor %}
                    {% endif %}
                </div>
            </section>
        {% endfor %}
    {% endif %}
{% endraw %}
```

<figure><img src="../.gitbook/assets/image (29).png" alt=""><figcaption><p>Bộ sưu tập</p></figcaption></figure>

### Tin tức

Luôn cập nhật những tin tức mới nhất lên trang web của bạn

Dưới đây là cách thức lấy tin tức của website:

```
{% raw %}
{% set lastestNews= getHotNews({'limit':5}) %}
{% if(lastestNews is not empty) %}
    {% for i in lastestNews %}
        <div>
            <a href="{{ i.viewLink }}">
               <img src="{{ i.imageUri }}" alt="">
            </a>
            <div>
                <a href="{{ i.viewLink }}">{{ i.title }}</a>
                {{ subString(i.intro, 500) }}
                {{ i.createdDateTime }}
            </div>
        </div>
    {% endfor %}
{% endif %}
{% endraw %}
```

<figure><img src="../.gitbook/assets/image (30).png" alt=""><figcaption><p>Tin tức</p></figcaption></figure>
