#!/bin/sh

set -e

envsubst < /etc/nginx/default.congf.tpl > /etc/nginx/conf.d/default.congf
nginx -g 'daemon off;'