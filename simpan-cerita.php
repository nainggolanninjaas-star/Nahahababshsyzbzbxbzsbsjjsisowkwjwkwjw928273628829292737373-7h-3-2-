<?php
// api/simpan-cerita.php - Menyimpan cerita baru
header('Content-Type: application/json');
require_once __DIR__ . '/../config.php';
require_once __DIR__ . '/../includes/functions.php';

// Cek method
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Cek login
if (!isset($_SESSION['user_id'])) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Harus login dulu']);
    exit;
}

// Ambil data JSON
$input = json_decode(file_get_contents('php://input'), true);

if (!$input) {
    echo json_encode(['success' => false, 'error' => 'Data tidak valid']);
    exit;
}

// Validasi input
$title = trim($input['title'] ?? '');
$category = trim($input['category'] ?? '');
$content = trim($input['content'] ?? '');
$trigger = trim($input['trigger'] ?? '');
$user_id = (int)$_SESSION['user_id'];

if (empty($title) || empty($category) || empty($content)) {
    echo json_encode(['success' => false, 'error' => 'Judul, kategori, dan cerita harus diisi']);
    exit;
}

if (strlen($content) < 100) {
    echo json_encode(['success' => false, 'error' => 'Cerita minimal 100 karakter']);
    exit;
}

// Escape string untuk keamanan
$title = pg_escape_string($conn, $title);
$category = pg_escape_string($conn, $category);
$content = pg_escape_string($conn, $content);
$trigger = pg_escape_string($conn, $trigger);

// Simpan ke database
$query = "INSERT INTO posts (user_id, title, category, content, trigger_warning, created_at) 
          VALUES ($user_id, '$title', '$category', '$content', '$trigger', NOW()) RETURNING id";

$result = pg_query($conn, $query);

if ($result) {
    $row = pg_fetch_assoc($result);
    
    // Catat log
    logActivity($conn, $user_id, 'CREATE_POST', ['post_id' => $row['id']]);
    
    echo json_encode([
        'success' => true,
        'post_id' => $row['id'],
        'message' => 'Cerita berhasil dipublikasikan!'
    ]);
} else {
    echo json_encode([
        'success' => false,
        'error' => 'Gagal menyimpan cerita: ' . pg_last_error($conn)
    ]);
}
?>