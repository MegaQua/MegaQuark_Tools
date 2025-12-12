import tweepy

# 认证信息
consumer_key = "4JadBpXcdV8jTkCxFOkNrpu6S"
consumer_secret = "FaYzceGIfLfUl3lgaSwX3hPGgn0nYjZuwBO0NqONLRhgmu5pT9"
#bearer_token = "AAAAAAAAAAAAAAAAAAAAAG8erQEAAAAArwSNXhm55EcptUwTIk0P5FlAxZo%3DECCMJtsFv2M7ijYucpHSIaoF0d9FYlZeoGOPknQxc7w9zo2ctK"
access_token = "3187609711-38h8l4eUi5l8qYnx55KIPCW8xMCXo6Kugm57Cql"
access_token_secret = "ATWAMRD1MftiyQOJImGJ7xgPsjFlzVW1EV2fvyQuyQD43"

# 创建认证对象
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret, access_token, access_token_secret
)

# 创建 API 对象
api = tweepy.API(auth)

# 获取特定用户的最新推文
username = "ArknightsStaff"
count = 1  # 要获取的推文数量

# 获取推文
tweets = api.user_timeline(screen_name=username, count=count, tweet_mode='extended')

# 打印推文内容
for tweet in tweets:
    print(tweet.full_text)
