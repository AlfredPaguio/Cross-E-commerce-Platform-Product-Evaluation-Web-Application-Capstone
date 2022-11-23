load_review_link = 'https://shopee.ph/Palmolive-Men-Anti-Dandruff-Scalp-Cooling-Shampoo-170ml-Pack-of-2-i.45237836' \
                   '.2274295796 '

start = load_review_link.find('-i.')
split_ = load_review_link[start:].strip(' ').split('.')

print(split_)