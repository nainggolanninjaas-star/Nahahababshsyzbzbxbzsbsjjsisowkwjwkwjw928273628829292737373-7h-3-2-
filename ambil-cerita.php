<?php
// api/ambil-cerita.php - Mengambil daftar cerita atau detail cerita
header('Content-Type: application/json');
require_once __DIR__ . '/../config.php';
require_once __DIR__ . '/../includes/functions.php';

$id = isset($_GET['id']) ? (int)$_GET['id'] : 0;
$page = isset($_GET['page']) ? (int)$_GET['page'] : 1;
$filter = isset($_GET['filter']) ? pg_escape_string($conn, $_GET['filter']) : 'all';
$limit = 10;
$offset = ($page - 1) * $limit;

// ===== AMBIL SATU CERITA (DETAIL) =====
if ($id > 0) {
    // Update views
    pg_query($conn, "UPDATE posts SET views = views + 1 WHERE id = $id");
    
    // Ambil detail post
    $query = "SELECT p.*, u.name as author_name, u.avatar as author_avatar, u.rgn as author_rgn
              FROM posts p
              JOIN users u ON p.user_id = u.id
              WHERE p.id = $id";
    
    $result = pg_query($conn, $query);
    
    if (!$result || pg_num_rows($result) == 0) {
        http_response_code(404);
        echo json_encode(['success' => false, 'error' => 'Cerita tidak ditemukan']);
        exit;
    }
    
    $post = pg_fetch_assoc($result);
    
    // Ambil gambar-gambar post
    $imgResult = pg_query($conn, "SELECT image_url FROM post_images WHERE post_id = $id");
    $images = [];
    while ($row = pg_fetch_assoc($imgResult)) {
        $images[] = $row['image_url'];
    }
    $post['images'] = $images;
    
    echo json_encode(['success' => true, 'post' => $post]);
    exit;
}

// ===== AMBIL DAFTAR CERITA =====
$where = "1=1";
if ($filter !== 'all') {
    $where .= " AND category = '$filter'";
}

// Hitung total
$countQuery = "SELECT COUNT(*) as total FROM posts WHERE $where";
$countResult = pg_query($conn, $countQuery);
$totalRow = pg_fetch_assoc($countResult);
$totalPosts = $totalRow['total'];
$totalPages = ceil($totalPosts / $limit);

// Ambil data
$query = "SELECT p.*, u.name as author_name, u.rgn as author_rgn,
          (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count
          FROM posts p
          JOIN users u ON p.user_id = u.id
          WHERE $where
          ORDER BY p.created_at DESC
          LIMIT $limit OFFSET $offset";

$result = pg_query($conn, $query);
$posts = [];

while ($row = pg_fetch_assoc($result)) {
    $posts[] = $row;
}

echo json_encode([
    'success' => true,
    'posts' => $posts,
    'total' => $totalPosts,
    'page' => $page,
    'totalPages' => $totalPages
]);
?>