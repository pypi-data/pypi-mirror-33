#!/bin/bash
crontab -l 2> _old.cron
echo '#!/bin/bash' > _mirror.sh

cat <<EOF >> _mirror.sh
cd $PWD
source $VIRTUAL_ENV/bin/activate
`which fluidmirror` -c $PWD/mirror.cfg sync
EOF

chmod +x _mirror.sh
echo "*/5 * * * * $PWD/_mirror.sh" > _new.cron

cat _old.cron _new.cron | crontab -
rm _old.crom _new.cron
