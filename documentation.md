## API Documentation

### Get Articles List API

```plaintext
/articles/list
```

Method: GET

Description:

This API retrieves a list of active articles, including the user's rating for each article. Each article in the response will contain the article's title, content, and the user's rating.

Sample Response:

```json
{
    "links": {
        "next": null,
        "previous": null
    },
    "count": 2,
    "total_pages": 1,
    "results": [
        {
            "uuid": "525843e8-acea-4a56-a2c6-49fc6312e351",
            "title": "test article",
            "rating_count": 0,
            "average_rating": 0.0,
            "user_rating": 4
        },
        {
            "uuid": "a032e80f-bf58-45d4-9cc9-fd3c7599db3e",
            "title": "article 2",
            "rating_count": 0,
            "average_rating": 0.0,
            "user_rating": null
        }
    ]
}
```

### Rate Article API

```plaintext
/articles/rate_article/<str:article_uuid>/
```

Method: POST

Description:

This API allows users to rate an article by providing a rate from 0 to 5. If a user has already rated the article, their rating will be updated.

Request Body:

```json
{
    "rate": 4
}
```

Sample Response:

```json
{
    "message": "Rating recorded successfully"
}
```

and if user already rate:
```json
{
    "message": "Rating updated successfully"
}
```

### Spam detection

The `update_article_rating` task runs every hour to update the average rate and rating count for each article. This task calculates the new average rate by including only the non-spam ratings and updates the `average_rating` and `rating_count` for each article in bulk. The task also ensures that the rating count is updated properly by considering new ratings that have been created after the last update.


The `detect_spam_rates` method detects spammy ratings based on the user's rating behavior. It analyzes ratings for each article in time slices and compares them to the overall average rating. If the rating in a particular time slice significantly deviates from the overall average, the ratings in that slice are marked as spam.
