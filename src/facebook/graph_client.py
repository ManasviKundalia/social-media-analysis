import pyfacebook

long_token = open('/home/manasvi/fb_token.txt', 'r').read()
# short_token = open('/home/manasvi/fb_token_short.txt', 'r').read()
api = pyfacebook.Api(app_secret='aae43affe48e3ac8869aec49d63408a9', long_term_token=long_token)
# print(api.get_token_info())
print(api.get_page_info(page_id='357390507677620'))