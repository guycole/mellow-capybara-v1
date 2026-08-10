#!/bin/bash
#
# Title:drop_schema.sh
# Description: remove schema
# Development Environment: OS X 10.15.2/postgres 12.12
# Author: G.S. Cole (guy at shastrax dot com)
#
export PGDATABASE=capybara
export PGHOST=localhost
export PGPASSWORD=woofwoof
export PGUSER=capybara_admin
#
psql $PGDATABASE -c "drop table if exists capybara_daily_score"
psql $PGDATABASE -c "drop table if exists capybara_load_log"
psql $PGDATABASE -c "drop table if exists capybara_geo_loc"
#
