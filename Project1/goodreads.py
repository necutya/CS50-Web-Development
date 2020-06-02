import requests


def return_rating_by_isbn(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "RMEeDeJp0vpQPMar9fx0Q", "isbns": isbn}).json()['books'][0]
    return dict(rating_count=res['work_ratings_count'], avg_rating=res['average_rating'])


if __name__ == '__main__':
    return_rating_by_isbn('9781632168146')
