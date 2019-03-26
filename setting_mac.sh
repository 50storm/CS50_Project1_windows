#!/bin/bash

echo "--settiing for--flask development [application.py]---"
export FLASK_APP=application.py
export FLASK_DEBUG=1
#export FLASK_DEBUG=0
export DATABASE_URL=postgres://clbljlcvobhpyp:56202fd3f8b91471a55b86a150995293b195305c2a2cbf5ec0fc1e0314e1022c@ec2-107-22-221-60.compute-1.amazonaws.com:5432/ddrle3028kagbu
#export DATABASE_URL=postgres://hiroshi:Tera54hiro@localhost/bookreview

echo "---printenv---"
echo "environemt valus that flask requires"
printenv FLASK_APP
printenv FLASK_DEBUG
printenv DATABASE_URL

flask run
echo "---setttin ends---"

exit 0
