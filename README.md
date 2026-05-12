# microgeo
Local microservice that wraps the public Overpass API (OSM data) and Nominatim (geocoding) behind a small REST API. Other local applications consume it over HTTP.

## Project Structure
```
microgeo/
├── app/
│   ├── main.py       # app factory, lifespan, exception handlers
│   ├── api/          # /v1 endpoints (area, point, search)
│   ├── services/     # Ochestration, async Overpass, async Nominatim
│   ├── models/       # request/response models
│   └── core/         # Settings via env / .env file, app logics
├── tests/
├── pyproject.toml
└── .env
```

## Public API

| User Story             | Method | Path               | Purpose                                      |
|------------------------|--------|--------------------|----------------------------------------------|
| 1. Specify an Area     | GET    | /v1/features/area  | OSM features inside a bounding box           |
| 2. Select a Location   | GET    | /v1/features/point | OSM features at a specific lat/lon           |
| 3. Search for Location | GET    | /v1/search         | Forward-geocode a name, address, or category |
|                        | GET    | /v1/status         | Returns status of the service                |

OSM tag filters are pass as repeated `filter=key=value` query parameters:
```http request
GET /v1/features/area?min_lat=34.0&min_lon=-117.2&max_lat=34.1&max_lon=-117.1&filter=amenity=cafe
GET /v1/features/point?lat=34.0556&lon=-117.1825&filter=amenity=restaurant
GET /v1/search?q=Oregon+State+University&limit=5
```


## Git Workflow

#### Sync main before branching
1. `git checkout main`
2. `git pull --rebase origin main`

#### Create branch
1. `git checkout -b feature/task`

#### Write Code/Commit locally
1. `git add .`
2. `git commit -m "message"`

#### To squash a small commit into a bigger one
1. `git rebase -i HEAD~n`

#### Update branch before pushing
1. `git fetch origin` (or git pull)
2. `git rebase origin/main`

#### Push for PR
1. `git push -u origin feature/task`

