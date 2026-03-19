<?php
// api/lapor.php - Melaporkan cerita tidak pantas
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
$reason = trim($input['reason'] ?? '');

if ($post_id === 0 || empty($reason)) {
    echo json_encode(['success' => false, 'error' => 'Data tidak valid']);
    exit;
}

$user_id = (int)$_SESSION['user_id'];
$reason = pg_escape_string($conn, $reason);

// Cek apakah sudah pernah lapor post ini
$checkQuery = "SELECT id FROM reports WHERE reporter_id = $user_id AND post_id = $post_id";
$checkResult = pg_query($conn, $checkQuery);

if (pg_num_rows($checkResult) > 0) {
    echo json_encode(['success' => false, 'error' => 'Anda sudah melaporkan cerita ini']);
    exit;
}

// Simpan laporan
$query = "INSERT INTO reports (reporter_id, post_id, reason, status) 
          VALUES ($user_id, $post_id, '$reason', 'pending')";

if (pg_query($conn, $query)) {
    logActivity($conn, $user_id, 'REPORT', ['post_id' => $post_id, 'reason' => $reason]);
    
    // Notifikasi ke admin (bisa via email/telegram nanti)
    
    echo json_encode(['success' => true, 'message' => 'Laporan terkirim']);
} else {
    echo json_encode(['success' => false, 'error' => 'Gagal mengirim laporan']);
}
?>