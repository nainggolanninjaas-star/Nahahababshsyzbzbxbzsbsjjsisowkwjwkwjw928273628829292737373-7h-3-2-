<?php
// ============================================
// FUNCTIONS.PHP - VERSI SEDERHANA (PASTI JALAN)
// ============================================

// ===== CEK LOGIN =====
function isLoggedIn() {
    return isset($_SESSION['user_id']);
}

function requireLogin() {
    if (!isLoggedIn()) {
        header('Location: /login.php');
        exit;
    }
}

// ===== AMBIL USER =====
function getCurrentUser($conn) {
    if (!isset($_SESSION['user_id'])) return null;
    $id = (int)$_SESSION['user_id'];
    $result = pg_query($conn, "SELECT * FROM users WHERE id = $id");
    return $result ? pg_fetch_assoc($result) : null;
}

// ===== FORMAT WAKTU =====
function timeAgo($datetime) {
    $time = strtotime($datetime);
    $diff = time() - $time;
    
    if ($diff < 60) return $diff . ' detik lalu';
    if ($diff < 3600) return floor($diff/60) . ' menit lalu';
    if ($diff < 86400) return floor($diff/3600) . ' jam lalu';
    return floor($diff/86400) . ' hari lalu';
}

// ===== AMBIL POSTINGAN =====
function getLatestPosts($conn, $limit = 10) {
    $result = pg_query($conn, "SELECT p.*, u.name as author_name 
                                FROM posts p 
                                JOIN users u ON p.user_id = u.id 
                                ORDER BY p.created_at DESC 
                                LIMIT $limit");
    $posts = [];
    while ($row = pg_fetch_assoc($result)) {
        $posts[] = $row;
    }
    return $posts;
}

// ===== SANITASI INPUT =====
function sanitize($data) {
    return htmlspecialchars(trim($data), ENT_QUOTES, 'UTF-8');
}
?>