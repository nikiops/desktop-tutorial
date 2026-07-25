# Ozon Review Service — Marketplace Review Automation

A full-stack service for collecting, analyzing and processing marketplace product reviews. The current implementation is located in `zakaz/ozon-review-service/`.

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
- **Data:** relational persistence for reviews and product statistics
- **Integrations:** Ozon API, AI response service, Yandex-related integration modules
- **Frontend:** browser-based management interface
- **Infrastructure:** Docker Compose, deployment and verification scripts

## Implemented capabilities

- Synchronization of product reviews from Ozon
- Review list with pagination, sorting and answered/unanswered filtering
- Review statistics: total reviews, unanswered count, average rating and product coverage
- Per-product review aggregation
- Local persistence and processing of newly fetched reviews
- API validation and error handling for external integrations
- Service settings and integration endpoints
- Deployment and environment verification scripts for Windows/Linux

## Main project

```text
zakaz/ozon-review-service/
├── app/
│   ├── api/routes/
│   ├── models/
│   ├── schemas/
│   └── services/
├── frontend/
├── docker-compose.yml
├── DEPLOYMENT.md
└── README.md
```

## API example

The backend exposes review-oriented endpoints such as:

- `GET /api/reviews`
- `GET /api/reviews/stats`
- `GET /api/reviews/products`
- `GET /api/reviews/unanswered/list`
- `POST /api/reviews/sync`

## Security

API credentials are expected through runtime configuration. Real marketplace/API secrets should never be committed to the repository.

## Status

Portfolio / freelance automation project focused on marketplace operations and review processing.
