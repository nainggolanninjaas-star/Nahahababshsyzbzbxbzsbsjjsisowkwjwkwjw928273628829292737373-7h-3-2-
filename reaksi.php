<?php
// api/reaksi.php - Menangani reaksi Wow/No
header('Content-Type: application/json');
require_once __DIR__ . '/../config.php';
require_once __DIR__ . '/../includes/functions.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Harus login dulu']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
$post_id = (int)($input['post_id'] ?? 0);
$type = $input['type'] ?? '';

if ($post_id === 0 || !in_array($type, ['wow', 'no'])) {
    echo json_encode(['success' => false, 'error' => 'Data tidak valid']);
    exit;
}

$user_id = (int)$_SESSION['user_id'];

// Cek apakah sudah pernah react
$checkQuery = "SELECT id, type FROM reactions WHERE user_id = $user_id AND post_id = $post_id";
$checkResult = pg_query($conn, $checkQuery);

if (pg_num_rows($checkResult) > 0) {
    // Sudah pernah react
    $existing = pg_fetch_assoc($checkResult);
    
    if ($existing['type'] === $type) {
        // React sama -> hapus (un-react)
        pg_query($conn, "DELETE FROM reactions WHERE id = {$existing['id']}");
        
        // Update counter di posts
        if ($type === 'wow') {
            pg_query($conn, "UPDATE posts SET wow_count = wow_count - 1 WHERE id = $post_id");
        } else {
            pg_query($conn, "UPDATE posts SET no_count = no_count - 1 WHERE id = $post_id");
        }
        
        $added = false;
    } else {
        // React beda -> update
        pg_query($conn, "UPDATE reactions SET type = '$type' WHERE id = {$existing['id']}");
        
        // Update counters
        if ($type === 'wow') {
            pg_query($conn, "UPDATE posts SET wow_count = wow_count + 1, no_count = no_count - 1 WHERE id = $post_id");
        } else {
            pg_query($conn, "UPDATE posts SET no_count = no_count + 1, wow_count = wow_count - 1 WHERE id = $post_id");
        }
        
        $added = true;
    }
} else {
    // Belum pernah react -> insert baru
    pg_query($conn, "INSERT INTO reactions (user_id, post_id, type) VALUES ($user_id, $post_id, '$type')");
    
    // Update counter
    if ($type === 'wow') {
        pg_query($conn, "UPDATE posts SET wow_count = wow_count + 1 WHERE id = $post_id");
    } else {
        pg_query($conn, "UPDATE posts SET no_count = no_count + 1 WHERE id = $post_id");
    }
    
    $added = true;
}

logActivity($conn, $user_id, 'REACTION', ['post_id' => $post_id, 'type' => $type, 'added' => $added]);

echo json_encode([
    'success' => true,
    'added' => $added,
    'type' => $type
]);
?>