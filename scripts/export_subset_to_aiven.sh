#!/usr/bin/env bash
#
# One-time admin/ETL script — NOT part of the deployed app.
#
# Exports a trimmed, referentially-consistent subset of the local yelp_db
# (2 cities: Metairie, Sparks) and loads it into the Aiven MySQL service
# used for the public Streamlit deploy. See Technical Design.md Section 1
# for why this exists: Streamlit Community Cloud can't reach localhost,
# and the full DB is way past Aiven's free-tier 1GB cap.
#
# Cut down from an original 5-city plan (Boise, Clearwater, Saint
# Petersburg, Sparks, Metairie) after real-world disk usage on Aiven's
# free tier came in far higher than the raw-review-text estimate
# suggested — likely InnoDB per-row/per-index overhead (review alone
# carries 4 indexes besides its primary key), not just text bytes.
#
# How the referential consistency works: every table except `category`
# is filtered down to rows connected to the 5 chosen cities, chaining
# through business_id / user_id, so no table ends up with a foreign key
# pointing at a row that doesn't exist in the trimmed set.
#
# Usage: from the repo root, with .env and .env.aiven both filled in:
#   chmod +x scripts/export_subset_to_aiven.sh
#   ./scripts/export_subset_to_aiven.sh

set -e  # stop immediately on any error, don't half-load the target DB

# --- load local DB creds (.env) and Aiven creds (.env.aiven) ---
set -a
source .env
source .env.aiven
set +a

CITIES="'Sparks','Metairie'"
BIZ_SUBQUERY="(SELECT business_id FROM business WHERE city IN ($CITIES))"
USER_SUBQUERY="(SELECT user_id FROM review WHERE business_id IN $BIZ_SUBQUERY UNION SELECT user_id FROM tip WHERE business_id IN $BIZ_SUBQUERY)"

OUT_DIR="subset_export"
mkdir -p "$OUT_DIR"

LOCAL_ARGS=(-h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" --single-transaction --no-tablespaces --set-gtid-purged=OFF --max_allowed_packet=4M)
AIVEN_ARGS=(-h "$AIVEN_DB_HOST" -P "$AIVEN_DB_PORT" -u "$AIVEN_DB_USER" -p"$AIVEN_DB_PASSWORD" --ssl-mode=REQUIRED --ssl-ca="$AIVEN_SSL_CA_PATH" --max_allowed_packet=4M)

echo "[1/4] Dumping table structure only (no rows) for all 9 tables..."
mysqldump "${LOCAL_ARGS[@]}" --no-data "$DB_NAME" \
  business business_hours business_category category checkin review tip user_elite_year yelp_user \
  > "$OUT_DIR/01_schema.sql"

echo "[2/4] Dumping trimmed data, table by table..."

mysqldump "${LOCAL_ARGS[@]}" --no-create-info --where="city IN ($CITIES)" \
  "$DB_NAME" business > "$OUT_DIR/02_business.sql"

mysqldump "${LOCAL_ARGS[@]}" --no-create-info \
  "$DB_NAME" category > "$OUT_DIR/03_category.sql"

mysqldump "${LOCAL_ARGS[@]}" --no-create-info --where="user_id IN $USER_SUBQUERY" \
  "$DB_NAME" yelp_user > "$OUT_DIR/04_yelp_user.sql"

mysqldump "${LOCAL_ARGS[@]}" --no-create-info --where="business_id IN $BIZ_SUBQUERY" \
  "$DB_NAME" business_hours > "$OUT_DIR/05_business_hours.sql"

mysqldump "${LOCAL_ARGS[@]}" --no-create-info --where="business_id IN $BIZ_SUBQUERY" \
  "$DB_NAME" business_category > "$OUT_DIR/06_business_category.sql"

mysqldump "${LOCAL_ARGS[@]}" --no-create-info --where="user_id IN $USER_SUBQUERY" \
  "$DB_NAME" user_elite_year > "$OUT_DIR/07_user_elite_year.sql"

mysqldump "${LOCAL_ARGS[@]}" --no-create-info --where="business_id IN $BIZ_SUBQUERY" \
  "$DB_NAME" review > "$OUT_DIR/08_review.sql"

mysqldump "${LOCAL_ARGS[@]}" --no-create-info --where="business_id IN $BIZ_SUBQUERY" \
  "$DB_NAME" tip > "$OUT_DIR/09_tip.sql"

mysqldump "${LOCAL_ARGS[@]}" --no-create-info --where="business_id IN $BIZ_SUBQUERY" \
  "$DB_NAME" checkin > "$OUT_DIR/10_checkin.sql"

echo "[3/4] Creating tables on Aiven, then loading data in FK-safe order..."

mysql "${AIVEN_ARGS[@]}" "$AIVEN_DB_NAME" < "$OUT_DIR/01_schema.sql"

{
  echo "SET FOREIGN_KEY_CHECKS=0;"
  cat "$OUT_DIR/03_category.sql"
  cat "$OUT_DIR/02_business.sql"
  cat "$OUT_DIR/04_yelp_user.sql"
  cat "$OUT_DIR/05_business_hours.sql"
  cat "$OUT_DIR/06_business_category.sql"
  cat "$OUT_DIR/07_user_elite_year.sql"
  cat "$OUT_DIR/08_review.sql"
  cat "$OUT_DIR/09_tip.sql"
  cat "$OUT_DIR/10_checkin.sql"
  echo "SET FOREIGN_KEY_CHECKS=1;"
} > "$OUT_DIR/11_all_data.sql"

mysql "${AIVEN_ARGS[@]}" "$AIVEN_DB_NAME" < "$OUT_DIR/11_all_data.sql"

echo "[4/4] Done. Row counts on Aiven:"
mysql "${AIVEN_ARGS[@]}" "$AIVEN_DB_NAME" -e "
  SELECT 'business' AS tbl, COUNT(*) AS row_count FROM business
  UNION ALL SELECT 'business_hours', COUNT(*) FROM business_hours
  UNION ALL SELECT 'business_category', COUNT(*) FROM business_category
  UNION ALL SELECT 'category', COUNT(*) FROM category
  UNION ALL SELECT 'yelp_user', COUNT(*) FROM yelp_user
  UNION ALL SELECT 'user_elite_year', COUNT(*) FROM user_elite_year
  UNION ALL SELECT 'review', COUNT(*) FROM review
  UNION ALL SELECT 'tip', COUNT(*) FROM tip
  UNION ALL SELECT 'checkin', COUNT(*) FROM checkin;
"
