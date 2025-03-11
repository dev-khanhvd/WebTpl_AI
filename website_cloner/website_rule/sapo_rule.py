class SapoRule:
    def __init__(self):
        self.sapo_types = {
            'homepage': {'pattern': r'^/?$', 'found': False},
            'search': {'pattern': r'^/search\?(q|query)=.*$', 'found': False},
            "category": {
                'pattern': r'^/collections/[^/]+$|^/category/[^/]+$',
                'found': False,
                'index_file': True
            },
            'product': {'pattern': r'^/products/[^/]+$|^/product/[^/]+$', 'found': False},
            'order_cart': {'pattern': r'^/cart$|^/gio-hang$', 'found': False},
            'order_checkout': {'pattern': r'^/checkout$|^/thanh-toan$', 'found': False},
            'order_search': {'pattern': r'^/apps/kiem-tra-don-hang$', 'found': False},
            'blog': {
                'pattern': r'^/blogs(/[^/]+)?$|^/tin-tuc$',
                'found': False,
                'index_file': True
            },
            'blog_article': {'pattern': r'^/blogs/[^/]+/[^/]+$|^/tin-tuc/[^/]+$', 'found': False},
            'contact': {'pattern': r'^/lien-he$', 'found': False},
            'user_signin': {'pattern': r'^/account/login$', 'found': False},
            'user_signup': {'pattern': r'^/account/register$', 'found': False},
            'map': {'pattern': r'^/he-thong-cua-hang$', 'found': False},
            'wish_list': {'pattern': r'^/san-pham-yeu-thich$', 'found': False},
            'promotion_index': {'pattern': r'^/flash-sale$', 'found': False},
            'promotion_list': {'pattern': r'^/san-pham-noi-bat$', 'found': False},
            'landing_page': {'pattern': r'^/pages/landing-page$', 'found': False},
        }

    def get_rules(self):
        return self.sapo_types