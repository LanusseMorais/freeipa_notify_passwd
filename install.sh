#!/bin/bash
mkdir /opt/freeipa_notify_passwd/ 
pip install -r conf/requirements.txt 
cp conf/freeipa_notify.py  conf/ipa_config.ini /opt/freeipa_notify_passwd/
cp freeipa_notify /etc/cron.daily/ 
