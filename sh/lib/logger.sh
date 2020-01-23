#!/bin/bash

DATETIME_FORMAT=$(date "+%Y-%m-%dT%H:%M:%S%z")

set_datetime() {
  echo -n "$DATETIME_FORMAT [debug]: "
  "$@"
 return $?
}
logger() {
  echo $(set_datetime "$@")
}