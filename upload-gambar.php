<?php
// api/upload-gambar.php - Upload gambar ke ImgBB
header('Content-Type: application/json');
require_once __DIR__ . '/../config.php';

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

if (!isset($_FILES['image'])) {
    echo json_encode(['success' => false, 'error' => 'Tidak ada file']);
    exit;
}

$file = $_FILES['image'];

// Cek error
if ($file['error'] !== UPLOAD_ERR_OK) {
    echo json_encode(['success' => false, 'error' => 'Error upload file']);
    exit;
}

// Cek ukuran (max 5MB)
if ($file['size'] > 5 * 1024 * 1024) {
    echo json_encode(['success' => false, 'error' => 'File terlalu besar (max 5MB)']);
    exit;
}

// Cek tipe file
$allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime = finfo_file($finfo, $file['tmp_name']);
finfo_close($finfo);

if (!in_array($mime, $allowed)) {
    echo json_encode(['success' => false, 'error' => 'Tipe file tidak didukung']);
    exit;
}

// Upload ke ImgBB
$api_key = getenv('IMGBB_API_KEY');
if (!$api_key) {
    echo json_encode(['success' => false, 'error' => 'API Key ImgBB tidak ditemukan']);
    exit;
}

$image_data = base64_encode(file_get_contents($file['tmp_name']));

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'https://api.imgbb.com/1/upload');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, [
    'key' => $api_key,
    'image' => $image_data,
    'name' => pathinfo($file['name'], PATHINFO_FILENAME)
]);

$response = curl_exec($ch);
curl_close($ch);

$data = json_decode($response, true);

if (isset($data['data']['url'])) {
    echo json_encode([
        'success' => true,
        'url' => $data['data']['url'],
        'delete_url' => $data['data']['delete_url'] ?? null
    ]);
} else {
    echo json_encode(['success' => false, 'error' => 'Gagal upload ke ImgBB']);
}
?>