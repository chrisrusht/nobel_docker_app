**Nobel Prize API**
=====================

**Introduction**
---------------

This API provides access to Nobel Prize data, allowing you to search for laureates by name, category, and description.

**Endpoints**
-------------

### Search by First Name

* **URL**: `/search/firstname=<firstname>`
* **Method**: GET
* **Description**: Search for laureates by first name.
* **Example**: `/search/firstname=marie`

### Search by Surname

* **URL**: `/search/surname=<surname>`
* **Method**: GET
* **Description**: Search for laureates by surname.
* **Example**: `/search/surname=curie`

### Search by First Name and Surname

* **URL**: `/search/firstname=<firstname>&surname=<surname>`
* **Method**: GET
* **Description**: Search for laureates by both first name and surname.
* **Example**: `/search/firstname=marie&surname=curie`

### Search by Category

* **URL**: `/search/category=<category>`
* **Method**: GET
* **Description**: Search for laureates by category (e.g. Physics, Chemistry, etc.).
* **Example**: `/search/category=physics`

### Search by Description

* **URL**: `/search/description=<description>`
* **Method**: GET
* **Description**: Search for laureates by description (motivation).
* **Example**: `/search/description=discovery`

**Response Format**
-------------------

All endpoints return a JSON response containing a list of matching laureates.

**Example Response**
--------------------

```json
[
  {
    "firstname": "Marie",
    "surname": "Curie",
    "category": "Physics",
    "motivation": "Discovery of the elements polonium and radium"
  },
  {
    "firstname": "Pierre",
    "surname": "Curie",
    "category": "Physics",
    "motivation": "Discovery of the elements polonium and radium"
  }
]
```

**Notes**
-------

* The API uses fuzzy search, so you can expect some variation in the results.
* The `description` endpoint searches the motivation field, which may not always contain a full description of the laureate's work.