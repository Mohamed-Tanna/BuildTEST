#!/bin/bash
template_name='freight-backend-'
template_name+=$1 
gcloud compute instance-groups managed set-instance-template freightmonster-dev-backend-instance-group \
                    --template=$template_name \
                    --zone=us-west1-a

gcloud compute instance-groups managed rolling-action start-update freightmonster-dev-backend-instance-group \
                    --max-unavailable=0\
                    --zone=us-west1-a\
                    --version=template=$template_name