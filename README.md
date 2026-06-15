# ◓ PokéAnalytics

A web application for Pokémon analytics — an educational project built as a test target for demonstrating QA automation skills.

---

## ⚠️ Disclaimer

> **This project is created solely for educational and portfolio demonstration purposes.**
>
> - Pokémon and all associated names, images, and trademarks are the property of **Nintendo**, **Creatures Inc.**, **GAME FREAK inc.**, and **The Pokémon Company**.
> - Pokémon data is sourced from the open **[PokéAPI](https://pokeapi.co/)**, distributed under the **BSD 3-Clause License** for non-commercial use.
> - This project is **not a commercial product**. It generates no revenue and is not distributed as end-user software.
> - The primary purpose of this project is to serve as a **system under test** for automated testing, demonstrating the author's QA Engineering skills.
> - The author makes no claims to any intellectual property related to the Pokémon franchise.
> - This project will be promptly removed upon any legitimate request from the rights holders.

---

## 🎯 Purpose

This is **not** a production application. It was built specifically as a testable system to demonstrate the following competencies:

| Area | Technologies |
|------|-------------|
| API Testing | Java, REST Assured, TestNG |
| UI Testing | Playwright |
| Reporting | Allure |
| Test Design | Boundary values, equivalence partitioning, pairwise |
| CI/CD | Docker, Docker Compose |

---

## 🚀 Running locally

```bash
docker compose up --build
```

The frontend is served on **http://localhost** and the API on the `/api/` path
(Swagger UI at **http://localhost/api/docs**).

On first boot the API auto-seeds Gen I (151 Pokémon) into a SQLite database
stored on the `api_data` volume, so data survives restarts. The database is no
longer committed to the repo — it is generated, not source.

### Configuration (environment variables)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:////data/pokeanalytics.db` | SQLAlchemy connection string |
| `CORS_ORIGINS` | `http://localhost,http://localhost:3000` | Comma-separated allowed origins |
| `AUTO_SEED` | `1` | Seed automatically on first boot when the DB is empty |
| `AUTO_SEED_MAX` | `151` | How many Pokémon to auto-seed |
| `SEED_TOKEN` | _(unset)_ | When set, enables `POST /api/admin/seed` (sent via the `X-Seed-Token` header). Disabled when unset |
| `API_WORKERS` | `2` | Gunicorn worker count |

### Backend tests

```bash
cd api
pip install -r requirements-dev.txt
pytest
```