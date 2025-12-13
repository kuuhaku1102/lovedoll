<?php
/**
 * Flush Rewrite Rules Script
 * 
 * This script should be run once to flush WordPress rewrite rules.
 * Access this file via browser: https://freya-era.com/wp-content/themes/lovedoll/flush-rewrite-rules.php
 * Then delete this file for security.
 */

// Load WordPress
require_once('../../../wp-load.php');

// Flush rewrite rules
flush_rewrite_rules(true);

echo "Rewrite rules flushed successfully!<br>";
echo "Please delete this file (flush-rewrite-rules.php) for security.<br>";
echo "<a href='" . home_url() . "'>Go to Home</a>";
