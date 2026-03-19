<?php
// ============================================
// CONFIG.PHP - VERSI BARU (LANGSUNG JALAN)
// ============================================

// Matikan error display di production
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Mulai session
if (session_status() == PHP_SESSION_NONE) {
    session_start();
}

// ===== BACA FILE .ENV MANUAL (TANPA FUNGSI) =====
$envFile = __DIR__ . '/.env';
if (file_exists($envFile)) {
    $lines = file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos(trim($line), '#') === 0) continue;
        $parts = explode('=', $line, 2);
        if (count($parts) == 2) {
            putenv(trim($parts[0]) . '=' . trim($parts[1]));
        }
    }
}

// ===== KONEKSI DATABASE LANGSUNG =====
$db_host = getenv('DB_HOST') ?: 'localhost';
$db_port = getenv('DB_PORT') ?: '5432';
$db_name = getenv('DB_NAME') ?: 'horor_forum';
$db_user = getenv('DB_USER') ?: 'postgres';
$db_pass = getenv('DB_PASS') ?: '';

$conn_string = "host=$db_host port=$db_port dbname=$db_name user=$db_user password=$db_pass";
$conn = pg_connect($conn_string);

if (!$conn) {
    error_log("Database error: " . pg_last_error());
    die("❌ Gagal konek database. Cek .env dan koneksi.");
}

// ===== SET TIMEZONE =====
date_default_timezone_set('Asia/Jakarta');
?>