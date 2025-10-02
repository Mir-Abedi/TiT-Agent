#!/bin/bash

# Server cleanup script for TiT-Agent deployment
# Run this on your server if you're still experiencing disk space issues

echo "Starting server cleanup..."

# Check current disk usage
echo "Current disk usage:"
df -h

# Clean up Docker resources
echo "Cleaning up Docker resources..."
sudo docker system prune -af --volumes
sudo docker builder prune -af
sudo docker image prune -af

# Clean up old logs
echo "Cleaning up old logs..."
sudo journalctl --vacuum-time=7d
sudo find /var/log -name "*.log" -type f -mtime +7 -delete

# Clean up package cache
echo "Cleaning up package cache..."
sudo apt-get clean
sudo apt-get autoremove -y

# Clean up temporary files
echo "Cleaning up temporary files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Check disk usage after cleanup
echo "Disk usage after cleanup:"
df -h

echo "Cleanup completed!"
