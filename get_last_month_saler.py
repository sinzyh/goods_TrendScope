from datetime import datetime

def get_last_month_saler(data: list):
    """
    从 SellerSprite 返回的列表结构中，获取【上一个月份】的 sales
    data: [
        {'dk': 'YYYYMM', 'sales': int},
        ...
    ]
    """
    if not data or not isinstance(data, list):
        return None

    # ---------- 1️⃣ 计算上一个月份 ----------
    now = datetime.now()
    year = now.year
    month = now.month

    if month == 1:
        last_year = year - 1
        last_month = 12
    else:
        last_year = year
        last_month = month - 1

    last_month_key = f"{last_year}{last_month:02d}"  # YYYYMM

    # ---------- 2️⃣ 遍历列表查找 ----------
    for item in data:
        if not isinstance(item, dict):
            continue
        if item.get("dk") == last_month_key:
            return item.get("sales")

    return None


if __name__ == '__main__':
    a = {
        "message": "",
        "data": {
            "asin": "B0FKBCX4DN",
            "asinObj": {
                "alias": "B0FKBCX4DN",
                "amazonChoice": "N",
                "asin": "B0FKBCX4DN",
                "asinUrl": "https://www.amazon.com/dp/B0FKBCX4DN?psc=1",
                "availableDate": 1761235200000,
                "bestSeller": "N",
                "brand": "OuMuaMua",
                "brandUrl": "/stores/OuMuaMua/page/9A21C19D-EB6E-4B94-A57F-E34C5D90C519?lp_asin=B0FKBCX4DN&ref_=ast_bln&store_ref=bl_ast_dp_brandLogo_sto",
                "bsrId": "toys-and-games",
                "bsrLabel": "Toys & Games",
                "bsrRank": 25266,
                "categoryId": "toys-and-games",
                "categoryName": "Toys & Games",
                "coupon": "",
                "createdTime": 1761702251000,
                "deliveryPrice": -1.0,
                "diamond": "B0FKBCX4DN",
                "dimensions": "1\"L x 1\"W x 1\"Th",
                "ebc": "N",
                "features": [
                    "Value-Packed Set: You’ll receive 25 christmas paper plates, 25 Christmas Tree napkins, and 25 forks. The Gingerbread plates and napkins offers a variety of styles and ample quantities, saving you the hassle of matching items—the perfect choice for your festive gatherings",
                    "Unique Themed Design: The holiday paper plates and napkins sets feature a variety of classic Christmas elements. The holiday paper plates are designed in a charming gingerbread style, while the napkins showcase elegant Christmas tree silhouettes. Each gingerbread plates and napkins is printed with intricate, festive patterns, bursting with holiday colors to create an immersive seasonal atmosphere",
                    "High Quality Materials: This disposable Christmas set is crafted from premium paper and plastic materials. Our Christmas plates disposable are safe, reliable, and fade-resistant. The Christmas paper plates heavy duty feature a reinforced design with a 350gsm weight—nearly twice as thick as standard plates—making them sturdy, durable, and resistant to warping. The Christmas tree napkins are soft yet thick, tear-resistant, and highly absorbent",
                    "Time-Saving Convenience: These gingerbread paper plates allow for easy cleanup after gatherings—simply toss them after use! Spend less time washing dishes and more time enjoying your celebration. A practical, high-value choice for hassle-free entertaining",
                    "Versatile Use: This set of Christmas dessert plates disposable is perfect for table settings and decorative backdrops at holiday gatherings - whether Christmas parties, birthdays, weddings, winter celebrations, or even baby showers. Beyond practicality, their cheerful designs instantly brighten any gathering with festive color and joy"
                ],
                "firstReviewDate": 1762444800000,
                "guestVisited": False,
                "imageUrl": "https://m.media-amazon.com/images/I/51wmJVBPkNL._AC_US200_.jpg",
                "lqs": 90,
                "monthUnits": 500,
                "monthUnitsUpdatedTime": 1765936325000,
                "newRelease": "N",
                "newReleaseLabel": "#1 New Release  in Kids' Party Plates",
                "newReleaseUrl": "/gp/new-releases/toys-and-games/274333011/ref=zg_b_hnr_274333011_1",
                "nodeId": 274333011,
                "nodeIdPath": "165793011:1266203011:274330011:274333011",
                "nodeLabelPath": "Toys & Games:Party Supplies:Party Tableware:Plates",
                "nonSharedDiamond": "B0FKBCX4DN",
                "overviews": "{\"Material\":\"Paper\",\"Brand\":\"OuMuaMua\",\"Color\":\"Brown Gingerbread Man\",\"Special Feature\":\"Durability\",\"Style\":\"Modern\"}",
                "parent": "B0FLDCMPZS",
                "price": 17.99,
                "primeExclusivePrice": -1.0,
                "rating": 4.0,
                "reviews": 17,
                "sellerId": "A3N9OOZDV4LGW0",
                "sellerName": "There For You",
                "sellerType": "FBA",
                "sellers": 1,
                "sku": [
                    "Color: Brown Gingerbread Man",
                    "Size: 75Pcs"
                ],
                "skuStr": "Color: Brown Gingerbread Man | Size: 75Pcs",
                "station": "GLOBAL",
                "subcategories": [
                    {
                        "code": "274333011",
                        "label": "Kids' Party Plates",
                        "rank": 16
                    }
                ],
                "title": "OuMuaMua Christmas Gingerbread Paper Plates, 75Pcs Gingerbread Christmas Disposable Tableware Set Include Paper Plates Napkins Forks for Xmas Holiday Birthday Party Supplies",
                "updatedTime": 1765950706000,
                "variationList": [
                    {
                        "asin": "B0FKBDLGX2",
                        "attribute": "Color: Dark Brown Gingerbread Man | Size: 100Pcs"
                    },
                    {
                        "asin": "B0FKBH58VW",
                        "attribute": "Color: Khaki Gingerbread House | Size: 150Pcs"
                    },
                    {
                        "asin": "B0FKBCX4DN",
                        "attribute": "Color: Brown Gingerbread Man | Size: 75Pcs"
                    },
                    {
                        "asin": "B0FKBCVJDG",
                        "attribute": "Color: Khaki Gingerbread House | Size: 75Pcs"
                    },
                    {
                        "asin": "B0FKBCVJTF",
                        "attribute": "Color: Khaki Brown Gingerbread House | Size: 177Pcs"
                    },
                    {
                        "asin": "B0FKBGP62P",
                        "attribute": "Color: Brown Gingerbread Man | Size: 150Pcs"
                    }
                ],
                "variations": 6,
                "videoUrl": "N",
                "weight": "12.6 ounces",
                "zoomImageUrl": "https://m.media-amazon.com/images/I/51wmJVBPkNL._AC_US600_.jpg"
            },
            "chartData": {
                "2025-10": {
                    "alias": "B0FKBCX4DN",
                    "amzUnitTrend": "{}",
                    "amzUnitTrends": [],
                    "asin": "B0FKBCX4DN",
                    "availableDate": 1761235200000,
                    "availableDays": 7,
                    "availableMonth": 0,
                    "availableYear": 0,
                    "averagePrice": 13.99,
                    "brand": "OuMuaMua",
                    "brandUrl": "https://www.amazon.com/s?k=OuMuaMua",
                    "bsrId": "toys-and-games",
                    "bsrLabel": "Toys & Games",
                    "bsrRank": 147484,
                    "categoryId": "165793011",
                    "categoryName": "Toys & Games",
                    "channel": "P",
                    "coupon": "",
                    "curMon": False,
                    "deliveryPrice": -1.0,
                    "dimensionType": "LS",
                    "dimensions": "1 x 1 x 1 inches",
                    "ebc": "N",
                    "fba": 5.29,
                    "firstReviewDate": 1761235200000,
                    "guestVisited": False,
                    "id": "USB0FKBCX4DN",
                    "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/71DmS+-PECL._AC_US200_.jpg",
                    "lqs": 70,
                    "marketId": 1,
                    "monDailySales": "",
                    "monthId": 202510,
                    "monthName": "202510",
                    "nodeId": 274333011,
                    "nodeIdPath": "165793011:1266203011:274330011:274333011",
                    "nodeLabelPath": "Toys & Games:Party Supplies:Party Tableware:Plates",
                    "order": {
                        "desc": True,
                        "field": ""
                    },
                    "overviews": "{\"Material\":\"Paper\",\"Brand\":\"OuMuaMua\",\"Color\":\"Brown Gingerbread Man\",\"Special Feature\":\"Durability\",\"Style\":\"Modern\"}",
                    "page": 0,
                    "pages": 0,
                    "parent": "B0FLDCMPZS",
                    "parentChangeHis": [],
                    "pkgDimensionType": "LS",
                    "pkgDimensions": "9.7 x 8.1 x 1.9 inches",
                    "pkgVolumeWeights": 487.14804,
                    "pkgWeight": "0.79 pounds",
                    "price": 13.99,
                    "primeExclusivePrice": -1.0,
                    "profit": 47.19,
                    "salesTrend": "{\"202509\":0,\"202507\":0,\"202508\":0,\"202505\":0,\"202506\":0,\"202503\":0,\"202504\":0,\"202501\":0,\"202502\":0,\"202510\":8,\"202411\":0,\"202412\":0,\"202410\":0}",
                    "sellerId": "A3N9OOZDV4LGW0",
                    "sellerName": "There For You",
                    "sellerNation": "CN",
                    "sellerType": "FBA",
                    "sellers": 1,
                    "sku": "Color: Brown Gingerbread Man | Size: 75Pcs",
                    "station": "GLOBAL",
                    "subcategories": [
                        {
                            "code": "274333011",
                            "label": "Kids' Party Plates",
                            "rank": 1086
                        }
                    ],
                    "symbol": "Y",
                    "syncTime": 1762163951000,
                    "title": "OuMuaMua Christmas Gingerbread Paper Plates, 75Pcs Gingerbread Christmas Disposable Tableware Set Include Paper Plates Napkins Forks for Xmas Holiday Birthday Party Supplies",
                    "took": 0,
                    "total": 0,
                    "totalAmount": 111.92,
                    "totalUnits": 8,
                    "trends": [
                        {
                            "dk": "202410",
                            "sales": 0
                        },
                        {
                            "dk": "202411",
                            "sales": 0
                        },
                        {
                            "dk": "202412",
                            "sales": 0
                        },
                        {
                            "dk": "202501",
                            "sales": 0
                        },
                        {
                            "dk": "202502",
                            "sales": 0
                        },
                        {
                            "dk": "202503",
                            "sales": 0
                        },
                        {
                            "dk": "202504",
                            "sales": 0
                        },
                        {
                            "dk": "202505",
                            "sales": 0
                        },
                        {
                            "dk": "202506",
                            "sales": 0
                        },
                        {
                            "dk": "202507",
                            "sales": 0
                        },
                        {
                            "dk": "202508",
                            "sales": 0
                        },
                        {
                            "dk": "202509",
                            "sales": 0
                        },
                        {
                            "dk": "202510",
                            "sales": 8
                        }
                    ],
                    "updatedTime": 1762166095297,
                    "variations": 3,
                    "video": "N",
                    "weight": "12.6 ounces"
                },
                "2025-11": {
                    "alias": "B0FKBCX4DN",
                    "amzUnit": 300,
                    "amzUnitDate": 1764935527000,
                    "amzUnitTrend": "{}",
                    "amzUnitTrends": [],
                    "asin": "B0FKBCX4DN",
                    "availableDate": 1761798480000,
                    "availableDays": 30,
                    "availableMonth": 0,
                    "availableYear": 0,
                    "averagePrice": 14.49,
                    "brand": "OuMuaMua",
                    "brandUrl": "https://www.amazon.com/s?k=OuMuaMua",
                    "bsrId": "toys-and-games",
                    "bsrLabel": "Toys & Games",
                    "bsrRank": 31177,
                    "bsrRankCr": -24.55,
                    "bsrRankCv": -6145,
                    "categoryId": "165793011",
                    "categoryName": "Toys & Games",
                    "channel": "P",
                    "coupon": "",
                    "curMon": False,
                    "deliveryPrice": -1.0,
                    "dimensionType": "LS",
                    "dimensions": "1 x 1 x 1 inches",
                    "ebc": "N",
                    "fba": 4.84,
                    "firstReviewDate": 1761798480000,
                    "guestVisited": False,
                    "id": "USB0FKBCX4DN",
                    "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/71bueLUP1SL._AC_US200_.jpg",
                    "lqs": 90,
                    "marketId": 1,
                    "monDailySales": "",
                    "monthId": 202511,
                    "monthName": "202511",
                    "newRelease": "#1 New Release  in Kids' Party Plates",
                    "nodeId": 274333011,
                    "nodeIdPath": "165793011:1266203011:274330011:274333011",
                    "nodeLabelPath": "Toys & Games:Party Supplies:Party Tableware:Plates",
                    "order": {
                        "desc": True,
                        "field": ""
                    },
                    "overviews": "{\"Material\":\"Paper\",\"Brand\":\"OuMuaMua\",\"Color\":\"Brown Gingerbread Man\",\"Special Feature\":\"Durability\",\"Style\":\"Modern\"}",
                    "page": 0,
                    "pages": 0,
                    "parent": "B0FLDCMPZS",
                    "parentChangeHis": [],
                    "pkgDimensionType": "LS",
                    "pkgDimensions": "9.7 x 8.1 x 1.7 inches",
                    "pkgVolumeWeights": 435.8693,
                    "pkgWeight": "0.79 pounds",
                    "price": 14.95,
                    "primeExclusivePrice": -1.0,
                    "profit": 59.46,
                    "rating": 4.7,
                    "reviews": 9,
                    "reviewsDelta": 1,
                    "reviewsIncreasement": 8,
                    "reviewsRate": 1.14,
                    "salesTrend": "{\"202509\":0,\"202507\":0,\"202508\":0,\"202505\":0,\"202506\":0,\"202503\":0,\"202504\":0,\"202501\":0,\"202502\":0,\"202510\":8,\"202411\":0,\"202511\":701,\"202412\":0}",
                    "sellerId": "A3N9OOZDV4LGW0",
                    "sellerName": "There For You",
                    "sellerNation": "CN",
                    "sellerType": "FBA",
                    "sellers": 1,
                    "sku": "Color: Brown Gingerbread Man | Size: 75Pcs",
                    "station": "GLOBAL",
                    "subcategories": [
                        {
                            "code": "274333011",
                            "label": "Kids' Party Plates",
                            "rank": 3
                        }
                    ],
                    "symbol": "Y",
                    "syncTime": 1764945577000,
                    "title": "OuMuaMua Christmas Gingerbread Paper Plates, 75Pcs Gingerbread Christmas Disposable Tableware Set Include Paper Plates Napkins Forks for Xmas Holiday Birthday Party Supplies",
                    "took": 0,
                    "total": 0,
                    "totalAmount": 10157.49,
                    "totalAmountGrowth": 4775.0,
                    "totalUnits": 701,
                    "totalUnitsGrowth": 4775.0,
                    "trends": [
                        {
                            "dk": "202411",
                            "sales": 0
                        },
                        {
                            "dk": "202412",
                            "sales": 0
                        },
                        {
                            "dk": "202501",
                            "sales": 0
                        },
                        {
                            "dk": "202502",
                            "sales": 0
                        },
                        {
                            "dk": "202503",
                            "sales": 0
                        },
                        {
                            "dk": "202504",
                            "sales": 0
                        },
                        {
                            "dk": "202505",
                            "sales": 0
                        },
                        {
                            "dk": "202506",
                            "sales": 0
                        },
                        {
                            "dk": "202507",
                            "sales": 0
                        },
                        {
                            "dk": "202508",
                            "sales": 0
                        },
                        {
                            "dk": "202509",
                            "sales": 0
                        },
                        {
                            "dk": "202510",
                            "sales": 8
                        },
                        {
                            "dk": "202511",
                            "sales": 701
                        }
                    ],
                    "updatedTime": 1764953518936,
                    "variations": 6,
                    "video": "N",
                    "weight": "12.6 ounces"
                },
                "2025-12": {
                    "averagePrice": 19.4,
                    "curMon": True,
                    "curMonDaysales": [
                        {
                            "bsr": 29636,
                            "dailySales": 18,
                            "dailySales5MA": 18.0,
                            "dateId": 20251118,
                            "dateStr": "2025/11/18",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 27801,
                            "dailySales": 20,
                            "dailySales5MA": 19.0,
                            "dateId": 20251119,
                            "dateStr": "2025/11/19",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 22180,
                            "dailySales": 22,
                            "dailySales5MA": 20.0,
                            "dateId": 20251120,
                            "dateStr": "2025/11/20",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 23424,
                            "dailySales": 25,
                            "dailySales5MA": 21.25,
                            "dateId": 20251121,
                            "dateStr": "2025/11/21",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 24852,
                            "dailySales": 25,
                            "dailySales5MA": 22.0,
                            "dateId": 20251122,
                            "dateStr": "2025/11/22",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 25032,
                            "dailySales": 21,
                            "dailySales5MA": 22.6,
                            "dateId": 20251123,
                            "dateStr": "2025/11/23",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 29565,
                            "dailySales": 20,
                            "dailySales5MA": 22.6,
                            "dateId": 20251124,
                            "dateStr": "2025/11/24",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 30522,
                            "dailySales": 23,
                            "dailySales5MA": 22.8,
                            "dateId": 20251125,
                            "dateStr": "2025/11/25",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 28593,
                            "dailySales": 23,
                            "dailySales5MA": 22.4,
                            "dateId": 20251126,
                            "dateStr": "2025/11/26",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 26009,
                            "dailySales": 20,
                            "dailySales5MA": 21.4,
                            "dateId": 20251127,
                            "dateStr": "2025/11/27",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 25822,
                            "dailySales": 60,
                            "dailySales5MA": 29.2,
                            "dateId": 20251128,
                            "dateStr": "2025/11/28",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 26381,
                            "dailySales": 26,
                            "dailySales5MA": 30.4,
                            "dateId": 20251129,
                            "dateStr": "2025/11/29",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 30575,
                            "dailySales": 29,
                            "dailySales5MA": 31.6,
                            "dateId": 20251130,
                            "dateStr": "2025/11/30",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 30635,
                            "dailySales": 60,
                            "dailySales5MA": 39.0,
                            "dateId": 20251201,
                            "dateStr": "2025/12/01",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 26495,
                            "dailySales": 29,
                            "dailySales5MA": 40.8,
                            "dateId": 20251202,
                            "dateStr": "2025/12/02",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 22141,
                            "dailySales": 54,
                            "dailySales5MA": 39.6,
                            "dateId": 20251203,
                            "dateStr": "2025/12/03",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 16444,
                            "dailySales": 63,
                            "dailySales5MA": 47.0,
                            "dateId": 20251204,
                            "dateStr": "2025/12/04",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 11837,
                            "dailySales": 71,
                            "dailySales5MA": 55.4,
                            "dateId": 20251205,
                            "dateStr": "2025/12/05",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 12231,
                            "dailySales": 76,
                            "dailySales5MA": 58.6,
                            "dateId": 20251206,
                            "dateStr": "2025/12/06",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 11414,
                            "dailySales": 60,
                            "dailySales5MA": 64.8,
                            "dateId": 20251207,
                            "dateStr": "2025/12/07",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 14604,
                            "dailySales": 69,
                            "dailySales5MA": 67.8,
                            "dateId": 20251208,
                            "dateStr": "2025/12/08",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 14962,
                            "dailySales": 86,
                            "dailySales5MA": 72.4,
                            "dateId": 20251209,
                            "dateStr": "2025/12/09",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 13476,
                            "dailySales": 87,
                            "dailySales5MA": 75.6,
                            "dateId": 20251210,
                            "dateStr": "2025/12/10",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 13094,
                            "dailySales": 69,
                            "dailySales5MA": 74.2,
                            "dateId": 20251211,
                            "dateStr": "2025/12/11",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 14691,
                            "dailySales": 70,
                            "dailySales5MA": 76.2,
                            "dateId": 20251212,
                            "dateStr": "2025/12/12",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 15823,
                            "dailySales": 55,
                            "dailySales5MA": 73.4,
                            "dateId": 20251213,
                            "dateStr": "2025/12/13",
                            "guestVisited": False,
                            "order": {
                                "desc": True,
                                "field": ""
                            },
                            "page": 0,
                            "pages": 0,
                            "took": 0,
                            "total": 0
                        },
                        {
                            "bsr": 17569,
                            "dailySales": 49,
                            "dailySales5MA": 66.0,
                            "dateId": 20251214,
                            "dateStr": "2025/12/14",
                            "guestVisited": False,
                            "order": {
                                "desc": True
                            }
                        }
                    ]

                }
            }
        }
    }
    print(get_last_month_saler(a))