#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SERVICE_NAME=$(basename $SCRIPT_DIR)

echo
echo "Installing $SERVICE_NAME..."

# set permissions for script files
echo "Setting permissions..."
chmod 755 $SCRIPT_DIR/*.py
chmod 755 $SCRIPT_DIR/*.sh
chmod 755 $SCRIPT_DIR/service/run
chmod 755 $SCRIPT_DIR/service/log/run

# create sym-link to run script in daemon
if [ ! -L /service/$SERVICE_NAME ]; then
    echo "Creating service..."
    ln -s $SCRIPT_DIR/service /service/$SERVICE_NAME
else
    echo "Service already exists."
fi

# add install-script to rc.local to be ready for firmware update
filename=/data/rc.local
if [ ! -f $filename ]
then
    touch $filename
    chmod 755 $filename
    echo "#!/bin/bash" >> $filename
    echo >> $filename
fi

# if not already added, then add to rc.local
grep -qxF "bash /data/etc/shelly-emulator/install.sh" $filename || echo "bash /data/etc/shelly-emulator/install.sh" >> $filename

echo
echo "Installation complete!"
echo
echo "Service status:"
svstat /service/$SERVICE_NAME
echo
echo "To view logs:"
echo "  tail -f /var/log/$SERVICE_NAME/current | tai64nlocal"
echo
echo "To restart service:"
echo "  bash $SCRIPT_DIR/restart.sh"
echo
echo "To uninstall:"
echo "  bash $SCRIPT_DIR/uninstall.sh"
echo
