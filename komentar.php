<?php
// api/komentar.php - Menangani komentar
header('Content-Type: application/json');
require_once __DIR__ . '/../config.php';
require_once __DIR__ . '/../includes/functions.php';

// ===== GET KOMENTAR =====
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $post_id = (int)($_GET['post_id'] ?? 0);
    
    if ($post_id === 0) {
        echo json_encode(['success' => false, 'error' => 'ID post tidak valid']);
        exit;
    }
    
    $query = "SELECT c.*, u.name as author_name, u.avatar 
              FROM comments c
              JOIN users u ON c.user_id = u.id
              WHERE c.post_id = $post_id
              ORDER BY c.created_at ASC";
    
    $result = pg_query($conn, $query);
    $comments = [];
    
    while ($row = pg_fetch_assoc($result)) {
        $comments[] = $row;
    }
    
    echo json_encode(['success' => true, 'comments' => $comments]);
    exit;
}

// ===== POST KOMENTAR =====
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_SESSION['user_id'])) {
        http_response_code(401);
        echo json_encode(['success' => false, 'error' => 'Harus login dulu']);
        exit;
    }
    
    $input = json_decode(file_get_contents('php://input'), true);
    $post_id = (int)($input['post_id'] ?? 0);
    $content = trim($input['content'] ?? '');
    
    if ($post_id === 0 || empty($content)) {
        echo json_encode(['success' => false, 'error' => 'Data tidak valid']);
        exit;
    }
    
    if (strlen($content) > 500) {
        echo json_encode(['success' => false, 'error' => 'Komentar maksimal 500 karakter']);
        exit;
    }
    
    $user_id = (int)$_SESSION['user_id'];
    $content = pg_escape_string($conn, $content);
    
    $query = "INSERT INTO comments (post_id, user_id, content) 
              VALUES ($post_id, $user_id, '$content') RETURNING id";
    
    $result = pg_query($conn, $query);
    
    if ($result) {
        // Update comment count di posts
        pg_query($conn, "UPDATE posts SET comment_count = comment_count + 1 WHERE id = $post_id");
        
        $row = pg_fetch_assoc($result);
        logActivity($conn, $user_id, 'COMMENT', ['post_id' => $post_id, 'comment_id' => $row['id']]);
        
        echo json_encode(['success' => true, 'comment_id' => $row['id']]);
    } else {
        echo json_encode(['success' => false, 'error' => 'Gagal menambah komentar']);
    }
    exit;
}

http_response_code(405);
echo json_encode(['success' => false, 'error' => 'Method not allowed']);
?>