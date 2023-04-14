#!/bin/bash
template_name='freight-backend-'
template_name+=$1
gcloud compute instance-templates create $template_name \
    --network=freightmonster-dev-network \
    --subnet=freightmonster-dev-network \
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
    --service-account=freightmonster-dev-backend@freightmonster-dev.iam.gserviceaccount.com\
    --scopes=cloud-platform\
    --no-address