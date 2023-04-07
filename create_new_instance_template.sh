#!/bin/bash
template_name='freight-backend-'
template_name+=$1
gcloud compute instance-templates create $template_name \
    --network=freightslayer-staging-network \
    --subnet=freightslayer-staging-network \
    --region=us-west1\
    --metadata commit-SHA=$1\
    --metadata-from-file  startup-script='vm_startup_script.sh'\
    --image 'ubuntu-2204-jammy-v20221206'\
    --image-project=ubuntu-os-cloud\
    --shielded-secure-boot\
    --shielded-integrity-monitoring\
    --shielded-vtpm\
    --boot-disk-type=pd-standard\
    --boot-disk-size=20\
    --service-account=freightslayer-staging-backend@freightslayer-staging.iam.gserviceaccount.com\
    --scopes=cloud-platform\
    --no-address