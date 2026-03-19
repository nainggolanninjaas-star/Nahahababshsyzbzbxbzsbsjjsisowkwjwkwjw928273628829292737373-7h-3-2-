<?php
// api-login.php
require_once 'config.php';

$data = json_decode(file_get_contents('php://input'), true);
$user = $data['user'];

$google_id = mysqli_real_escape_string($conn, $user['id']);
$name = mysqli_real_escape_string($conn, $user['name']);
$email = mysqli_real_escape_string($conn, $user['email']);
$avatar = mysqli_real_escape_string($conn, $user['picture']);

// Cek user sudah ada atau belum
$result = mysqli_query($conn, "SELECT * FROM users WHERE google_id = '$google_id' OR email = '$email'");

if (mysqli_num_rows($result) == 0) {
    // User baru
    $rgn = 'HOROR-' . date('Y') . '-' . str_pad(rand(1, 9999), 4, '0', STR_PAD_LEFT);
    mysqli_query($conn, "INSERT INTO users (google_id, name, email, avatar, rgn) 
                         VALUES ('$google_id', '$name', '$email', '$avatar', '$rgn')");
    $user_id = mysqli_insert_id($conn);
} else {
    $row = mysqli_fetch_assoc($result);
    $user_id = $row['id'];
    $rgn = $row['rgn'];
}

// Set session
$_SESSION['user_id'] = $user_id;
$_SESSION['user_name'] = $name;
$_SESSION['user_rgn'] = $rgn;

echo json_encode(['success' => true, 'rgn' => $rgn]);
?>