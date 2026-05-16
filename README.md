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

## UML Diagram
```mermaid
classDiagram
    class Settings{
        +String app_name
        +String app_version
        +String host
        +Int port
        +String overpass_url
        +float area_query_budget_seconds
        
        +get_settings() Settings
    }
    class OverpassClient{
        -_settings Settings
        -_http httpx.AsyncClient
        +query_bbox(bbox, filters) list[dict[str, Any]]
        +query_around_point(lat, long, radius_m, filters) list[dict[str, Any]]
        -_execute(query) list[dict[str, Any]]
        -_parse_response(resonse) list[dict[str, Any]]
    }
    class NominatimClient {
        -_settings Settings
        -_http httpx.AsyncClient
        +search(query) list[dict[String, Any]]
        +reverse_geocode(lat, lon, zoom) dict[String, Any]
        -_enforce_limit(limit)
        -_get_headers() dict[String, String]
    }
    class GeocodeService{
        -OverpassService _overpass
        -NominatimService _nominatim
        +features_in_area(bbox, filters) FeatureCollection
        -_validate_bbox(bbox)
    }
    namespace Api {
        class Routes {
            -_parse_filters(raw) dict[String, String]
            +get_features_in_area(service, bbox, filter) FeatureCollection
        }
        class Status {
            +get_status() dict[String, String]
            +get_ready() dict[String, String]
        }
        class Dependencies {
            +get_http_client(request) httpx.AsyncClient
            +get_overpass_client(settings, http_client) OverpassClient
            +get_nominatim_client(settings, http_client) NominatimClient
            +get_geocode_service(overpass, nominatim) GeocodeService
        }
    }
    namespace Utils {
        class Overpass_Query_Builder["Overpass Query Builder (pure functions)"] {
            +build_bbox_query(bbox, filters, timeout_seconds) String
            +build_around_point_query(lat, lon, radius_m, filters, timeout_seconds) String
            -_timeout_clause(budget_seconds) Int
            -_format_filters(filters) String
            -_escape(literal) String
        }
    }
    namespace Models {
        class BoundingBox {
            +min_lat float
            +min_lon float
            +max_lat float
            +max_lon float
        }
        class OSMFeature {
            +id String
            +type String
            +geometry dict[String, Any]
            +properties dict[String, Any]
        }
        class FeatureCollection {
            +type String
            +features list[OSMFeature]
            +metadata dict[String, Any]
        }
    }
    
    GeocodeService --> BoundingBox
    GeocodeService --> FeatureCollection
    GeocodeService --> OverpassClient
    GeocodeService --> NominatimClient
    GeocodeService --> Overpass_Query_Builder
    
    OverpassClient --> Settings
    
    NominatimClient --> Settings
    
    Dependencies ..> OverpassClient
    Dependencies ..> NominatimClient
    Dependencies ..> GeocodeService
    Dependencies ..> Settings
    
    Overpass_Query_Builder --> OSMFeature
    
    Routes --> Dependencies
    Routes --> GeocodeService
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

