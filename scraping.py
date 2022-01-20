"""
Mengambil 100 top dari data seacrh key tokopedia
"""

from bs4 import BeautifulSoup as bs
import csv
import requests


TOKOPEDIA_API_URL = 'https://gql.tokopedia.com/'


def get_search_result(search_keyword, page=1, max_retries=3):
    
    api_response = ''
    # Kasih query body dan mengarahkan dari tokopedia untuk mendapatkan hasil pencarian
    query_body = [{"operationName":"SearchProductQueryV4","variables":{"params":f"device=desktop&navsource=home&ob=23&page={page}&q={search_keyword}&related=true&rows=60&safe_search=false&scheme=https&shipping=&source=search&st=product&start=0&topads_bucket=true&unique_id=14ed3345ffad7b4017c80de8e7bfda49&user_addressId=&user_cityId=176&user_districtId=2274&user_id=&user_lat=&user_long=&user_postCode=&variants="},"query":"query SearchProductQueryV4($params: String!) {\n  ace_search_product_v4(params: $params) {\n    header {\n      totalData\n      totalDataText\n      processTime\n      responseCode\n      errorMessage\n      additionalParams\n      keywordProcess\n      __typename\n    }\n    data {\n      isQuerySafe\n      ticker {\n        text\n        query\n        typeId\n        __typename\n      }\n      redirection {\n        redirectUrl\n        departmentId\n        __typename\n      }\n      related {\n        relatedKeyword\n        otherRelated {\n          keyword\n          url\n          product {\n            id\n            name\n            price\n            imageUrl\n            rating\n            countReview\n            url\n            priceStr\n            wishlist\n            shop {\n              city\n              isOfficial\n              isPowerBadge\n              __typename\n            }\n            ads {\n              adsId: id\n              productClickUrl\n              productWishlistUrl\n              shopClickUrl\n              productViewUrl\n              __typename\n            }\n            badges {\n              title\n              imageUrl\n              show\n              __typename\n            }\n            ratingAverage\n            labelGroups {\n              position\n              type\n              title\n              url\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      suggestion {\n        currentKeyword\n        suggestion\n        suggestionCount\n        instead\n        insteadCount\n        query\n        text\n        __typename\n      }\n      products {\n        id\n        name\n        ads {\n          adsId: id\n          productClickUrl\n          productWishlistUrl\n          productViewUrl\n          __typename\n        }\n        badges {\n          title\n          imageUrl\n          show\n          __typename\n        }\n        category: departmentId\n        categoryBreadcrumb\n        categoryId\n        categoryName\n        countReview\n        discountPercentage\n        gaKey\n        imageUrl\n        labelGroups {\n          position\n          title\n          type\n          url\n          __typename\n        }\n        originalPrice\n        price\n        priceRange\n        rating\n        ratingAverage\n        shop {\n          shopId: id\n          name\n          url\n          city\n          isOfficial\n          isPowerBadge\n          __typename\n        }\n        url\n        wishlist\n        sourceEngine: source_engine\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}]
    referer = f'https://www.tokopedia.com/search?st=product&q={search_keyword}&navsource=home'

    # Header standar agar dapat melakukan panggilan API yang diizinkan dan dikenali ke tokopedia
    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://www.tokopedia.com',
        'referer': f'{referer}',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }

    # Retry x times
    for _ in range(max_retries):
        try:
            resp = requests.post(TOKOPEDIA_API_URL, headers=headers, json=query_body)
            if resp.ok:
                api_response = resp.json()
                break
            else:
                resp.raise_for_status()
        except Exception as e:
            print(f'Tokopedia api calls failed due to: {e}')

    return api_response


def parse_search_result_data(api_response):
    
    product_list = []
    for resp in api_response:
        product_results = resp.get('data').get('ace_search_product_v4').get('data').get('products') # Standard tokopedia response style
        for product in product_results:
            product_dict = dict(
                product_name=product.get('name'),
                product_image_link=product.get('imageUrl'),
                product_price=product.get('price'),
                product_rating=product.get('rating'),
                product_average_rating=product.get('ratingAverage'),
                product_merchant=product.get('shop').get('name'),
                product_target_url=product.get('url') # Digunakan untuk menjelajah lebih jauh ke halaman produk itu sendiri, untuk mengekstrak deskripsi
            )
            product_list.append(product_dict)

    return product_list


# TODO: cari tahu mengapa panggilan backend untuk posting ke url ini tidak berfungsi, temukan proper yang tepat untuk diteruskan
def get_product_result(product_page_url):
    
    api_response = ''
    # url halaman produk yang diberikan selalu mengikuti pola ini:
    # https://{shop_domain}/{product_key}?whid=0
    splitted_product_page_url = product_page_url.split('/')
    shop_domain = splitted_product_page_url[-2]
    product_key = splitted_product_page_url[-1].split('?')[0]
    query_body = [{"operationName":"PDPGetLayoutQuery","variables":{"shopDomain":f"{shop_domain}","productKey":f"{product_key}","layoutID":"","apiVersion":1,"userLocation":{"addressID":"0","districtID":"2274","postalCode":"","latlon":""}},"query":"fragment ProductVariant on pdpDataProductVariant {\n  errorCode\n  parentID\n  defaultChild\n  sizeChart\n  variants {\n    productVariantID\n    variantID\n    name\n    identifier\n    option {\n      picture {\n        urlOriginal: url\n        urlThumbnail: url100\n        __typename\n      }\n      productVariantOptionID\n      variantUnitValueID\n      value\n      hex\n      __typename\n    }\n    __typename\n  }\n  children {\n    productID\n    price\n    priceFmt\n    optionID\n    productName\n    productURL\n    picture {\n      urlOriginal: url\n      urlThumbnail: url100\n      __typename\n    }\n    stock {\n      stock\n      isBuyable\n      stockWordingHTML\n      minimumOrder\n      maximumOrder\n      __typename\n    }\n    isCOD\n    isWishlist\n    campaignInfo {\n      campaignID\n      campaignType\n      campaignTypeName\n      campaignIdentifier\n      background\n      discountPercentage\n      originalPrice\n      discountPrice\n      stock\n      stockSoldPercentage\n      startDate\n      endDate\n      endDateUnix\n      appLinks\n      isAppsOnly\n      isActive\n      hideGimmick\n      isCheckImei\n      __typename\n    }\n    thematicCampaign {\n      additionalInfo\n      background\n      campaignName\n      icon\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ProductMedia on pdpDataProductMedia {\n  media {\n    type\n    urlThumbnail: URLThumbnail\n    videoUrl: videoURLAndroid\n    prefix\n    suffix\n    description\n    __typename\n  }\n  videos {\n    source\n    url\n    __typename\n  }\n  __typename\n}\n\nfragment ProductHighlight on pdpDataProductContent {\n  name\n  price {\n    value\n    currency\n    __typename\n  }\n  campaign {\n    campaignID\n    campaignType\n    campaignTypeName\n    campaignIdentifier\n    background\n    percentageAmount\n    originalPrice\n    discountedPrice\n    originalStock\n    stock\n    stockSoldPercentage\n    threshold\n    startDate\n    endDate\n    endDateUnix\n    appLinks\n    isAppsOnly\n    isActive\n    hideGimmick\n    __typename\n  }\n  thematicCampaign {\n    additionalInfo\n    background\n    campaignName\n    icon\n    __typename\n  }\n  stock {\n    useStock\n    value\n    stockWording\n    __typename\n  }\n  variant {\n    isVariant\n    parentID\n    __typename\n  }\n  wholesale {\n    minQty\n    price {\n      value\n      currency\n      __typename\n    }\n    __typename\n  }\n  isCashback {\n    percentage\n    __typename\n  }\n  isTradeIn\n  isOS\n  isPowerMerchant\n  isWishlist\n  isCOD\n  isFreeOngkir {\n    isActive\n    __typename\n  }\n  preorder {\n    duration\n    timeUnit\n    isActive\n    preorderInDays\n    __typename\n  }\n  __typename\n}\n\nfragment ProductCustomInfo on pdpDataCustomInfo {\n  icon\n  title\n  isApplink\n  applink\n  separator\n  description\n  __typename\n}\n\nfragment ProductInfo on pdpDataProductInfo {\n  row\n  content {\n    title\n    subtitle\n    applink\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDetail on pdpDataProductDetail {\n  content {\n    title\n    subtitle\n    applink\n    showAtFront\n    isAnnotation\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDataInfo on pdpDataInfo {\n  icon\n  title\n  isApplink\n  applink\n  content {\n    icon\n    text\n    __typename\n  }\n  __typename\n}\n\nfragment ProductSocial on pdpDataSocialProof {\n  row\n  content {\n    icon\n    title\n    subtitle\n    applink\n    type\n    rating\n    __typename\n  }\n  __typename\n}\n\nquery PDPGetLayoutQuery($shopDomain: String, $productKey: String, $layoutID: String, $apiVersion: Float, $userLocation: pdpUserLocation!) {\n  pdpGetLayout(shopDomain: $shopDomain, productKey: $productKey, layoutID: $layoutID, apiVersion: $apiVersion, userLocation: $userLocation) {\n    name\n    pdpSession\n    basicInfo {\n      alias\n      isQA\n      id: productID\n      shopID\n      shopName\n      minOrder\n      maxOrder\n      weight\n      weightUnit\n      condition\n      status\n      url\n      needPrescription\n      catalogID\n      isLeasing\n      isBlacklisted\n      menu {\n        id\n        name\n        url\n        __typename\n      }\n      category {\n        id\n        name\n        title\n        breadcrumbURL\n        isAdult\n        detail {\n          id\n          name\n          breadcrumbURL\n          isAdult\n          __typename\n        }\n        __typename\n      }\n      txStats {\n        transactionSuccess\n        transactionReject\n        countSold\n        paymentVerified\n        itemSoldPaymentVerified\n        __typename\n      }\n      stats {\n        countView\n        countReview\n        countTalk\n        rating\n        __typename\n      }\n      __typename\n    }\n    components {\n      name\n      type\n      position\n      data {\n        ...ProductMedia\n        ...ProductHighlight\n        ...ProductInfo\n        ...ProductDetail\n        ...ProductSocial\n        ...ProductDataInfo\n        ...ProductCustomInfo\n        ...ProductVariant\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}]

    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://www.tokopedia.com',
        'content-length': '5408',
        'referer': f'{product_page_url}',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'x-tkpd-akamai': 'pdpGetLayout'
    }
    resp = requests.post(TOKOPEDIA_API_URL, headers=headers, json=query_body)
    if resp:
        api_response = resp.json()

    return api_response


# TODO: cari tahu mengapa konten permintaan dapatkan ke url taget tidak berfungsi
def get_product_description(product_page_url):
    
    product_description = ''
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    }
    # Masih tidak berfungsi untuk saat ini, poin untuk perbaikan
    # page_content = requests.get(product_page_url, headers=headers, timeout=1).content
    page_content = ''
    if page_content:
        soup = bs(page_content, 'lxml')
        product_description = soup.find('div', {'data-testid': 'lblPDPDescriptionProduk'})

    return product_description


def write_into_csv(product_data, search_keyword):
    
    data_list = []
    for product in product_data:
        data_list.append([
            product.get('product_name'),
            product.get('product_image_link'),
            product.get('product_price'),
            product.get('product_rating'),
            product.get('product_average_rating'),
            product.get('product_description'),
            product.get('product_merchant')
        ])
    file_header = ['Product Name', 'Product Image Link', 'Product Price', 'Product Rating', 'Product Average Rating', 'Product Description', 'Merchant Name']
    
    # i++
    with open(f'Top 100 {search_keyword}.csv', 'w', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(file_header)
        writer.writerows(data_list)


def main(search_keyword):
    
    # Mulailah dengan pencarian halaman pertama
    page = 1
    product_data = []
    # Untuk mendapatkan 100 hasil teratas, kami memeriksa len data yang diurai, jika data tidak mencukupi terus crawling ke halaman berikutnya,
    # Respon default dari Tokopedia adalah 60 produk per halaman
    while len(product_data) < 100:
        # Untuk menghindari infinite loop, buat asumsi untuk melakukan hard stop di halaman 5 apa pun hasilnya
        if page >= 5:
            break
        # Dapatkan tanggapan dari API tokopedia
        search_result = get_search_result(search_keyword, max_retries=1, page=page)
        # Tingkatkan nomor halaman untuk dijelajahi melalui halaman berikutnya
        page += 1
        if search_result:
            parsed_data = parse_search_result_data(search_result)
            product_data.extend(parsed_data)

    # Hanya mendapatkan top 100
    if len(product_data) >= 100:
        product_data = product_data[:100]

    for product in product_data:
        try:
            product_description = get_product_description(product.get('product_target_url'))
        except Exception as e:
            print(f'Failed to get the product description due to: {e}')
            product_description = ''
        product['product_description'] = product_description

    # Ekspor ke bentuk CSV file
    write_into_csv(product_data, search_keyword)

    return product_data


if __name__ == '__main__':
    search_keyword = input('Enter your search keyword: ')
    res = main(search_keyword)