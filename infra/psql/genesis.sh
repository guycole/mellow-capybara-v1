#!/bin/bash
#
# Title:genesis.sh
# Description:
# Development Environment: OS X 12.7.6/postgres 15.8
#
psql -U postgres template1 (or psql -U gsc template1)

# (mac) user
createuser -U gsc -d -e -l -P -r -s slug_admin
woofwoof
createuser -U gsc -e -l -P slug_client
batabat

# (linux) su - postgres
createuser -U postgres -d -e -l -P -r -s capybara_admin
woofwoof
createuser -U postgres -e -l -P capybara_client
batabat

createdb capybara -O capybara_admin -E UTF8 -T template0 -l C

# psql -h localhost -p 5432 -U capybara_admin -d capybara
# psql -h localhost -p 5432 -U capybara_client -d capybara
