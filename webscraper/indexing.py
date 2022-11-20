url = 'https://www.lazada.com.ph/products/cod-solar-power-bank-50000mah-original-fast-charging-brand-universal' \
      '-portable-buy-1-take-4-freebies-with-led-flashlight-hot-sales-high-capacity-high-quality-digital-display-pd' \
      '-lithium-polymer-bank-charge-carry-around-iphone-black-i2748827349-s13190101338.html '

url2 = 'https://shopee.ph/HUILISHI-Korean-small-stand-up-collar-summer-cotton-plain-color-T-shirt-fashion-casual-mens' \
       '-tops-i.64151604.21813358711 '

end = url.find('.html')

# print(end)

g = url[:end].split('-')  # shop
h = url[:end].split('-')  # item
print(g[-1].strip(g[-1][0]))
print(h[-2].strip(g[-2][0]))
