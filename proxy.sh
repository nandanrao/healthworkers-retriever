#!/bin/sh

echo "Starting SSH Tunnel"
ssh-keyscan -H $ORANGE_SSH_PEER_IP >> ~/.ssh/known_hosts
echo "$ORANGE_RSA" | base64 --decode > ~/.ssh/orange_rsa
chmod 400 ~/.ssh/orange_rsa
ssh -tt -i ~/.ssh/orange_rsa -L 0.0.0.0:3306:$ORANGE_DB_IP:3306 -N $ORANGE_SSH_USER@$ORANGE_SSH_PEER_IP
