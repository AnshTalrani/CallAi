#!/bin/bash
# Connect to FreePBX container and update AMI credentials
docker exec freepbx bash -c "
  # Backup current manager.conf
  cp /etc/asterisk/manager.conf /etc/asterisk/manager.conf.bak
  
  # Set new credentials (admin/admin for testing)
  NEW_PASS='admin123'
  
  # Update manager.conf with new credentials
  sed -i "s/^secret = .*/secret = $NEW_PASS/" /etc/asterisk/manager.conf
  
  # Reload AMI
  asterisk -rx "module reload manager"
  
  echo "AMI credentials updated:"
  echo "Username: admin"
  echo "Password: $NEW_PASS"
"
