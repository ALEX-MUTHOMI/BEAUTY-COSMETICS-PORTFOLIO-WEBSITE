@echo off
setlocal
if not exist tests\postman\reports mkdir tests\postman\reports
newman.cmd run tests\postman\beauty_backend_acceptance.postman_collection.json -e tests\postman\local-docker.postman_environment.json --bail --reporters cli,json --reporter-json-export tests\postman\reports\newman-local.json
