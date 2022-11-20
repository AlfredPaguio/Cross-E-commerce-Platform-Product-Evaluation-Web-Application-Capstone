from textblob import TextBlob


def do_sentiment(soup_comment):
    analysis = TextBlob(soup_comment)

    if analysis.sentiment.polarity > 0:  # Positive Sentiment
        return 1
    elif analysis.sentiment.polarity == 0:  # Nuertal Sentiment
        return 0
    else:  # Negative Sentiment
        return -1
