# Phase 2 Final Fix Plan (M1–M14)

This fix plan addresses the gaps identified in the Final Production Readiness Audit. Implementing these fixes is required to reach a true `GO` state for production deployment.

## P0: Deployment Blockers

### 1. Alembic Migration Consistency
**Issue:** `alembic check` detects uncommitted schema drift (`remove_table sample_items`, `remove_index ix_sample_items_id`).
**Fix:**
- Generate an automigration to capture the removal of `sample_items`.
- Run: `alembic revision --autogenerate -m "drop_sample_items"`
- Upgrade the database to the new head.

## P1: Runtime Safety & API Consistency

### 2. Organization Tier API Compatibility
**Issue:** Mypy flags `Organization has no attribute "tier"` in `src/api/v1/billing.py:62`.
**Fix:**
- Review the `Organization` ORM model.
- If `tier` is a dynamic property based on the active `SubscriptionPlan`, add an `@property` to the `Organization` model, or fetch the tier from the `BillingRepository` and inject it into the Pydantic schema explicitly before returning the response.

### 3. Redis Lua Script Typing Errors
**Issue:** Mypy flags `evalsha` in `src/modules/billing/entitlement_service.py` as having incompatible argument types (expected `str`, got `int`).
**Fix:**
- Explicitly cast the arguments passed to `redis.evalsha` (the rate limit thresholds and usage increments) to `str`. Redis Lua script parameters over RESP must be serialized as strings.

## P2: Code Hygiene & Code Quality

### 4. Mypy Type Annotations
**Issue:** 21 typing errors detected (e.g., missing return types in tests, undefined `Any` in `organization_service.py`).
**Fix:**
- Import `Any` from `typing` in `organization_service.py`.
- Add `-> None` return type annotations to `test_tutor.py` functions.
- Specify type arguments for dictionaries (`dict[str, Any]`) in `tutor_service.py`.
- Import `AsyncSession` correctly in `ai/service.py` and `tutor/tutor.py`.

### 5. Ruff & Black Formatting
**Issue:** 149 Ruff linting errors (mostly missing docstrings `D102`, `D103`, and equality checks `== True`) and 18 files needing Black formatting.
**Fix:**
- Run `black src tests`.
- Run `ruff check --fix src tests` to automatically resolve import issues and `== True` comparisons to `is True` or boolean truthy evaluation.
- Add minimal public docstrings to the newly added repository methods and API routes.

---
**Verdict:** Do not proceed to Phase 3 or production deployment until P0 and P1 fixes are fully verified.
