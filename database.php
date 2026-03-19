<?php
// config/database.php - Koneksi Database versi PHP

require_once __DIR__ . '/../includes/functions.php';

function getDbConnection() {
    static $conn = null;
    
    if ($conn === null) {
        $host = getenv('DB_HOST') ?: 'localhost';
        $port = getenv('DB_PORT') ?: '5432';
        $dbname = getenv('DB_NAME') ?: 'horor_forum';
        $user = getenv('DB_USER') ?: 'postgres';
        $pass = getenv('DB_PASS') ?: '';
        
        $connString = "host=$host port=$port dbname=$dbname user=$user password=$pass";
        $conn = pg_connect($connString);
        
        if (!$conn) {
            error_log("Database error: " . pg_last_error());
            return null;
        }
    }
    
    return $conn;
}

// Fungsi query helper
function dbQuery($sql, $params = []) {
    $conn = getDbConnection();
    if (!$conn) return false;
    
    if (empty($params)) {
        return pg_query($conn, $sql);
    } else {
        // Untuk query dengan parameter (prepared statement)
        $result = pg_query_params($conn, $sql, $params);
        return $result;
    }
}

// Fungsi ambil satu baris
function dbFetchOne($result) {
    return $result ? pg_fetch_assoc($result) : null;
}

// Fungsi ambil semua baris
function dbFetchAll($result) {
    $data = [];
    while ($row = pg_fetch_assoc($result)) {
        $data[] = $row;
    }
    return $data;
}
?>